from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.dependencies import get_current_user_optional, get_csrf_token
from app.routers import (
    auth_router,
    dashboard_router,
    vendors_router,
    admin_vendors_router,
)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Campus Split",
    description="Campus-focused direct vendor payment splitting and debt tracking prototype.",
    version="0.1.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# 1. Mount Static Assets
static_path = BASE_DIR / "static"
static_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# 2. Configure Jinja2 Templates
templates_path = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(templates_path))
app.state.templates = templates

# 3. Add Session Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE_NAME,
    max_age=settings.SESSION_MAX_AGE,
    same_site="lax",
    https_only=False,  # Localhost development
)


# 4. Custom Exception Handlers for Web Presentation
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    # Handle redirect signals (such as 303 to login)
    if exc.status_code == status.HTTP_303_SEE_OTHER:
        location = exc.headers.get("Location", "/login") if exc.headers else "/login"
        return RedirectResponse(url=location, status_code=status.HTTP_303_SEE_OTHER)

    # Differentiate between browser page loads and API/HTMX calls
    accept_header = request.headers.get("accept", "")
    is_html_request = "text/html" in accept_header or not accept_header

    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        if is_html_request:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        return JSONResponse(status_code=401, content={"detail": exc.detail})

    if exc.status_code == status.HTTP_403_FORBIDDEN:
        if is_html_request:
            current_user = None
            try:
                from app.database import SessionLocal
                with SessionLocal() as db:
                    current_user = get_current_user_optional(request, db)
            except Exception:
                pass
            return templates.TemplateResponse(
                request=request,
                name="errors/403.html",
                context={
                    "detail": exc.detail,
                    "current_user": current_user,
                    "csrf_token": get_csrf_token(request),
                },
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return JSONResponse(status_code=403, content={"detail": exc.detail})

    if exc.status_code == status.HTTP_404_NOT_FOUND:
        if is_html_request:
            current_user = None
            try:
                from app.database import SessionLocal
                with SessionLocal() as db:
                    current_user = get_current_user_optional(request, db)
            except Exception:
                pass
            return templates.TemplateResponse(
                request=request,
                name="errors/404.html",
                context={
                    "detail": exc.detail,
                    "current_user": current_user,
                    "csrf_token": get_csrf_token(request),
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return JSONResponse(status_code=404, content={"detail": exc.detail})

    # Default fallback
    if is_html_request:
        return HTMLResponse(content=f"Error {exc.status_code}: {exc.detail}", status_code=exc.status_code)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# 5. Include Application Routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(vendors_router)
app.include_router(admin_vendors_router)
