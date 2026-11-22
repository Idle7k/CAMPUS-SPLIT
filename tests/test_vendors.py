import pytest
from app.models.vendor import Vendor
from app.services import vendor_service
from tests.conftest import get_form_csrf_token


def test_vendor_service_crud(db_session):
    """Test vendor service creation, update, and retrieval."""
    # 1. Create
    vendor = vendor_service.create_vendor(
        db=db_session,
        name="Chemistry Lab Supplies",
        category="Stationery & Lab",
        description="Lab coats and test tubes",
        upi_id="chemlab@oksbi",
        is_active=True,
    )
    assert vendor.id is not None
    assert vendor.name == "Chemistry Lab Supplies"
    assert vendor.is_active is True

    # 2. Update
    updated = vendor_service.update_vendor(
        db=db_session,
        vendor_id=vendor.id,
        name="Chemistry & Biology Lab Store",
        category="Lab Essentials",
        description="Full science consumables",
        upi_id="chembio@oksbi",
        is_active=True,
    )
    assert updated.name == "Chemistry & Biology Lab Store"
    assert updated.upi_id == "chembio@oksbi"

    # 3. Toggle Status
    toggled = vendor_service.toggle_vendor_status(db_session, vendor.id)
    assert toggled.is_active is False

    toggled_again = vendor_service.toggle_vendor_status(db_session, vendor.id)
    assert toggled_again.is_active is True


def test_vendor_upi_validation(db_session):
    """Test that invalid UPI IDs are rejected."""
    # Valid
    assert vendor_service.validate_upi_id("vendor@upi") is True
    assert vendor_service.validate_upi_id("john.doe@okaxis") is True

    # Invalid
    assert vendor_service.validate_upi_id("invalid-upi-no-at-symbol") is False
    assert vendor_service.validate_upi_id("@nobank") is False
    assert vendor_service.validate_upi_id("no_user@") is False

    with pytest.raises(ValueError, match="Invalid UPI ID format"):
        vendor_service.create_vendor(
            db=db_session,
            name="Bad Vendor",
            category="Dining",
            description=None,
            upi_id="invalid_upi_format",
        )


def test_vendor_directory_filters_inactive(db_session):
    """Ensure active_only=True returns only active vendors."""
    v1 = vendor_service.create_vendor(db_session, "Active 1", "Cat", None, "v1@upi", is_active=True)
    v2 = vendor_service.create_vendor(db_session, "Inactive 2", "Cat", None, "v2@upi", is_active=False)

    active_list = vendor_service.get_vendors(db_session, active_only=True)
    all_list = vendor_service.get_vendors(db_session, active_only=False)

    active_ids = [v.id for v in active_list]
    assert v1.id in active_ids
    assert v2.id not in active_ids
    assert len(all_list) >= len(active_list) + 1


def test_admin_create_vendor_http(authenticated_admin_client, db_session):
    """Test administrator creating a vendor via HTTP POST."""
    csrf_token = get_form_csrf_token(authenticated_admin_client, "/admin/vendors/new")
    response = authenticated_admin_client.post(
        "/admin/vendors/new",
        data={
            "name": "Hostel 3 Mess",
            "category": "Food & Dining",
            "upi_id": "hostel3mess@okaxis",
            "description": "Daily student dining hall",
            "is_active": "true",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["Location"] == "/admin/vendors"

    # Verify vendor exists in database
    vendor = db_session.query(Vendor).filter_by(name="Hostel 3 Mess").first()
    assert vendor is not None
    assert vendor.upi_id == "hostel3mess@okaxis"


def test_admin_update_vendor_http(authenticated_admin_client, test_vendor, db_session):
    """Test administrator updating a vendor via HTTP POST."""
    csrf_token = get_form_csrf_token(authenticated_admin_client, f"/admin/vendors/{test_vendor.id}/edit")
    response = authenticated_admin_client.post(
        f"/admin/vendors/{test_vendor.id}/edit",
        data={
            "name": "Updated Canteen Express",
            "category": "Fast Food",
            "upi_id": "updatedcanteen@okhdfcbank",
            "description": "Renovated cafeteria",
            "is_active": "true",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["Location"] == "/admin/vendors"

    db_session.refresh(test_vendor)
    assert test_vendor.name == "Updated Canteen Express"
    assert test_vendor.category == "Fast Food"


def test_admin_toggle_vendor_http(authenticated_admin_client, test_vendor, db_session):
    """Test administrator toggling vendor active status via HTTP POST."""
    initial_status = test_vendor.is_active

    csrf_token = get_form_csrf_token(authenticated_admin_client, "/admin/vendors")
    response = authenticated_admin_client.post(
        f"/admin/vendors/{test_vendor.id}/toggle",
        data={"csrf_token": csrf_token},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["Location"] == "/admin/vendors"

    db_session.refresh(test_vendor)
    assert test_vendor.is_active is not initial_status


def test_student_view_vendor_details(authenticated_student_client, test_vendor):
    """Test student viewing a vendor's profile page."""
    response = authenticated_student_client.get(f"/vendors/{test_vendor.id}")
    assert response.status_code == 200
    assert test_vendor.name in response.text
    assert test_vendor.upi_id in response.text
