"""Seed script to populate initial demo accounts and campus vendors.
Idempotent: safe to run multiple times.
"""
from app.config import settings
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.vendor import Vendor
from app.services.auth_service import hash_password

SAMPLE_VENDORS = [
    {
        "name": "Campus Canteen",
        "category": "Food & Dining",
        "description": "Main campus cafeteria serving daily meals, dosas, thalis, and quick snacks.",
        "upi_id": "campus.canteen@okhdfcbank",
        "is_active": True,
    },
    {
        "name": "Tech Park Stationery & Xerox",
        "category": "Printing & Supplies",
        "description": "Photocopies, project spiral binding, lab manuals, and academic stationery.",
        "upi_id": "techpark.xerox@oksbi",
        "is_active": True,
    },
    {
        "name": "Night Mess Canteen",
        "category": "Food & Dining",
        "description": "Late-night student mess serving hot chai, maggi, egg rolls, and parathas until 2 AM.",
        "upi_id": "nightmess@icici",
        "is_active": True,
    },
    {
        "name": "Hostel Express Laundry",
        "category": "Laundry & Services",
        "description": "Weekly laundry wash, fold, dry clean, and steam pressing for campus residents.",
        "upi_id": "hostel.laundry@paytm",
        "is_active": True,
    },
    {
        "name": "Department Coffee Co.",
        "category": "Beverages & Cafe",
        "description": "Specialty filter coffee, cold brew, artisanal tea, and fresh bakery pastries.",
        "upi_id": "deptcoffee@axl",
        "is_active": True,
    },
    {
        "name": "Campus Medical & Wellness",
        "category": "Healthcare & Essentials",
        "description": "First-aid supplies, OTC pharmaceuticals, and general healthcare essentials.",
        "upi_id": "campuswellness@ybl",
        "is_active": False,  # Demo inactive vendor for testing admin toggle
    },
]

DEMO_USERS = [
    {
        "username": settings.ADMIN_USERNAME,
        "password": settings.ADMIN_PASSWORD,
        "role": UserRole.ADMIN,
    },
    {
        "username": "aarav",
        "password": settings.STUDENT_DEFAULT_PASSWORD,
        "role": UserRole.STUDENT,
    },
    {
        "username": "diya",
        "password": settings.STUDENT_DEFAULT_PASSWORD,
        "role": UserRole.STUDENT,
    },
    {
        "username": "rohan",
        "password": settings.STUDENT_DEFAULT_PASSWORD,
        "role": UserRole.STUDENT,
    },
]


def seed_database():
    db = SessionLocal()
    try:
        print("--- Seeding Campus Split Database ---")
        
        # 1. Seed Users
        for user_data in DEMO_USERS:
            existing = db.query(User).filter(User.username.ilike(user_data["username"])).first()
            if not existing:
                user = User(
                    username=user_data["username"],
                    password_hash=hash_password(user_data["password"]),
                    role=user_data["role"],
                    is_active=True,
                )
                db.add(user)
                print(f"Created demo {user_data['role'].value} account: {user_data['username']}")
            else:
                print(f"User '{user_data['username']}' already exists.")

        # 2. Seed Vendors
        for vendor_data in SAMPLE_VENDORS:
            existing = db.query(Vendor).filter(Vendor.name == vendor_data["name"]).first()
            if not existing:
                vendor = Vendor(
                    name=vendor_data["name"],
                    category=vendor_data["category"],
                    description=vendor_data["description"],
                    upi_id=vendor_data["upi_id"],
                    is_active=vendor_data["is_active"],
                )
                db.add(vendor)
                status_str = "active" if vendor_data["is_active"] else "inactive"
                print(f"Created vendor: {vendor_data['name']} ({status_str})")
            else:
                print(f"Vendor '{vendor_data['name']}' already exists.")

        db.commit()
        print("--- Seeding Complete Successfully ---")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
