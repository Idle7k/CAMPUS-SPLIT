import pytest
from app.models.user import User, UserRole
from app.models.vendor import Vendor
from app.models.expense import Expense, ExpenseShare
from app.models.payment import Payment, PaymentAllocation
from app.models.ledger import LedgerEntry
from app.models.settlement import Settlement

from app.services.expense_service import create_expense
from app.services.payment_service import (
    create_payment_attempt,
    record_payment_status,
    confirm_payment,
    get_user_vendor_due_paise,
    get_unpaid_vendor_liability_for_share,
)
from app.services.ledger_service import (
    get_peer_receivable_paise,
    get_peer_payable_paise,
    get_outstanding_amount_for_entry,
)
from app.services.settlement_service import record_settlement


@pytest.fixture
def setup_laundry_scenario(db_session):
    """
    Sets up 3 student roommates (A, B, C), a vendor (Campus Laundry),
    and a ₹210 laundry expense with three ₹70 shares.
    21000 paise total, 7000 paise each.
    """
    # Create students
    student_a = User(
        username="student_a",
        password_hash="fakehash",
        role=UserRole.STUDENT,
        is_active=True,
    )
    student_b = User(
        username="student_b",
        password_hash="fakehash",
        role=UserRole.STUDENT,
        is_active=True,
    )
    student_c = User(
        username="student_c",
        password_hash="fakehash",
        role=UserRole.STUDENT,
        is_active=True,
    )
    # Create vendor
    vendor = Vendor(
        name="Campus Laundry",
        category="Laundry",
        description="Campus laundry service",
        upi_id="campuslaundry@icici",
        is_active=True,
    )
    db_session.add_all([student_a, student_b, student_c, vendor])
    db_session.commit()
    db_session.refresh(student_a)
    db_session.refresh(student_b)
    db_session.refresh(student_c)
    db_session.refresh(vendor)

    # Create ₹210 expense (21000 paise) split equally
    expense = create_expense(
        db=db_session,
        creator_id=student_a.id,
        vendor_id=vendor.id,
        description="Weekly Laundry Service",
        total_amount_paise=21000,
        split_type="equal",
        participant_data=[
            {"user_id": student_a.id, "amount_paise": 7000, "payment_route": "vendor"},
            {"user_id": student_b.id, "amount_paise": 7000, "payment_route": "vendor"},
            {"user_id": student_c.id, "amount_paise": 7000, "payment_route": "vendor"},
        ],
    )

    return {
        "student_a": student_a,
        "student_b": student_b,
        "student_c": student_c,
        "vendor": vendor,
        "expense": expense,
    }


def test_case_a_everyone_pays_own_share_directly(db_session, setup_laundry_scenario):
    """
    CASE A: Everyone pays their own share directly.
    - 3 participants, ₹70 each.
    - Each pays ₹70 to the vendor directly.
    - Vendor outstanding becomes ₹0.
    - NO peer debt is generated for anyone.
    """
    data = setup_laundry_scenario
    a, b, c = data["student_a"], data["student_b"], data["student_c"]
    vendor = data["vendor"]
    expense = data["expense"]

    shares_by_user = {s.user_id: s for s in expense.shares}

    # Verify initial vendor liability
    assert get_user_vendor_due_paise(db_session, a.id) == 7000
    assert get_user_vendor_due_paise(db_session, b.id) == 7000
    assert get_user_vendor_due_paise(db_session, c.id) == 7000

    # Student A pays own share
    pay_a = create_payment_attempt(
        db=db_session,
        payer_id=a.id,
        vendor_id=vendor.id,
        amount_paise=7000,
        expense_id=expense.id,
        allocations_data=[{"share_id": shares_by_user[a.id].id, "amount_paise": 7000}],
    )
    confirm_payment(db_session, pay_a.id)

    # Student B pays own share
    pay_b = create_payment_attempt(
        db=db_session,
        payer_id=b.id,
        vendor_id=vendor.id,
        amount_paise=7000,
        expense_id=expense.id,
        allocations_data=[{"share_id": shares_by_user[b.id].id, "amount_paise": 7000}],
    )
    confirm_payment(db_session, pay_b.id)

    # Student C pays own share
    pay_c = create_payment_attempt(
        db=db_session,
        payer_id=c.id,
        vendor_id=vendor.id,
        amount_paise=7000,
        expense_id=expense.id,
        allocations_data=[{"share_id": shares_by_user[c.id].id, "amount_paise": 7000}],
    )
    confirm_payment(db_session, pay_c.id)

    # Check vendor liabilities: all should be 0
    assert get_user_vendor_due_paise(db_session, a.id) == 0
    assert get_user_vendor_due_paise(db_session, b.id) == 0
    assert get_user_vendor_due_paise(db_session, c.id) == 0

    # Rule 6.3 & Invariant: Direct to vendor payment for own share NEVER generates peer debt
    assert get_peer_receivable_paise(db_session, a.id) == 0
    assert get_peer_payable_paise(db_session, a.id) == 0
    assert get_peer_receivable_paise(db_session, b.id) == 0
    assert get_peer_payable_paise(db_session, b.id) == 0
    assert get_peer_receivable_paise(db_session, c.id) == 0
    assert get_peer_payable_paise(db_session, c.id) == 0

    ledger_count = db_session.query(LedgerEntry).count()
    assert ledger_count == 0


def test_case_b_one_student_pays_complete_bill_covering_others(db_session, setup_laundry_scenario):
    """
    CASE B: One student pays the complete ₹210 laundry bill; two roommates each owe that student ₹70.
    - Student A pays ₹210 to vendor.
    - Allocated: ₹70 to A's share, ₹70 to B's share, ₹70 to C's share.
    - Vendor outstanding is ₹0.
    - Student B owes Student A ₹70.
    - Student C owes Student A ₹70.
    - Student A owes nothing.
    """
    data = setup_laundry_scenario
    a, b, c = data["student_a"], data["student_b"], data["student_c"]
    vendor = data["vendor"]
    expense = data["expense"]

    shares_by_user = {s.user_id: s for s in expense.shares}

    # Student A pays 21000 paise covering all 3 shares
    pay_a = create_payment_attempt(
        db=db_session,
        payer_id=a.id,
        vendor_id=vendor.id,
        amount_paise=21000,
        expense_id=expense.id,
        allocations_data=[
            {"share_id": shares_by_user[a.id].id, "amount_paise": 7000},
            {"share_id": shares_by_user[b.id].id, "amount_paise": 7000},
            {"share_id": shares_by_user[c.id].id, "amount_paise": 7000},
        ],
    )
    confirm_payment(db_session, pay_a.id)

    # Vendor outstanding for all participants must be 0
    assert get_user_vendor_due_paise(db_session, a.id) == 0
    assert get_user_vendor_due_paise(db_session, b.id) == 0
    assert get_user_vendor_due_paise(db_session, c.id) == 0

    # Peer balances
    # Student A: Others owe A ₹140 (14000 paise)
    assert get_peer_receivable_paise(db_session, a.id) == 14000
    assert get_peer_payable_paise(db_session, a.id) == 0

    # Student B: owes A ₹70 (7000 paise)
    assert get_peer_receivable_paise(db_session, b.id) == 0
    assert get_peer_payable_paise(db_session, b.id) == 7000

    # Student C: owes A ₹70 (7000 paise)
    assert get_peer_receivable_paise(db_session, c.id) == 0
    assert get_peer_payable_paise(db_session, c.id) == 7000

    # Check exact ledger entries
    entries = db_session.query(LedgerEntry).all()
    assert len(entries) == 2  # One for B->A, one for C->A (NONE for A->A)

    debtor_ids = {e.debtor_id for e in entries}
    assert debtor_ids == {b.id, c.id}
    for e in entries:
        assert e.creditor_id == a.id
        assert e.amount == 7000
        assert e.status == "outstanding"


def test_case_c_partial_coverage_mixed_vendor_outstanding(db_session, setup_laundry_scenario):
    """
    CASE C: One student pays ₹140, covering their own share and another person's share,
    while the third participant still owes the vendor ₹70.
    - Student A pays ₹140 (covering A's ₹70 and B's ₹70).
    - Student B owes Student A ₹70.
    - Student C owes the vendor ₹70.
    - Student C owes no one in peer debts.
    """
    data = setup_laundry_scenario
    a, b, c = data["student_a"], data["student_b"], data["student_c"]
    vendor = data["vendor"]
    expense = data["expense"]

    shares_by_user = {s.user_id: s for s in expense.shares}

    # Student A pays 14000 paise covering A and B
    pay_a = create_payment_attempt(
        db=db_session,
        payer_id=a.id,
        vendor_id=vendor.id,
        amount_paise=14000,
        expense_id=expense.id,
        allocations_data=[
            {"share_id": shares_by_user[a.id].id, "amount_paise": 7000},
            {"share_id": shares_by_user[b.id].id, "amount_paise": 7000},
        ],
    )
    confirm_payment(db_session, pay_a.id)

    # Vendor liabilities
    assert get_user_vendor_due_paise(db_session, a.id) == 0
    assert get_user_vendor_due_paise(db_session, b.id) == 0
    assert get_user_vendor_due_paise(db_session, c.id) == 7000  # C still owes vendor!

    # Peer debts
    assert get_peer_receivable_paise(db_session, a.id) == 7000
    assert get_peer_payable_paise(db_session, a.id) == 0

    assert get_peer_receivable_paise(db_session, b.id) == 0
    assert get_peer_payable_paise(db_session, b.id) == 7000

    # Student C has NO peer debt
    assert get_peer_receivable_paise(db_session, c.id) == 0
    assert get_peer_payable_paise(db_session, c.id) == 0


def test_case_d_roommate_partially_repays_debt(db_session, setup_laundry_scenario):
    """
    CASE D: A roommate partially repays a ₹70 debt.
    - Student A covered Student B's ₹70 share.
    - Student B repays ₹30 to Student A.
    - Remaining peer debt is ₹40.
    - Over-settlement attempt is rejected.
    """
    data = setup_laundry_scenario
    a, b = data["student_a"], data["student_b"]
    vendor = data["vendor"]
    expense = data["expense"]

    shares_by_user = {s.user_id: s for s in expense.shares}

    pay = create_payment_attempt(
        db=db_session,
        payer_id=a.id,
        vendor_id=vendor.id,
        amount_paise=7000,
        expense_id=expense.id,
        allocations_data=[{"share_id": shares_by_user[b.id].id, "amount_paise": 7000}],
    )
    confirm_payment(db_session, pay.id)

    # Find the ledger entry
    entry = db_session.query(LedgerEntry).filter(
        LedgerEntry.debtor_id == b.id,
        LedgerEntry.creditor_id == a.id,
    ).first()
    assert entry is not None
    assert entry.amount == 7000
    assert get_outstanding_amount_for_entry(db_session, entry) == 7000

    # Partial settlement: B pays A 3000 paise (₹30)
    settlement = record_settlement(
        db=db_session,
        payer_id=b.id,
        recipient_id=a.id,
        amount_paise=3000,
        ledger_entry_id=entry.id,
        notes="Partial repayment for laundry",
    )
    assert settlement.amount == 3000

    # Check updated balances
    assert get_outstanding_amount_for_entry(db_session, entry) == 4000
    assert entry.status == "partially_settled"
    assert get_peer_payable_paise(db_session, b.id) == 4000
    assert get_peer_receivable_paise(db_session, a.id) == 4000

    # Try over-settlement: Attempt to repay 5000 paise when only 4000 remains -> must fail
    with pytest.raises(ValueError, match="exceeds outstanding debt"):
        record_settlement(
            db=db_session,
            payer_id=b.id,
            recipient_id=a.id,
            amount_paise=5000,
            ledger_entry_id=entry.id,
        )

    # Settle the remaining 4000 paise
    settlement_final = record_settlement(
        db=db_session,
        payer_id=b.id,
        recipient_id=a.id,
        amount_paise=4000,
        ledger_entry_id=entry.id,
    )
    assert get_outstanding_amount_for_entry(db_session, entry) == 0
    assert entry.status == "settled"
    assert get_peer_payable_paise(db_session, b.id) == 0
    assert get_peer_receivable_paise(db_session, a.id) == 0


def test_case_e_repeated_payment_confirmation_idempotency(db_session, setup_laundry_scenario):
    """
    CASE E: Repeated payment confirmation does not duplicate ledger entries or share updates.
    """
    data = setup_laundry_scenario
    a, b = data["student_a"], data["student_b"]
    vendor = data["vendor"]
    expense = data["expense"]

    shares_by_user = {s.user_id: s for s in expense.shares}

    pay = create_payment_attempt(
        db=db_session,
        payer_id=a.id,
        vendor_id=vendor.id,
        amount_paise=7000,
        expense_id=expense.id,
        allocations_data=[{"share_id": shares_by_user[b.id].id, "amount_paise": 7000}],
    )

    # First confirmation
    confirm_payment(db_session, pay.id)
    assert db_session.query(LedgerEntry).count() == 1
    assert get_peer_payable_paise(db_session, b.id) == 7000

    # Second confirmation (should be idempotent no-op)
    confirm_payment(db_session, pay.id)
    assert db_session.query(LedgerEntry).count() == 1
    assert get_peer_payable_paise(db_session, b.id) == 7000

    # Third confirmation
    confirm_payment(db_session, pay.id)
    assert db_session.query(LedgerEntry).count() == 1
    assert get_peer_payable_paise(db_session, b.id) == 7000


def test_case_f_failed_or_cancelled_payments_do_not_clear_liabilities(db_session, setup_laundry_scenario):
    """
    CASE F: Failed or cancelled payments do not clear vendor liabilities and do not create peer debts.
    """
    data = setup_laundry_scenario
    a, b = data["student_a"], data["student_b"]
    vendor = data["vendor"]
    expense = data["expense"]

    shares_by_user = {s.user_id: s for s in expense.shares}

    # Attempt 1: Fails
    pay_failed = create_payment_attempt(
        db=db_session,
        payer_id=a.id,
        vendor_id=vendor.id,
        amount_paise=7000,
        expense_id=expense.id,
        allocations_data=[{"share_id": shares_by_user[b.id].id, "amount_paise": 7000}],
    )
    record_payment_status(db_session, pay_failed.id, "failed")

    # Attempt 2: Cancelled
    pay_cancelled = create_payment_attempt(
        db=db_session,
        payer_id=b.id,
        vendor_id=vendor.id,
        amount_paise=7000,
        expense_id=expense.id,
        allocations_data=[{"share_id": shares_by_user[b.id].id, "amount_paise": 7000}],
    )
    record_payment_status(db_session, pay_cancelled.id, "cancelled")

    # Cannot confirm a failed or cancelled payment
    with pytest.raises(ValueError, match="Cannot confirm payment that is already"):
        confirm_payment(db_session, pay_failed.id)

    # Vendor liabilities must remain unchanged (₹70 each)
    assert get_user_vendor_due_paise(db_session, a.id) == 7000
    assert get_user_vendor_due_paise(db_session, b.id) == 7000
    assert get_unpaid_vendor_liability_for_share(db_session, shares_by_user[b.id]) == 7000

    # No peer debts generated
    assert db_session.query(LedgerEntry).count() == 0
    assert get_peer_receivable_paise(db_session, a.id) == 0
    assert get_peer_payable_paise(db_session, b.id) == 0
