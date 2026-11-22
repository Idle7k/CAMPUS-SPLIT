import secrets
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.payment import Payment, PaymentAllocation
from app.models.expense import Expense, ExpenseShare
from app.models.ledger import LedgerEntry
from app.models.vendor import Vendor
from app.models.user import User


VALID_PAYMENT_STATUSES = [
    "pending",
    "initiated",
    "reported_paid",
    "confirmed_demo",
    "failed",
    "cancelled",
]


def get_allocated_amount_for_share(db: Session, share_id: int) -> int:
    """
    Returns the sum of confirmed or reported payment allocations for an expense share in paise.
    Only allocations tied to confirmed/reported payments reduce the unpaid liability.
    """
    total = (
        db.query(func.coalesce(func.sum(PaymentAllocation.allocated_amount), 0))
        .join(Payment, PaymentAllocation.payment_id == Payment.id)
        .filter(
            PaymentAllocation.expense_share_id == share_id,
            Payment.status.in_(["confirmed_demo", "reported_paid"]),
        )
        .scalar()
    )
    return total or 0


def get_unpaid_vendor_liability_for_share(db: Session, share: ExpenseShare) -> int:
    """Returns the outstanding unpaid vendor liability for an expense share in paise."""
    allocated = get_allocated_amount_for_share(db, share.id)
    return max(0, share.amount - allocated)


def get_user_vendor_due_paise(db: Session, user_id: int) -> int:
    """
    Calculates total unpaid vendor liability for user_id across all expenses.
    Only confirmed payments reduce outstanding vendor liabilities.
    """
    shares = db.query(ExpenseShare).filter(
        ExpenseShare.user_id == user_id,
        ExpenseShare.status != "paid"
    ).all()

    total = 0
    for s in shares:
        total += get_unpaid_vendor_liability_for_share(db, s)
    return total


def create_payment_attempt(
    db: Session,
    payer_id: int,
    vendor_id: int,
    amount_paise: int,
    expense_id: Optional[int] = None,
    method: str = "upi",
    reference_id: Optional[str] = None,
    allocations_data: Optional[List[Dict[str, int]]] = None,
) -> Payment:
    """
    Initiates a new payment in 'pending' or 'initiated' state.
    Allocations data format: [{'share_id': int, 'amount_paise': int}].
    Validates:
    - Amount > 0.
    - Payer and Vendor exist and Vendor is active.
    - Sum of allocation amounts equals payment amount (if allocations provided).
    - Allocations do not exceed remaining unpaid amount of shares.
    """
    if amount_paise <= 0:
        raise ValueError("Payment amount must be greater than zero")

    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor or not vendor.is_active:
        raise ValueError("Vendor does not exist or is inactive")

    payer = db.query(User).filter(User.id == payer_id).first()
    if not payer:
        raise ValueError("Payer does not exist")

    ref = reference_id or f"PAY-{secrets.token_hex(8).upper()}"

    # Check reference uniqueness
    if db.query(Payment).filter(Payment.reference_id == ref).first():
        raise ValueError(f"Payment with reference '{ref}' already exists")

    # Validate allocations if provided
    if allocations_data:
        total_allocated = sum(a["amount_paise"] for a in allocations_data)
        if total_allocated != amount_paise:
            raise ValueError(
                f"Sum of allocations ({total_allocated}) does not match payment amount ({amount_paise})"
            )

        for a in allocations_data:
            share = db.query(ExpenseShare).filter(ExpenseShare.id == a["share_id"]).first()
            if not share:
                raise ValueError(f"ExpenseShare with id {a['share_id']} does not exist")
            unpaid = get_unpaid_vendor_liability_for_share(db, share)
            if a["amount_paise"] > unpaid:
                raise ValueError(
                    f"Allocated amount {a['amount_paise']} exceeds remaining unpaid share of {unpaid}"
                )

    try:
        payment = Payment(
            payer_id=payer_id,
            vendor_id=vendor_id,
            expense_id=expense_id,
            amount=amount_paise,
            method=method,
            status="pending",
            reference_id=ref,
        )
        db.add(payment)
        db.flush()

        if allocations_data:
            for a in allocations_data:
                alloc = PaymentAllocation(
                    payment_id=payment.id,
                    expense_share_id=a["share_id"],
                    allocated_amount=a["amount_paise"],
                )
                db.add(alloc)

        db.commit()
        db.refresh(payment)
        return payment
    except Exception:
        db.rollback()
        raise


def record_payment_status(
    db: Session,
    payment_id: int,
    status: str,
    metadata_note: Optional[str] = None,
) -> Payment:
    """
    Updates payment status (e.g., 'initiated', 'reported_paid', 'failed', 'cancelled').
    Note: To confirm a payment and apply financial ledger effects, use `confirm_payment`.
    """
    if status not in VALID_PAYMENT_STATUSES:
        raise ValueError(f"Invalid payment status: {status}")

    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise ValueError(f"Payment {payment_id} not found")

    payment.status = status
    if metadata_note:
        existing = payment.confirmation_metadata or ""
        payment.confirmation_metadata = f"{existing}\n{metadata_note}".strip()

    db.commit()
    db.refresh(payment)
    return payment


def confirm_payment(
    db: Session,
    payment_id: int,
    confirmation_method: str = "simulated_demo",
) -> Payment:
    """
    Atomically confirms a payment and applies financial ledger effects.
    
    Financial semantics (Rules 6.2 & 6.3):
    1. Idempotency: If payment is already 'confirmed_demo', return cleanly without re-applying allocations or ledger entries.
    2. Only confirmed payments reduce outstanding vendor liabilities.
    3. Update each covered ExpenseShare: if fully covered, set status='paid'; if partially covered, status='partially_paid'.
    4. Peer Debt: If payer covers another participant's share (payer != share.user_id),
       generate a peer LedgerEntry (debtor = share.user_id, creditor = payer).
    5. Direct-to-Vendor: If participant pays their OWN share (payer == share.user_id),
       NEVER create a peer debt.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise ValueError(f"Payment with id {payment_id} not found")

    # Idempotency protection: do not duplicate effects if already confirmed
    if payment.status == "confirmed_demo":
        return payment

    if payment.status in ["failed", "cancelled"]:
        raise ValueError(f"Cannot confirm payment that is already {payment.status}")

    try:
        payment.status = "confirmed_demo"
        meta_note = f"Confirmed via {confirmation_method}"
        if payment.confirmation_metadata:
            payment.confirmation_metadata += f" | {meta_note}"
        else:
            payment.confirmation_metadata = meta_note

        # Process allocations
        for alloc in payment.allocations:
            share = alloc.expense_share
            total_allocated = get_allocated_amount_for_share(db, share.id)
            
            # Update share status
            if total_allocated >= share.amount:
                share.status = "paid"
            elif total_allocated > 0:
                share.status = "partially_paid"

            # Check if expense is fully paid
            if share.expense and all(s.status == "paid" for s in share.expense.shares):
                share.expense.status = "settled"

            # Peer debt logic (Rule 6.3)
            # Debtor = share.user_id
            # Creditor = payment.payer_id
            if payment.payer_id != share.user_id:
                # Check for existing ledger entry to guarantee idempotency
                existing_debt = db.query(LedgerEntry).filter(
                    LedgerEntry.payment_allocation_id == alloc.id
                ).first()

                if not existing_debt:
                    debt = LedgerEntry(
                        debtor_id=share.user_id,
                        creditor_id=payment.payer_id,
                        amount=alloc.allocated_amount,
                        expense_id=share.expense_id,
                        payment_allocation_id=alloc.id,
                        status="outstanding",
                        notes=f"Share for '{share.expense.description if share.expense else 'Expense'}' covered by {payment.payer.username}",
                    )
                    db.add(debt)

        db.commit()
        db.refresh(payment)
        return payment
    except Exception:
        db.rollback()
        raise
