from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_authenticated_user, get_csrf_token
from app.models.user import User
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

    return templates.TemplateResponse(
        request=request,
        name="dashboard/index.html",
        context={
            "current_user": current_user,
            "active_page": "dashboard",
            "csrf_token": get_csrf_token(request),
            "active_vendor_count": len(active_vendors),
            "sample_vendors": active_vendors[:4],
        },
    )
