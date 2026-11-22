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


def test_responsive_layouts_desktop_and_mobile(live_server):
    """
    Test responsive layouts at specified viewports:
    - Desktop: 1440x900 (sidebar visible, mobile nav hidden, no overflow)
    - Mobile: 390x844 (sidebar hidden, mobile nav visible, mobile bottom nav active)
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # ── 1. Desktop Viewport (1440 x 900) ─────────────────────────
        desktop_page = browser.new_page(viewport={"width": 1440, "height": 900})
        desktop_page.goto(f"{live_server}/login")
        desktop_page.fill("#username", "admin")
        desktop_page.fill("#password", "admin123")
        desktop_page.click("button[type='submit']")
        desktop_page.wait_for_url("**/dashboard")

        # Sidebar must be visible on desktop
        assert desktop_page.locator("aside").is_visible()
        # Mobile bottom navigation must be hidden on desktop
        assert not desktop_page.locator("nav.md\\:hidden").is_visible()

        # Check navigation to Balances & Expenses
        desktop_page.click("a[href='/balances']")
        desktop_page.wait_for_url("**/balances")
        assert "Balances" in desktop_page.title()

        desktop_page.click("a[href='/expenses']")
        desktop_page.wait_for_url("**/expenses")
        assert "Expenses" in desktop_page.title()

        # Verify no horizontal scroll overflow on desktop
        scroll_width = desktop_page.evaluate("document.documentElement.scrollWidth")
        client_width = desktop_page.evaluate("document.documentElement.clientWidth")
        assert scroll_width <= client_width

        desktop_page.close()

        # ── 2. Mobile Viewport (390 x 844) ───────────────────────────
        mobile_page = browser.new_page(viewport={"width": 390, "height": 844})
        mobile_page.goto(f"{live_server}/login")
        mobile_page.fill("#username", "admin")
        mobile_page.fill("#password", "admin123")
        mobile_page.click("button[type='submit']")
        mobile_page.wait_for_url("**/dashboard")

        # Desktop sidebar should NOT be visible
        assert not mobile_page.locator("aside").is_visible()
        # Mobile top header and bottom nav must be visible
        assert mobile_page.locator("header.md\\:hidden").is_visible()
        assert mobile_page.locator("nav.md\\:hidden").is_visible()

        # Navigate using mobile bottom navigation to Vendors
        mobile_page.locator("nav.md\\:hidden a[href='/vendors']").click()
        mobile_page.wait_for_url("**/vendors")
        assert "Vendors" in mobile_page.title()

        # Verify no horizontal scroll overflow on mobile
        m_scroll_width = mobile_page.evaluate("document.documentElement.scrollWidth")
        m_client_width = mobile_page.evaluate("document.documentElement.clientWidth")
        assert m_scroll_width <= m_client_width

        mobile_page.close()
        browser.close()
