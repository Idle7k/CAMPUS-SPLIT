from typing import Optional
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from sqlalchemy.orm import Session

from app.models.user import User, UserRole

# Modern Argon2id hasher
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hashes a plaintext password using Argon2id."""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against an Argon2id hash."""
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Retrieve user by username (case-insensitive lookup)."""
    return db.query(User).filter(User.username.ilike(username.strip())).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Retrieve user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def register_user(
    db: Session,
    username: str,
    password: str,
    role: UserRole = UserRole.STUDENT,
) -> User:
    """
    Registers a new user account.
    Enforces uniqueness and securely hashes the password.
    """
    clean_username = username.strip()
    if not clean_username:
        raise ValueError("Username cannot be empty")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters")

    existing = get_user_by_username(db, clean_username)
    if existing:
        raise ValueError(f"Username '{clean_username}' is already taken")

    hashed = hash_password(password)
    user = User(
        username=clean_username,
        password_hash=hashed,
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(
    db: Session,
    username: str,
    password: str,
) -> Optional[User]:
    """
    Authenticates a user by username and password.
    Returns the User object on success, or None on failure.
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
