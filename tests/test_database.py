import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User, UserRole
from app.models.group import Group, GroupMember
from app.models.vendor import Vendor
from app.models.expense import Expense, ExpenseShare
from app.models.payment import Payment, PaymentAllocation
from app.models.ledger import LedgerEntry
from app.models.settlement import Settlement
from app.services.auth_service import hash_password


def test_sqlite_foreign_key_enforcement(db_session):
    """
    Ensure SQLite enforces foreign keys via PRAGMA foreign_keys = ON.
    Inserting a record with a non-existent foreign key must raise IntegrityError.
    """
    invalid_expense = Expense(
        creator_id=999999,  # Non-existent user
        vendor_id=999999,   # Non-existent vendor
        description="Invalid FK Expense",
        total_amount=5000,
        split_type="equal",
        status="active",
    )
    db_session.add(invalid_expense)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_group_member_cascade_delete(db_session):
    """
    Deleting a group should cascade-delete group_members join records.
    """
    user = User(
        username="group_creator",
        password_hash=hash_password("password123"),
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    group = Group(name="Hostel Room 402", creator_id=user.id)
    db_session.add(group)
    db_session.commit()

    membership = GroupMember(group_id=group.id, user_id=user.id, role="admin")
    db_session.add(membership)
    db_session.commit()

    # Verify membership exists
    assert db_session.query(GroupMember).filter_by(group_id=group.id).count() == 1

    # Delete group
    db_session.delete(group)
    db_session.commit()

    # Membership should be cascade-deleted
    assert db_session.query(GroupMember).filter_by(group_id=group.id).count() == 0
    # User should still exist
    assert db_session.query(User).filter_by(id=user.id).first() is not None


def test_financial_history_restrict_delete(db_session):
    """
    Per AGENTS.md Section 5:
    'Do not cascade-delete financial history when a user, group, vendor or expense is edited or deactivated.'
    Deleting a user who is creator of an expense must be restricted.
    """
    user = User(
        username="expense_creator",
        password_hash=hash_password("password123"),
        role=UserRole.STUDENT,
        is_active=True,
    )
    vendor = Vendor(
        name="Canteen",
        category="Dining",
        upi_id="canteen@upi",
        is_active=True,
    )
    db_session.add_all([user, vendor])
    db_session.commit()

    expense = Expense(
        creator_id=user.id,
        vendor_id=vendor.id,
        description="Dinner",
        total_amount=30000,
        split_type="equal",
        status="active",
    )
    db_session.add(expense)
    db_session.commit()

    # Attempting to delete user must fail due to ondelete="RESTRICT"
    db_session.delete(user)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
