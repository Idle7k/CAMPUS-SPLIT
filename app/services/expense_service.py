from typing import List, Dict, Any, Optional
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.expense import Expense, ExpenseShare
from app.models.vendor import Vendor
from app.models.user import User
from app.models.group import Group, GroupMember
from app.models.payment import Payment, PaymentAllocation
from app.models.ledger import LedgerEntry


def rupees_to_paise(amount_rupees: Any) -> int:
    """
    Converts rupees (int, float, str, Decimal) to integer paise strictly without float inaccuracy.
    Example: 210 -> 21000, 70.50 -> 7050.
    """
    if isinstance(amount_rupees, int):
        return amount_rupees * 100
    try:
        d = Decimal(str(amount_rupees).strip())
        paise = (d * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return int(paise)
    except (InvalidOperation, ValueError, TypeError) as e:
        raise ValueError(f"Invalid monetary value: {amount_rupees}") from e


def calculate_equal_split(total_paise: int, num_participants: int) -> List[int]:
    """
    Calculates equal shares in integer paise.
    Handles remainders deterministically: distributes 1 extra paisa to the first remainder participants
    so that sum(shares) == total_paise exactly.
    """
    if num_participants <= 0:
        raise ValueError("Number of participants must be greater than zero")
    if total_paise <= 0:
        raise ValueError("Total amount must be greater than zero")

    base_share = total_paise // num_participants
    remainder = total_paise % num_participants

    shares = [base_share + 1 if i < remainder else base_share for i in range(num_participants)]
    return shares


def calculate_percentage_split(total_paise: int, percentages: List[Decimal]) -> List[int]:
    """
    Calculates custom percentage splits.
    Percentages must sum to exactly 100%.
    Deterministic remainder allocation is applied to reconcile any rounding differences to total_paise.
    """
    if not percentages:
        raise ValueError("Percentages list cannot be empty")
    
    total_percent = sum(percentages)
    if abs(total_percent - Decimal("100")) > Decimal("0.001"):
        raise ValueError(f"Percentages must sum to exactly 100%, got {total_percent}%")

    raw_shares = []
    for p in percentages:
        if p < Decimal("0"):
            raise ValueError("Percentages cannot be negative")
        raw_paise = (Decimal(total_paise) * p / Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        raw_shares.append(int(raw_paise))

    # Adjust rounding discrepancy to match total_paise exactly
    diff = total_paise - sum(raw_shares)
    if diff != 0:
        # adjust the first participant's share with the remainder
        raw_shares[0] += diff

    return raw_shares


def calculate_custom_split(total_paise: int, custom_shares_paise: List[int]) -> List[int]:
    """
    Validates custom amount split.
    Sum of custom shares must equal total_paise exactly.
    """
    if not custom_shares_paise:
        raise ValueError("Custom shares cannot be empty")
    
    for s in custom_shares_paise:
        if s <= 0:
            raise ValueError("Each participant share must be greater than zero")

    if sum(custom_shares_paise) != total_paise:
        raise ValueError(
            f"Sum of custom shares ({sum(custom_shares_paise)} paise) does not match total amount ({total_paise} paise)"
        )
    return custom_shares_paise


def create_expense(
    db: Session,
    creator_id: int,
    vendor_id: int,
    description: str,
    total_amount_paise: int,
    split_type: str,
    participant_data: List[Dict[str, Any]],
    group_id: Optional[int] = None,
) -> Expense:
    """
    Creates an expense transactionally with shares and payment arrangements.
    participant_data is a list of dicts:
    [
        {
            "user_id": int,
            "amount_paise": int,
            "payment_route": "vendor" | "covered" | "already_paid",
            "covered_by_id": Optional[int]  # Required if payment_route is "covered"
        }
    ]

    Invariants:
    1. Vendor must exist and be active.
    2. Creator and participants must exist.
    3. No duplicate participants.
    4. sum(amount_paise) == total_amount_paise exactly.
    5. Peer debt is created ONLY when a payment actually covers another person's share
       (or in this phase when marked as covered by another participant with a recorded payment).
       An expense share alone NEVER creates a peer debt.
    """
    clean_desc = description.strip()
    if not clean_desc:
        raise ValueError("Expense description cannot be empty")
    if total_amount_paise <= 0:
        raise ValueError("Total amount must be greater than zero")

    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise ValueError("Vendor does not exist")
    if not vendor.is_active:
        raise ValueError("Selected vendor is inactive")

    creator = db.query(User).filter(User.id == creator_id).first()
    if not creator:
        raise ValueError("Creator does not exist")

    if group_id:
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise ValueError("Group does not exist")

    if not participant_data:
        raise ValueError("At least one participant is required")

    # Check unique participants
    participant_ids = [p["user_id"] for p in participant_data]
    if len(participant_ids) != len(set(participant_ids)):
        raise ValueError("Duplicate participants are not allowed in an expense")

    # Validate all participants exist
    users = db.query(User).filter(User.id.in_(participant_ids)).all()
    if len(users) != len(participant_ids):
        raise ValueError("One or more selected participants do not exist")

    # Validate total matches
    shares_sum = sum(p["amount_paise"] for p in participant_data)
    if shares_sum != total_amount_paise:
        raise ValueError(
            f"Sum of shares ({shares_sum} paise) does not equal expense total ({total_amount_paise} paise)"
        )

    # Begin atomic creation
    try:
        expense = Expense(
            creator_id=creator_id,
            vendor_id=vendor_id,
            group_id=group_id,
            description=clean_desc,
            total_amount=total_amount_paise,
            split_type=split_type,
            status="active",
        )
        db.add(expense)
        db.flush()  # generates expense.id

        created_shares = []
        for p in participant_data:
            user_id = p["user_id"]
            share_paise = p["amount_paise"]
            route = p.get("payment_route", "vendor")  # "vendor", "covered", "already_paid"

            if share_paise <= 0:
                raise ValueError("Share amount must be greater than zero")

            # Determine share status based on payment route
            # "vendor": Unpaid share payable to vendor
            # "already_paid": Direct payment made to vendor by participant
            # "covered": Another participant covered this share -> creates Payment + PaymentAllocation + LedgerEntry
            share_status = "unpaid"
            if route == "already_paid":
                share_status = "paid"
            elif route == "covered":
                share_status = "paid"

            share = ExpenseShare(
                expense_id=expense.id,
                user_id=user_id,
                amount=share_paise,
                status=share_status,
            )
            db.add(share)
            db.flush()
            created_shares.append((share, p))

        # Handle payments and peer debts resulting from coverage or direct payments
        for share, p in created_shares:
            route = p.get("payment_route", "vendor")

            if route == "already_paid":
                # Participant paid their own share directly to vendor
                # Note: NO peer debt created when participant pays vendor for own share
                payment = Payment(
                    payer_id=share.user_id,
                    vendor_id=vendor_id,
                    expense_id=expense.id,
                    amount=share.amount,
                    method="upi",
                    status="reported_paid",
                    reference_id=f"EXP-{expense.id}-SHARE-{share.id}-OWN",
                    confirmation_metadata="Participant reported direct vendor payment at creation",
                )
                db.add(payment)
                db.flush()

                allocation = PaymentAllocation(
                    payment_id=payment.id,
                    expense_share_id=share.id,
                    allocated_amount=share.amount,
                )
                db.add(allocation)
                db.flush()

            elif route == "covered":
                # One participant pays vendor and covers this student's share.
                # Must specify covered_by_id (defaults to expense creator if unspecified)
                covered_by_id = p.get("covered_by_id") or creator_id
                if covered_by_id == share.user_id:
                    raise ValueError("A participant cannot cover their own share as a peer debt")

                # Verify coverer exists
                coverer = db.query(User).filter(User.id == covered_by_id).first()
                if not coverer:
                    raise ValueError(f"Covering user with id {covered_by_id} does not exist")

                # Record payment made by coverer to the vendor
                payment = Payment(
                    payer_id=covered_by_id,
                    vendor_id=vendor_id,
                    expense_id=expense.id,
                    amount=share.amount,
                    method="upi",
                    status="reported_paid",
                    reference_id=f"EXP-{expense.id}-SHARE-{share.id}-COV-{covered_by_id}",
                    confirmation_metadata=f"Covered by user {covered_by_id} for user {share.user_id}",
                )
                db.add(payment)
                db.flush()

                allocation = PaymentAllocation(
                    payment_id=payment.id,
                    expense_share_id=share.id,
                    allocated_amount=share.amount,
                )
                db.add(allocation)
                db.flush()

                # Rule 6.3: "If one student pays for another student's share,
                # record the covered amount as a peer debt from the share owner to the person who paid."
                # Debtor = share.user_id (person whose share was covered)
                # Creditor = covered_by_id (person who paid)
                ledger_entry = LedgerEntry(
                    debtor_id=share.user_id,
                    creditor_id=covered_by_id,
                    amount=share.amount,
                    expense_id=expense.id,
                    payment_allocation_id=allocation.id,
                    status="outstanding",
                    notes=f"Share for '{clean_desc}' covered by {coverer.username}",
                )
                db.add(ledger_entry)
                db.flush()

            elif route == "vendor":
                # Direct vendor payment due: no payment or ledger entry created yet.
                pass
            else:
                raise ValueError(f"Unknown payment route: {route}")

        # Update expense status if all shares are paid
        if all(s.status == "paid" for s, _ in created_shares):
            expense.status = "settled"

        db.commit()
        db.refresh(expense)
        return expense
    except Exception:
        db.rollback()
        raise


def get_expense_by_id(db: Session, expense_id: int) -> Optional[Expense]:
    """Retrieve expense with relationships loaded."""
    return db.query(Expense).filter(Expense.id == expense_id).first()
