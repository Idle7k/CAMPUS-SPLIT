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


def test_models_complete_domain_graph(db_session):
    """
    Verifies that all 10 domain entities can be created and linked according
    to the Phase 1 schema requirements.
    """
    # 1. Users
    alice = User(username="alice", password_hash=hash_password("pass123"), role=UserRole.STUDENT)
    bob = User(username="bob", password_hash=hash_password("pass123"), role=UserRole.STUDENT)
    db_session.add_all([alice, bob])
    db_session.commit()

    # 2. Group & Membership
    roommates = Group(name="Flat 3B", creator_id=alice.id)
    db_session.add(roommates)
    db_session.commit()

    m1 = GroupMember(group_id=roommates.id, user_id=alice.id, role="admin")
    m2 = GroupMember(group_id=roommates.id, user_id=bob.id, role="member")
    db_session.add_all([m1, m2])
    db_session.commit()

    # 3. Vendor
    vendor = Vendor(
        name="Night Canteen",
        category="Dining",
        description="Late night food",
        upi_id="nightcanteen@oksbi",
        is_active=True,
    )
    db_session.add(vendor)
    db_session.commit()

    # 4. Expense & ExpenseShares (₹210 = 21000 paise; two shares of 10500 paise each)
    expense = Expense(
        creator_id=alice.id,
        vendor_id=vendor.id,
        group_id=roommates.id,
        description="Late night maggi & tea",
        total_amount=21000,
        split_type="equal",
        status="active",
    )
    db_session.add(expense)
    db_session.commit()

    share_alice = ExpenseShare(expense_id=expense.id, user_id=alice.id, amount=10500, status="paid")
    share_bob = ExpenseShare(expense_id=expense.id, user_id=bob.id, amount=10500, status="unpaid")
    db_session.add_all([share_alice, share_bob])
    db_session.commit()

    # 5. Payment & PaymentAllocation (Alice pays ₹21000 to vendor, covering both shares)
    payment = Payment(
        payer_id=alice.id,
        vendor_id=vendor.id,
        expense_id=expense.id,
        amount=21000,
        method="upi",
        status="confirmed_demo",
        reference_id="UPI-DEMO-REF-001",
    )
    db_session.add(payment)
    db_session.commit()

    alloc_alice = PaymentAllocation(payment_id=payment.id, expense_share_id=share_alice.id, allocated_amount=10500)
    alloc_bob = PaymentAllocation(payment_id=payment.id, expense_share_id=share_bob.id, allocated_amount=10500)
    db_session.add_all([alloc_alice, alloc_bob])
    db_session.commit()

    # 6. LedgerEntry (Bob owes Alice ₹105.00 / 10500 paise because Alice covered Bob's share)
    debt = LedgerEntry(
        debtor_id=bob.id,
        creditor_id=alice.id,
        amount=10500,
        expense_id=expense.id,
        payment_allocation_id=alloc_bob.id,
        status="outstanding",
        notes="Alice covered Bob's share of dinner",
    )
    db_session.add(debt)
    db_session.commit()

    # 7. Settlement (Bob repays Alice ₹50.00 / 5000 paise partially)
    repayment = Settlement(
        payer_id=bob.id,
        recipient_id=alice.id,
        ledger_entry_id=debt.id,
        amount=5000,
        status="confirmed_demo",
        notes="Partial cash reimbursement",
    )
    db_session.add(repayment)
    db_session.commit()

    # Assertions on relationships
    assert len(expense.shares) == 2
    assert expense.shares[0].amount == 10500
    assert debt.debtor.username == "bob"
    assert debt.creditor.username == "alice"
    assert len(debt.settlements) == 1
    assert debt.settlements[0].amount == 5000
    assert payment.allocations[0].payment_id == payment.id


def test_unique_constraints(db_session):
    """Test duplicate constraints on domain models."""
    u1 = User(username="unique_user", password_hash="hash1", role=UserRole.STUDENT)
    db_session.add(u1)
    db_session.commit()

    # 1. Duplicate username
    duplicate_user = User(username="unique_user", password_hash="hash2", role=UserRole.STUDENT)
    db_session.add(duplicate_user)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # 2. Duplicate GroupMember
    g = Group(name="Study Group", creator_id=u1.id)
    db_session.add(g)
    db_session.commit()

    m1 = GroupMember(group_id=g.id, user_id=u1.id)
    m2 = GroupMember(group_id=g.id, user_id=u1.id)
    db_session.add(m1)
    db_session.commit()

    db_session.add(m2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_money_represented_in_integer_paise(db_session):
    """
    Verifies that all monetary fields are typed as integer paise,
    protecting against floating point precision errors.
    """
    user = User(username="paise_user", password_hash="hash", role=UserRole.STUDENT)
    vendor = Vendor(name="Store", category="Supplies", upi_id="store@upi", is_active=True)
    db_session.add_all([user, vendor])
    db_session.commit()

    # ₹149.50 must be stored as 14950 paise
    paise_amount = 14950
    expense = Expense(
        creator_id=user.id,
        vendor_id=vendor.id,
        description="Notebooks",
        total_amount=paise_amount,
        split_type="equal",
        status="active",
    )
    db_session.add(expense)
    db_session.commit()
    db_session.refresh(expense)

    assert isinstance(expense.total_amount, int)
    assert expense.total_amount == 14950
