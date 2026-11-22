import pytest
from decimal import Decimal
from app.models.user import User, UserRole
from app.models.vendor import Vendor
from app.models.group import Group, GroupMember
from app.models.expense import Expense, ExpenseShare
from app.models.ledger import LedgerEntry
from app.models.payment import Payment, PaymentAllocation
from app.services import expense_service
from tests.conftest import get_form_csrf_token


def test_rupees_to_paise():
    """Verify strict conversion from rupees to integer paise without float inaccuracy."""
    assert expense_service.rupees_to_paise(210) == 21000
    assert expense_service.rupees_to_paise("210") == 21000
    assert expense_service.rupees_to_paise("70.50") == 7050
    assert expense_service.rupees_to_paise(Decimal("70.55")) == 7055

    with pytest.raises(ValueError):
        expense_service.rupees_to_paise("invalid_amount")


def test_calculate_equal_split_even():
    """Test standard even division: 21000 paise (₹210) among 3 students."""
    shares = expense_service.calculate_equal_split(21000, 3)
    assert len(shares) == 3
    assert shares == [7000, 7000, 7000]  # Exactly ₹70.00 each
    assert sum(shares) == 21000


def test_calculate_equal_split_with_remainder():
    """Test equal split with 1 or 2 paise remainder: 100 paise (₹1) among 3 students."""
    shares = expense_service.calculate_equal_split(100, 3)
    assert len(shares) == 3
    # 100 // 3 = 33, remainder 1 -> first student gets 34, others 33
    assert shares == [34, 33, 33]
    assert sum(shares) == 100


def test_calculate_percentage_split():
    """Test percentage split totaling 100%."""
    total = 10000  # ₹100
    pcts = [Decimal("50"), Decimal("25"), Decimal("25")]
    shares = expense_service.calculate_percentage_split(total, pcts)
    assert shares == [5000, 2500, 2500]
    assert sum(shares) == total

    # Rejects percentages not summing to 100
    with pytest.raises(ValueError, match="must sum to exactly 100"):
        expense_service.calculate_percentage_split(total, [Decimal("50"), Decimal("40")])


def test_calculate_custom_split():
    """Test custom share validation."""
    total = 21000
    custom = [10000, 6000, 5000]
    validated = expense_service.calculate_custom_split(total, custom)
    assert validated == custom
    assert sum(validated) == total

    # Fails if sum does not match
    with pytest.raises(ValueError, match="does not match total"):
        expense_service.calculate_custom_split(total, [10000, 6000, 4000])


def test_laundry_expense_demonstration_three_shares(db_session):
    """
    Core demonstration required by Task 04:
    - ₹210 laundry bill split among 3 participants (₹70 each).
    - Participant A (Ananya/Creator): pays vendor directly (₹70 share).
    - Participant B (Rohan): covered by Participant A (₹70 share).
    - Participant C (Kabir): already paid directly to vendor (₹70 share).

    Expected Invariants:
    1. Expense total = 21000 paise.
    2. Shares: three shares of 7000 paise each.
    3. Peer Debt: EXACTLY ONE peer debt exists — Rohan owes Ananya ₹70.
    4. NO peer debt exists for Ananya (paying vendor directly).
    5. NO peer debt exists for Kabir (paying vendor directly for own share).
    """
    # 1. Create participants
    u_ananya = User(username="ananya_demo", password_hash="hash", role=UserRole.STUDENT, is_active=True)
    u_rohan = User(username="rohan_demo", password_hash="hash", role=UserRole.STUDENT, is_active=True)
    u_kabir = User(username="kabir_demo", password_hash="hash", role=UserRole.STUDENT, is_active=True)
    db_session.add_all([u_ananya, u_rohan, u_kabir])

    vendor = Vendor(
        name="Campus Laundry Co.",
        category="Laundry",
        upi_id="campuslaundry@icici",
        is_active=True,
    )
    db_session.add(vendor)
    db_session.commit()

    # 2. Setup 3-person split
    total_paise = 21000  # ₹210.00
    equal_shares = expense_service.calculate_equal_split(total_paise, 3)
    assert equal_shares == [7000, 7000, 7000]

    participants = [
        {
            "user_id": u_ananya.id,
            "amount_paise": equal_shares[0],
            "payment_route": "vendor",  # Will pay vendor directly later
        },
        {
            "user_id": u_rohan.id,
            "amount_paise": equal_shares[1],
            "payment_route": "covered",  # Covered by Ananya
            "covered_by_id": u_ananya.id,
        },
        {
            "user_id": u_kabir.id,
            "amount_paise": equal_shares[2],
            "payment_route": "already_paid",  # Paid directly to vendor
        },
    ]

    # 3. Create expense
    expense = expense_service.create_expense(
        db=db_session,
        creator_id=u_ananya.id,
        vendor_id=vendor.id,
        description="Weekly laundry pickup",
        total_amount_paise=total_paise,
        split_type="equal",
        participant_data=participants,
    )

    # 4. Verify Expense & Shares
    assert expense.id is not None
    assert expense.total_amount == 21000
    assert len(expense.shares) == 3

    shares_by_user = {s.user_id: s for s in expense.shares}
    assert shares_by_user[u_ananya.id].amount == 7000
    assert shares_by_user[u_ananya.id].status == "unpaid"  # Owes vendor

    assert shares_by_user[u_rohan.id].amount == 7000
    assert shares_by_user[u_rohan.id].status == "paid"  # Share covered

    assert shares_by_user[u_kabir.id].amount == 7000
    assert shares_by_user[u_kabir.id].status == "paid"  # Paid directly to vendor

    # 5. Verify Peer Debts (Rule 6.3)
    ledger_entries = db_session.query(LedgerEntry).filter(LedgerEntry.expense_id == expense.id).all()
    assert len(ledger_entries) == 1, "Only the covered share should generate a peer debt"

    debt = ledger_entries[0]
    assert debt.debtor_id == u_rohan.id, "Debtor must be Rohan"
    assert debt.creditor_id == u_ananya.id, "Creditor must be Ananya"
    assert debt.amount == 7000, "Debt must be exactly ₹70.00 (7000 paise)"
    assert debt.status == "outstanding"


def test_expense_creation_rejects_sum_mismatch(db_session):
    """Ensure atomic rollback if shares do not equal total amount."""
    u1 = User(username="user1", password_hash="h", role=UserRole.STUDENT, is_active=True)
    v = Vendor(name="V1", category="C", upi_id="v@upi", is_active=True)
    db_session.add_all([u1, v])
    db_session.commit()

    with pytest.raises(ValueError, match="does not equal expense total"):
        expense_service.create_expense(
            db=db_session,
            creator_id=u1.id,
            vendor_id=v.id,
            description="Mismatch expense",
            total_amount_paise=10000,
            split_type="equal",
            participant_data=[{"user_id": u1.id, "amount_paise": 9000, "payment_route": "vendor"}],
        )

    # Ensure nothing persisted
    assert db_session.query(Expense).filter_by(description="Mismatch expense").first() is None


def test_http_expense_creation_endpoint(authenticated_student_client, test_vendor, test_student_user, db_session):
    """Test full HTTP POST expense creation."""
    other_user = User(username="other_peer", password_hash="h", role=UserRole.STUDENT, is_active=True)
    db_session.add(other_user)
    db_session.commit()

    csrf_token = get_form_csrf_token(authenticated_student_client, "/expenses/new")

    response = authenticated_student_client.post(
        "/expenses/new",
        json={
            "csrf_token": csrf_token,
            "vendor_id": test_vendor.id,
            "description": "Lab equipment split",
            "total_amount": "200.00",
            "split_type": "equal",
            "participants": [
                {"user_id": test_student_user.id, "payment_route": "vendor"},
                {"user_id": other_user.id, "payment_route": "covered"},
            ],
        },
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify expense in DB
    created = db_session.query(Expense).filter(Expense.id == data["expense_id"]).first()
    assert created is not None
    assert created.total_amount == 20000
    assert len(created.shares) == 2
    assert all(s.amount == 10000 for s in created.shares)
