from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.ledger import LedgerEntry
from app.models.settlement import Settlement
from app.models.user import User


def get_ledger_entry_by_id(db: Session, entry_id: int) -> Optional[LedgerEntry]:
    """Retrieve a ledger entry by ID."""
    return db.query(LedgerEntry).filter(LedgerEntry.id == entry_id).first()


def get_settled_amount_for_entry(db: Session, entry_id: int) -> int:
    """Calculate the total amount settled against a specific ledger entry in paise."""
    total = db.query(func.coalesce(func.sum(Settlement.amount), 0)).filter(
        Settlement.ledger_entry_id == entry_id,
        Settlement.status.in_(["confirmed_demo", "reported"])
    ).scalar()
    return total or 0


def get_outstanding_amount_for_entry(db: Session, entry: LedgerEntry) -> int:
    """Calculate remaining unsettled amount of a ledger entry in paise."""
    settled = get_settled_amount_for_entry(db, entry.id)
    remaining = entry.amount - settled
    return max(0, remaining)


def get_peer_receivable_paise(db: Session, user_id: int) -> int:
    """
    Calculate total amount owed TO user_id by peers across all active debts,
    subtracting any settlements already made.
    """
    entries = db.query(LedgerEntry).filter(
        LedgerEntry.creditor_id == user_id,
        LedgerEntry.status != "settled"
    ).all()
    
    total = 0
    for e in entries:
        total += get_outstanding_amount_for_entry(db, e)
    return total


def get_peer_payable_paise(db: Session, user_id: int) -> int:
    """
    Calculate total amount user_id OWES to peers across all active debts,
    subtracting any settlements already made.
    """
    entries = db.query(LedgerEntry).filter(
        LedgerEntry.debtor_id == user_id,
        LedgerEntry.status != "settled"
    ).all()

    total = 0
    for e in entries:
        total += get_outstanding_amount_for_entry(db, e)
    return total


def get_peer_debts_owed_to_user(db: Session, user_id: int) -> List[dict]:
    """List outstanding debts where user is creditor (people owe user)."""
    entries = db.query(LedgerEntry).filter(
        LedgerEntry.creditor_id == user_id,
        LedgerEntry.status != "settled"
    ).all()

    result = []
    for e in entries:
        outstanding = get_outstanding_amount_for_entry(db, e)
        if outstanding > 0:
            result.append({
                "entry": e,
                "debtor": e.debtor,
                "original_amount": e.amount,
                "outstanding_amount": outstanding,
            })
    return result


def get_peer_debts_owed_by_user(db: Session, user_id: int) -> List[dict]:
    """List outstanding debts where user is debtor (user owes people)."""
    entries = db.query(LedgerEntry).filter(
        LedgerEntry.debtor_id == user_id,
        LedgerEntry.status != "settled"
    ).all()

    result = []
    for e in entries:
        outstanding = get_outstanding_amount_for_entry(db, e)
        if outstanding > 0:
            result.append({
                "entry": e,
                "creditor": e.creditor,
                "original_amount": e.amount,
                "outstanding_amount": outstanding,
            })
    return result
