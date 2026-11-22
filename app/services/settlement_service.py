from typing import Optional
from sqlalchemy.orm import Session

from app.models.settlement import Settlement
from app.models.ledger import LedgerEntry
from app.models.user import User
from app.services.ledger_service import get_outstanding_amount_for_entry


def record_settlement(
    db: Session,
    payer_id: int,
    recipient_id: int,
    amount_paise: int,
    ledger_entry_id: Optional[int] = None,
    notes: Optional[str] = None,
    status: str = "confirmed_demo",
) -> Settlement:
    """
    Records a full or partial peer repayment against an outstanding peer debt.

    Financial semantics (Rules 6.4 & 6.5):
    - A settlement is a repayment of a peer debt, not a vendor payment.
    - Amount must be strictly positive integer paise.
    - Payer and Recipient must exist and be distinct users.
    - If linked to a specific ledger_entry_id:
        - Ledger entry must exist.
        - Payer must match ledger_entry.debtor_id.
        - Recipient must match ledger_entry.creditor_id.
        - Settlement amount must NOT exceed the remaining outstanding amount of that ledger entry.
    - Updates ledger entry status:
        - 'settled' if remaining outstanding reaches 0.
        - 'partially_settled' if outstanding > 0.
    - Atomic database transaction.
    - Preserves history; never alters original expense, share, or vendor payment.
    """
    if amount_paise <= 0:
        raise ValueError("Settlement amount must be greater than zero")

    if payer_id == recipient_id:
        raise ValueError("Payer and recipient cannot be the same user")

    payer = db.query(User).filter(User.id == payer_id).first()
    if not payer:
        raise ValueError("Payer does not exist")

    recipient = db.query(User).filter(User.id == recipient_id).first()
    if not recipient:
        raise ValueError("Recipient does not exist")

    ledger_entry: Optional[LedgerEntry] = None
    if ledger_entry_id:
        ledger_entry = db.query(LedgerEntry).filter(LedgerEntry.id == ledger_entry_id).first()
        if not ledger_entry:
            raise ValueError(f"Ledger entry with id {ledger_entry_id} does not exist")

        if ledger_entry.debtor_id != payer_id:
            raise ValueError("Payer does not match the debtor on this ledger entry")

        if ledger_entry.creditor_id != recipient_id:
            raise ValueError("Recipient does not match the creditor on this ledger entry")

        outstanding = get_outstanding_amount_for_entry(db, ledger_entry)
        if amount_paise > outstanding:
            raise ValueError(
                f"Settlement amount ({amount_paise} paise) exceeds outstanding debt ({outstanding} paise)"
            )

    try:
        settlement = Settlement(
            payer_id=payer_id,
            recipient_id=recipient_id,
            ledger_entry_id=ledger_entry_id,
            amount=amount_paise,
            status=status,
            notes=notes,
        )
        db.add(settlement)
        db.flush()

        if ledger_entry:
            # Recompute remaining outstanding with this settlement included
            new_outstanding = get_outstanding_amount_for_entry(db, ledger_entry)
            if new_outstanding == 0:
                ledger_entry.status = "settled"
            else:
                ledger_entry.status = "partially_settled"

        db.commit()
        db.refresh(settlement)
        return settlement
    except Exception:
        db.rollback()
        raise
