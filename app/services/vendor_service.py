from typing import List, Optional
import re
from sqlalchemy.orm import Session

from app.models.vendor import Vendor

# Basic UPI ID format regex: user@bank
UPI_REGEX = re.compile(r"^[\w.\-_]+@[\w.\-_]+$")


def validate_upi_id(upi_id: str) -> bool:
    """Validates basic format of a UPI ID (payee@bank)."""
    return bool(UPI_REGEX.match(upi_id.strip()))


def get_vendors(db: Session, active_only: bool = False) -> List[Vendor]:
    """Retrieve all vendors, optionally filtering by active status."""
    query = db.query(Vendor)
    if active_only:
        query = query.filter(Vendor.is_active.is_(True))
    return query.order_by(Vendor.name.asc()).all()


def get_vendor_by_id(db: Session, vendor_id: int) -> Optional[Vendor]:
    """Retrieve a vendor by primary key."""
    return db.query(Vendor).filter(Vendor.id == vendor_id).first()


def create_vendor(
    db: Session,
    name: str,
    category: str,
    description: Optional[str],
    upi_id: str,
    qr_image_path: Optional[str] = None,
    is_active: bool = True,
) -> Vendor:
    """Creates a new campus vendor record."""
    clean_name = name.strip()
    clean_category = category.strip()
    clean_upi = upi_id.strip().lower()

    if not clean_name:
        raise ValueError("Vendor name cannot be empty")
    if not clean_category:
        raise ValueError("Vendor category cannot be empty")
    if not validate_upi_id(clean_upi):
        raise ValueError("Invalid UPI ID format (must be handle@provider, e.g. canteen@okhdfcbank)")

    vendor = Vendor(
        name=clean_name,
        category=clean_category,
        description=description.strip() if description else None,
        upi_id=clean_upi,
        qr_image_path=qr_image_path.strip() if qr_image_path else None,
        is_active=is_active,
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


def update_vendor(
    db: Session,
    vendor_id: int,
    name: str,
    category: str,
    description: Optional[str],
    upi_id: str,
    is_active: bool,
    qr_image_path: Optional[str] = None,
) -> Optional[Vendor]:
    """Updates an existing vendor's details."""
    vendor = get_vendor_by_id(db, vendor_id)
    if not vendor:
        return None

    clean_name = name.strip()
    clean_category = category.strip()
    clean_upi = upi_id.strip().lower()

    if not clean_name:
        raise ValueError("Vendor name cannot be empty")
    if not clean_category:
        raise ValueError("Vendor category cannot be empty")
    if not validate_upi_id(clean_upi):
        raise ValueError("Invalid UPI ID format (must be handle@provider)")

    vendor.name = clean_name
    vendor.category = clean_category
    vendor.description = description.strip() if description else None
    vendor.upi_id = clean_upi
    vendor.is_active = is_active
    if qr_image_path is not None:
        vendor.qr_image_path = qr_image_path.strip() if qr_image_path else None

    db.commit()
    db.refresh(vendor)
    return vendor


def toggle_vendor_status(db: Session, vendor_id: int) -> Optional[Vendor]:
    """Toggles a vendor's active/inactive status."""
    vendor = get_vendor_by_id(db, vendor_id)
    if not vendor:
        return None

    vendor.is_active = not vendor.is_active
    db.commit()
    db.refresh(vendor)
    return vendor
