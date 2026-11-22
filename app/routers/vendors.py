from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_authenticated_user, get_csrf_token
from app.models.user import User
from app.services import vendor_service

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.get("", response_class=HTMLResponse)
def list_active_vendors(
    request: Request,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """Student campus vendor directory, listing all active vendors."""
    templates = request.app.state.templates
    vendors = vendor_service.get_vendors(db, active_only=True)
    categories = sorted(list({v.category for v in vendors}))

    return templates.TemplateResponse(
        request=request,
        name="vendors/index.html",
        context={
            "current_user": current_user,
            "active_page": "vendors",
            "csrf_token": get_csrf_token(request),
            "vendors": vendors,
            "categories": categories,
        },
    )


@router.get("/{vendor_id}", response_class=HTMLResponse)
def vendor_details(
    vendor_id: int,
    request: Request,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """View details of a specific campus vendor."""
    templates = request.app.state.templates
    vendor = vendor_service.get_vendor_by_id(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    return templates.TemplateResponse(
        request=request,
        name="vendors/detail.html",
        context={
            "current_user": current_user,
            "active_page": "vendors",
            "csrf_token": get_csrf_token(request),
            "vendor": vendor,
        },
    )
