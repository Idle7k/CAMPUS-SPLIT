import os
import re
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.models.vendor import Vendor
from app.services.auth_service import hash_password

TEST_DB_FILE = "test_campus_split.db"
TEST_DATABASE_URL = f"sqlite:///./{TEST_DB_FILE}"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)


@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    expire_on_commit=False,
    future=True,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test tables at beginning of session, tear down at end."""
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass

    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass


@pytest.fixture(autouse=True)
def clean_tables():
    """Clean all table contents after each test for full test isolation."""
    yield
    with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture
def db_session():
    """Provides a fresh database session per test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """TestClient that uses the isolated test database."""
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def login_user(client: TestClient, username: str, password: str):
    """Helper to perform CSRF-protected form login."""
    resp = client.get("/login")
    match = re.search(r'name="csrf_token" value="([^"]+)"', resp.text)
    csrf_token = match.group(1) if match else ""
    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )


def get_form_csrf_token(client: TestClient, url: str) -> str:
    """Helper to fetch a page and extract its CSRF token."""
    resp = client.get(url)
    match = re.search(r'name="csrf_token" value="([^"]+)"', resp.text)
    return match.group(1) if match else ""


@pytest.fixture
def test_admin_user(db_session) -> User:
    """Creates a test admin user."""
    admin = User(
        username="test_admin",
        password_hash=hash_password("admin_pass123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def test_student_user(db_session) -> User:
    """Creates a test student user."""
    student = User(
        username="test_student",
        password_hash=hash_password("student_pass123"),
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def test_vendor(db_session) -> Vendor:
    """Creates a sample campus vendor."""
    vendor = Vendor(
        name="Test Campus Canteen",
        category="Food & Dining",
        description="Fresh meals and tea for students",
        upi_id="testcanteen@okhdfcbank",
        is_active=True,
    )
    db_session.add(vendor)
    db_session.commit()
    db_session.refresh(vendor)
    return vendor


@pytest.fixture
def authenticated_admin_client(client, test_admin_user):
    """Client authenticated as administrator."""
    login_user(client, test_admin_user.username, "admin_pass123")
    return client


@pytest.fixture
def authenticated_student_client(client, test_student_user):
    """Client authenticated as student."""
    login_user(client, test_student_user.username, "student_pass123")
    return client
