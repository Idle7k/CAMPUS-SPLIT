import secrets
from typing import Optional
from fastapi import Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import get_user_by_id


def get_csrf_token(request: Request) -> str:
    """Retrieves or generates a CSRF token stored in the user's session."""
    token = request.session.get("csrf_token")
    if not token:
        token = secrets.token_hex(16)
        request.session["csrf_token"] = token
    return token


def verify_csrf_token(request: Request, csrf_token: Optional[str]) -> bool:
    """Verifies that the submitted CSRF token matches the session token."""
    expected = request.session.get("csrf_token")
    if not expected or not csrf_token:
        return False
    return secrets.compare_digest(expected, csrf_token)


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Retrieves the authenticated user from the session if present, else None."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        request.session.clear()
        return None
    return user


def require_authenticated_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Enforces authentication.
    Redirects HTML browsers to /login, or raises 401 for API/HTMX clients.
    """
    user = get_current_user_optional(request, db)
    if not user:
        if request.headers.get("HX-Request"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"HX-Redirect": "/login"},
            )
        # Browser navigation redirect
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )
    return user


def require_admin(
    request: Request,
    user: User = Depends(require_authenticated_user),
) -> User:
    """
    Enforces administrator authorization.
    Rejects non-admin users with 403 Forbidden.
    """
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Administrator access required.",
        )
    return user
