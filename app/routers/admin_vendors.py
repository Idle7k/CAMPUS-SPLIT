from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin, get_csrf_token, verify_csrf_token
from app.models.user import User
from app.services import vendor_service

router = APIRouter(prefix="/admin/vendors", tags=["Admin Vendors"])


@router.get("", response_class=HTMLResponse)
def admin_vendors_list(
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Administrator console listing all campus vendors with active/inactive status."""
    templates = request.app.state.templates
    vendors = vendor_service.get_vendors(db, active_only=False)

    return templates.TemplateResponse(
        request=request,
        name="admin/vendors/index.html",
        context={
            "current_user": current_user,
            "active_page": "admin_vendors",
            "csrf_token": get_csrf_token(request),
            "vendors": vendors,
        },
    )


@router.get("/new", response_class=HTMLResponse)
def admin_new_vendor_form(
    request: Request,
    current_user: User = Depends(require_admin),
):
    """Render form to create a new campus vendor."""
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request,
        name="admin/vendors/form.html",
        context={
            "current_user": current_user,
            "active_page": "admin_vendors",
            "csrf_token": get_csrf_token(request),
            "vendor": None,
            "form_data": None,
        },
    )


@router.post("/new", response_class=HTMLResponse)
def admin_create_vendor(
    request: Request,
    name: str = Form(...),
    category: str = Form(...),
    upi_id: str = Form(...),
    description: str = Form(None),
    is_active: bool = Form(False),
    csrf_token: str = Form(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Process creation of a new campus vendor."""
    templates = request.app.state.templates

    if not verify_csrf_token(request, csrf_token):
        return templates.TemplateResponse(
            request=request,
            name="admin/vendors/form.html",
            context={
                "current_user": current_user,
                "active_page": "admin_vendors",
                "csrf_token": get_csrf_token(request),
                "error": "Invalid session token. Please try again.",
                "vendor": None,
                "form_data": {"name": name, "category": category, "upi_id": upi_id, "description": description},
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        vendor_service.create_vendor(
            db=db,
            name=name,
            category=category,
            description=description,
            upi_id=upi_id,
            is_active=is_active,
        )
    except ValueError as e:
        return templates.TemplateResponse(
            request=request,
            name="admin/vendors/form.html",
            context={
                "current_user": current_user,
                "active_page": "admin_vendors",
                "csrf_token": get_csrf_token(request),
                "error": str(e),
                "vendor": None,
                "form_data": {"name": name, "category": category, "upi_id": upi_id, "description": description},
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return RedirectResponse(url="/admin/vendors", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{vendor_id}/edit", response_class=HTMLResponse)
def admin_edit_vendor_form(
    vendor_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Render edit form for an existing vendor."""
    templates = request.app.state.templates
    vendor = vendor_service.get_vendor_by_id(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    return templates.TemplateResponse(
        request=request,
        name="admin/vendors/form.html",
        context={
            "current_user": current_user,
            "active_page": "admin_vendors",
            "csrf_token": get_csrf_token(request),
            "vendor": vendor,
            "form_data": None,
        },
    )


@router.post("/{vendor_id}/edit", response_class=HTMLResponse)
def admin_update_vendor(
    vendor_id: int,
    request: Request,
    name: str = Form(...),
    category: str = Form(...),
    upi_id: str = Form(...),
    description: str = Form(None),
    is_active: bool = Form(False),
    csrf_token: str = Form(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Process update of an existing vendor."""
    templates = request.app.state.templates

    if not verify_csrf_token(request, csrf_token):
        vendor = vendor_service.get_vendor_by_id(db, vendor_id)
        return templates.TemplateResponse(
            request=request,
            name="admin/vendors/form.html",
            context={
                "current_user": current_user,
                "active_page": "admin_vendors",
                "csrf_token": get_csrf_token(request),
                "error": "Invalid session token. Please try again.",
                "vendor": vendor,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        updated = vendor_service.update_vendor(
            db=db,
            vendor_id=vendor_id,
            name=name,
            category=category,
            description=description,
            upi_id=upi_id,
            is_active=is_active,
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    except ValueError as e:
        vendor = vendor_service.get_vendor_by_id(db, vendor_id)
        return templates.TemplateResponse(
            request=request,
            name="admin/vendors/form.html",
            context={
                "current_user": current_user,
                "active_page": "admin_vendors",
                "csrf_token": get_csrf_token(request),
                "error": str(e),
                "vendor": vendor,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return RedirectResponse(url="/admin/vendors", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{vendor_id}/toggle")
def admin_toggle_vendor(
    vendor_id: int,
    request: Request,
    csrf_token: str = Form(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Toggles active/inactive status for a vendor."""
    if not verify_csrf_token(request, csrf_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSRF token")

    updated = vendor_service.toggle_vendor_status(db, vendor_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    return RedirectResponse(url="/admin/vendors", status_code=status.HTTP_303_SEE_OTHER)
