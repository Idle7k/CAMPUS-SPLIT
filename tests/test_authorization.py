def test_unauthenticated_routes_redirect_to_login(client):
    """Unauthenticated access to protected routes must redirect to /login."""
    routes = [
        "/dashboard",
        "/vendors",
        "/admin/vendors",
        "/admin/vendors/new",
    ]
    for route in routes:
        response = client.get(route, follow_redirects=False)
        assert response.status_code == 303, f"Route {route} did not redirect"
        assert response.headers["Location"] == "/login"


def test_student_cannot_access_admin_vendor_list(authenticated_student_client):
    """
    A student must be rejected with 403 Forbidden when attempting to view
    the administrator vendor console.
    """
    response = authenticated_student_client.get("/admin/vendors")
    assert response.status_code == 403
    assert "Administrator access required" in response.text or "403" in response.text


def test_student_cannot_access_admin_vendor_create(authenticated_student_client):
    """A student must be forbidden from opening the admin vendor creation form."""
    response = authenticated_student_client.get("/admin/vendors/new")
    assert response.status_code == 403


def test_student_cannot_post_admin_vendor_create(authenticated_student_client):
    """A student must be forbidden from POSTing to the admin vendor creation endpoint."""
    response = authenticated_student_client.post(
        "/admin/vendors/new",
        data={
            "name": "Unauthorized Vendor",
            "category": "Food",
            "upi_id": "unauth@upi",
            "csrf_token": "dummy",
        },
    )
    assert response.status_code == 403


def test_student_cannot_toggle_vendor_status(authenticated_student_client, test_vendor):
    """A student must be forbidden from toggling vendor active/inactive status."""
    response = authenticated_student_client.post(
        f"/admin/vendors/{test_vendor.id}/toggle",
        data={"csrf_token": "dummy"},
    )
    assert response.status_code == 403


def test_admin_can_access_admin_routes(authenticated_admin_client):
    """An administrator must be permitted to access administrator routes."""
    response = authenticated_admin_client.get("/admin/vendors")
    assert response.status_code == 200
    assert "Campus Vendor Directory Management" in response.text
    assert "Administrator Restricted" in response.text


def test_student_can_access_student_routes(authenticated_student_client):
    """A student must be permitted to access dashboard and vendor directory."""
    resp_dash = authenticated_student_client.get("/dashboard")
    assert resp_dash.status_code == 200
    assert "System Foundation Ready" in resp_dash.text
    assert "Financial Overview" in resp_dash.text

    resp_vendors = authenticated_student_client.get("/vendors")
    assert resp_vendors.status_code == 200
    assert "Official Campus Directory" in resp_vendors.text
