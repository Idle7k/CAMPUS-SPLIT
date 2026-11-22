from app.routers.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router
from app.routers.vendors import router as vendors_router
from app.routers.admin_vendors import router as admin_vendors_router

__all__ = [
    "auth_router",
    "dashboard_router",
    "vendors_router",
    "admin_vendors_router",
]
