from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_csrf_token, verify_csrf_token, get_current_user_optional
from app.models.user import UserRole
from app.services import auth_service

router = APIRouter(tags=["Authentication"])


@router.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = get_current_user_optional(request, db)
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    templates = request.app.state.templates
    csrf_token = get_csrf_token(request)
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "csrf_token": csrf_token,
            "current_user": None,
        },
    )


@router.post("/login", response_class=HTMLResponse)
def handle_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    templates = request.app.state.templates

    if not verify_csrf_token(request, csrf_token):
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "csrf_token": get_csrf_token(request),
                "error": "Invalid session token. Please try again.",
                "username": username,
                "current_user": None,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user = auth_service.authenticate_user(db, username=username, password=password)
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "csrf_token": get_csrf_token(request),
                "error": "Invalid username or password.",
                "username": username,
                "current_user": None,
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Establish session
    request.session["user_id"] = user.id
    request.session["user_role"] = user.role.value
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/register", response_class=HTMLResponse)
def register_page(
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = get_current_user_optional(request, db)
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    templates = request.app.state.templates
    csrf_token = get_csrf_token(request)
    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={
            "csrf_token": csrf_token,
            "current_user": None,
        },
    )


@router.post("/register", response_class=HTMLResponse)
def handle_register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    role: str = Form("student"),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    templates = request.app.state.templates

    if not verify_csrf_token(request, csrf_token):
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={
                "csrf_token": get_csrf_token(request),
                "error": "Invalid session token. Please try again.",
                "username": username,
                "current_user": None,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={
                "csrf_token": get_csrf_token(request),
                "error": "Passwords do not match.",
                "username": username,
                "current_user": None,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_role = UserRole.ADMIN if role == "admin" else UserRole.STUDENT
        user = auth_service.register_user(
            db,
            username=username,
            password=password,
            role=user_role,
        )
    except ValueError as e:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={
                "csrf_token": get_csrf_token(request),
                "error": str(e),
                "username": username,
                "current_user": None,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Automatically sign in newly registered user
    request.session["user_id"] = user.id
    request.session["user_role"] = user.role.value
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.api_route("/logout", methods=["GET", "POST"])
def logout(request: Request):
    """Clears the session cookie and redirects to /login."""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
