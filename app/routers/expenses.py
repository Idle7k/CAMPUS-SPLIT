import json
from decimal import Decimal
from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.dependencies import require_authenticated_user, get_csrf_token, verify_csrf_token
from app.models.user import User
from app.models.vendor import Vendor
from app.models.group import Group, GroupMember
from app.models.expense import Expense, ExpenseShare
from app.services import vendor_service, expense_service

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("", response_class=HTMLResponse)
def expenses_list(
    request: Request,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """View all expenses created by or shared with current user."""
    templates = request.app.state.templates
    user_expenses = db.query(Expense).filter(
        or_(
            Expense.creator_id == current_user.id,
            Expense.shares.any(ExpenseShare.user_id == current_user.id)
        )
    ).order_by(Expense.created_at.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="expenses/index.html",
        context={
            "current_user": current_user,
            "active_page": "expenses",
            "csrf_token": get_csrf_token(request),
            "expenses": user_expenses,
        },
    )


@router.get("/new", response_class=HTMLResponse)
def new_expense_page(
    request: Request,
    vendor_id: int = None,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """Render multi-step expense creation workflow."""
    templates = request.app.state.templates
    active_vendors = vendor_service.get_vendors(db, active_only=True)
    all_students = db.query(User).filter(User.is_active.is_(True)).order_by(User.username.asc()).all()
    user_groups = db.query(Group).filter(
        or_(
            Group.creator_id == current_user.id,
            Group.members.any(GroupMember.user_id == current_user.id)
        )
    ).all()

    # Pre-select vendor if query param provided
    selected_vendor = None
    if vendor_id:
        selected_vendor = vendor_service.get_vendor_by_id(db, vendor_id)

    return templates.TemplateResponse(
        request=request,
        name="expenses/form.html",
        context={
            "current_user": current_user,
            "active_page": "expenses",
            "csrf_token": get_csrf_token(request),
            "vendors": active_vendors,
            "selected_vendor": selected_vendor,
            "students": all_students,
            "groups": user_groups,
            "error": None,
        },
    )


@router.post("/preview", response_class=JSONResponse)
def preview_split(
    request: Request,
    data: dict,
    current_user: User = Depends(require_authenticated_user),
):
    """
    Authoritative server-side split calculation preview.
    Validates amounts, percentages, or custom inputs and returns calculated shares in paise and rupees.
    """
    try:
        total_amount_rupees = data.get("total_amount")
        total_paise = expense_service.rupees_to_paise(total_amount_rupees)
        split_type = data.get("split_type", "equal")
        participants = data.get("participants", [])

        if not participants:
            return JSONResponse(status_code=400, content={"error": "At least one participant is required"})

        if split_type == "equal":
            shares = expense_service.calculate_equal_split(total_paise, len(participants))
        elif split_type == "percentage":
            percentages = [Decimal(str(p.get("percentage", 0))) for p in participants]
            shares = expense_service.calculate_percentage_split(total_paise, percentages)
        elif split_type == "custom":
            custom_paise = [expense_service.rupees_to_paise(p.get("custom_amount", 0)) for p in participants]
            shares = expense_service.calculate_custom_split(total_paise, custom_paise)
        else:
            return JSONResponse(status_code=400, content={"error": f"Invalid split type: {split_type}"})

        result = []
        for i, p in enumerate(participants):
            share_paise = shares[i]
            result.append({
                "user_id": p.get("user_id"),
                "amount_paise": share_paise,
                "amount_rupees": f"{share_paise / 100:.2f}",
            })

        return JSONResponse(content={
            "total_paise": total_paise,
            "total_rupees": f"{total_paise / 100:.2f}",
            "shares": result,
            "matched": sum(shares) == total_paise,
        })
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.post("/new", response_class=HTMLResponse)
async def create_expense_endpoint(
    request: Request,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """Process expense creation form submission."""
    templates = request.app.state.templates

    # Handle form or JSON submission
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        csrf = body.get("csrf_token")
        if not verify_csrf_token(request, csrf):
            return JSONResponse(status_code=400, content={"error": "Invalid CSRF token"})
        payload = body
    else:
        form = await request.form()
        csrf = form.get("csrf_token")
        if not verify_csrf_token(request, csrf):
            active_vendors = vendor_service.get_vendors(db, active_only=True)
            all_students = db.query(User).filter(User.is_active.is_(True)).all()
            return templates.TemplateResponse(
                request=request,
                name="expenses/form.html",
                context={
                    "current_user": current_user,
                    "active_page": "expenses",
                    "csrf_token": get_csrf_token(request),
                    "vendors": active_vendors,
                    "students": all_students,
                    "error": "Session token invalid or expired. Please try again.",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            payload_json = form.get("expense_data")
            payload = json.loads(payload_json) if payload_json else {}
        except Exception:
            payload = {}

    try:
        vendor_id = int(payload.get("vendor_id"))
        description = str(payload.get("description", "")).strip()
        total_amount_rupees = payload.get("total_amount")
        total_paise = expense_service.rupees_to_paise(total_amount_rupees)
        split_type = payload.get("split_type", "equal")
        group_id = payload.get("group_id")
        if group_id:
            group_id = int(group_id)

        participants_in = payload.get("participants", [])
        if not participants_in:
            raise ValueError("No participants specified")

        # Calculate authoritative share amounts in paise
        if split_type == "equal":
            shares = expense_service.calculate_equal_split(total_paise, len(participants_in))
        elif split_type == "percentage":
            percentages = [Decimal(str(p.get("percentage", 0))) for p in participants_in]
            shares = expense_service.calculate_percentage_split(total_paise, percentages)
        elif split_type == "custom":
            custom_paise = [expense_service.rupees_to_paise(p.get("custom_amount", 0)) for p in participants_in]
            shares = expense_service.calculate_custom_split(total_paise, custom_paise)
        else:
            raise ValueError(f"Unknown split type: {split_type}")

        # Construct participant_data list with routes
        participant_data = []
        for idx, p in enumerate(participants_in):
            u_id = int(p["user_id"])
            route = p.get("payment_route", "vendor")
            cov_id = p.get("covered_by_id")
            if cov_id:
                cov_id = int(cov_id)

            participant_data.append({
                "user_id": u_id,
                "amount_paise": shares[idx],
                "payment_route": route,
                "covered_by_id": cov_id,
            })

        expense = expense_service.create_expense(
            db=db,
            creator_id=current_user.id,
            vendor_id=vendor_id,
            description=description,
            total_amount_paise=total_paise,
            split_type=split_type,
            participant_data=participant_data,
            group_id=group_id,
        )

        if "application/json" in content_type:
            return JSONResponse(content={"success": True, "expense_id": expense.id, "redirect_url": f"/expenses/{expense.id}"})
        return RedirectResponse(url=f"/expenses/{expense.id}", status_code=status.HTTP_303_SEE_OTHER)

    except (ValueError, TypeError, KeyError) as e:
        if "application/json" in content_type:
            return JSONResponse(status_code=400, content={"error": str(e)})

        active_vendors = vendor_service.get_vendors(db, active_only=True)
        all_students = db.query(User).filter(User.is_active.is_(True)).all()
        return templates.TemplateResponse(
            request=request,
            name="expenses/form.html",
            context={
                "current_user": current_user,
                "active_page": "expenses",
                "csrf_token": get_csrf_token(request),
                "vendors": active_vendors,
                "students": all_students,
                "error": str(e),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/{expense_id}", response_class=HTMLResponse)
def expense_detail_view(
    expense_id: int,
    request: Request,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """View details of a specific shared expense."""
    templates = request.app.state.templates
    expense = expense_service.get_expense_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    return templates.TemplateResponse(
        request=request,
        name="expenses/detail.html",
        context={
            "current_user": current_user,
            "active_page": "expenses",
            "csrf_token": get_csrf_token(request),
            "expense": expense,
        },
    )
