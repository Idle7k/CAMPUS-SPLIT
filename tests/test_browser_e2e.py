import socket
import threading
import time
import pytest
import uvicorn
from playwright.sync_api import sync_playwright

from app.database import Base, SessionLocal
from app.main import app
from app.models.user import User, UserRole
from app.models.vendor import Vendor
from app.services.auth_service import hash_password


def get_free_port():
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def live_server():
    """Spins up a lightweight uvicorn instance on localhost for browser testing."""
    port = get_free_port()
    config = uvicorn.Config(app=app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config=config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for server to start accepting connections
    base_url = f"http://127.0.0.1:{port}"
    timeout = 10
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                break
        except (OSError, ConnectionRefusedError):
            time.sleep(0.1)

    # Ensure admin user and demo vendors exist in main DB for e2e
    db = SessionLocal()
    try:
        admin = db.query(User).filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin)

        student = db.query(User).filter_by(username="aarav").first()
        if not student:
            student = User(
                username="aarav",
                password_hash=hash_password("student123"),
                role=UserRole.STUDENT,
                is_active=True,
            )
            db.add(student)

        vendor = db.query(Vendor).first()
        if not vendor:
            vendor = Vendor(
                name="E2E Campus Canteen",
                category="Food & Dining",
                description="Live browser test merchant",
                upi_id="e2ecanteen@okhdfcbank",
                is_active=True,
            )
            db.add(vendor)
        db.commit()
    finally:
        db.close()

    yield base_url
    server.should_exit = True


def test_browser_login_and_vendor_directory(live_server):
    """
    Playwright Browser Test:
    1. Loads the login page.
    2. Submits login form with admin credentials.
    3. Verifies redirect to Dashboard.
    4. Navigates to Campus Vendors directory.
    5. Navigates to Administrator Vendor Console.
    6. Verifies logout journey.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Unauthenticated root redirects to /login
        page.goto(f"{live_server}/")
        page.wait_for_url("**/login")
        assert "Sign In" in page.title()

        # 2. Fill login form
        page.fill("#username", "admin")
        page.fill("#password", "admin123")
        page.click("button[type='submit']")

        # 3. Verify Dashboard
        page.wait_for_url("**/dashboard")
        assert "Dashboard" in page.title()
        assert page.locator("text=System Foundation Ready").is_visible()

        # 4. Navigate to Campus Vendors
        page.click("a[href='/vendors']")
        page.wait_for_url("**/vendors")
        assert "Campus Vendors" in page.title()
        assert page.locator("text=Official Campus Directory").is_visible()

        # 5. Navigate to Admin Vendor Console
        page.click("a[href='/admin/vendors']")
        page.wait_for_url("**/admin/vendors")
        assert page.locator("text=Administrator Restricted").is_visible()

        # 6. Logout
        page.click("button[title='Sign out']")
        page.wait_for_url("**/login")
        assert "Sign In" in page.title()

        browser.close()
