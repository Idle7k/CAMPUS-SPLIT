from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_authenticated_user, get_csrf_token
from app.models.user import User
from app.models.expense import Expense, ExpenseShare
from app.models.ledger import LedgerEntry
from app.models.group import Group, GroupMember
from app.services import vendor_service

router = APIRouter(tags=["Dashboard"])


@router.get("/", response_class=HTMLResponse)
def index_redirect(
    request: Request,
):
    """Root route redirects directly to the authenticated dashboard."""
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_view(
    request: Request,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    templates = request.app.state.templates
    active_vendors = vendor_service.get_vendors(db, active_only=True)

    # Calculate real figures from database
    peer_receivable = db.query(func.coalesce(func.sum(LedgerEntry.amount), 0)).filter(
        LedgerEntry.creditor_id == current_user.id,
        LedgerEntry.status == "outstanding"
    ).scalar() or 0

    peer_payable = db.query(func.coalesce(func.sum(LedgerEntry.amount), 0)).filter(
        LedgerEntry.debtor_id == current_user.id,
        LedgerEntry.status == "outstanding"
    ).scalar() or 0

    vendor_due = db.query(func.coalesce(func.sum(ExpenseShare.amount), 0)).filter(
        ExpenseShare.user_id == current_user.id,
        ExpenseShare.status == "unpaid"
    ).scalar() or 0

    recent_expenses = db.query(Expense).filter(
        or_(
            Expense.creator_id == current_user.id,
            Expense.shares.any(ExpenseShare.user_id == current_user.id)
        )
    ).order_by(Expense.created_at.desc()).limit(5).all()

    return templates.TemplateResponse(
        request=request,
        name="dashboard/index.html",
        context={
            "current_user": current_user,
            "active_page": "dashboard",
            "csrf_token": get_csrf_token(request),
            "active_vendor_count": len(active_vendors),
            "sample_vendors": active_vendors[:4],
            "peer_receivable_paise": peer_receivable,
            "peer_payable_paise": peer_payable,
            "vendor_due_paise": vendor_due,
            "recent_expenses": recent_expenses,
        },
    )


@router.get("/balances", response_class=HTMLResponse)
def balances_view(
    request: Request,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """View personal peer liabilities and vendor dues segregated."""
    templates = request.app.state.templates

    peer_receivable = db.query(func.coalesce(func.sum(LedgerEntry.amount), 0)).filter(
        LedgerEntry.creditor_id == current_user.id,
        LedgerEntry.status == "outstanding"
    ).scalar() or 0

    peer_payable = db.query(func.coalesce(func.sum(LedgerEntry.amount), 0)).filter(
        LedgerEntry.debtor_id == current_user.id,
        LedgerEntry.status == "outstanding"
    ).scalar() or 0

    vendor_due = db.query(func.coalesce(func.sum(ExpenseShare.amount), 0)).filter(
        ExpenseShare.user_id == current_user.id,
        ExpenseShare.status == "unpaid"
    ).scalar() or 0

    return templates.TemplateResponse(
        request=request,
        name="balances/index.html",
        context={
            "current_user": current_user,
            "active_page": "balances",
            "csrf_token": get_csrf_token(request),
            "peer_receivable_paise": peer_receivable,
            "peer_payable_paise": peer_payable,
            "vendor_due_paise": vendor_due,
        },
    )


@router.get("/groups", response_class=HTMLResponse)
def groups_list_view(
    request: Request,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """View all groups the user created or is member of."""
    templates = request.app.state.templates
    user_groups = db.query(Group).filter(
        or_(
            Group.creator_id == current_user.id,
            Group.members.any(GroupMember.user_id == current_user.id)
        )
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="groups/index.html",
        context={
            "current_user": current_user,
            "active_page": "groups",
            "csrf_token": get_csrf_token(request),
            "groups": user_groups,
        },
    )
