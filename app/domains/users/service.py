from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.domains.users.model import User
from app.domains.users.schema import UserCreate


def _normalize_email(email: str) -> str:
    return email.lower().strip()


def _normalize_username(username: str) -> str:
    return username.lower().strip()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == _normalize_email(email)).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == _normalize_username(username)).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    normalized_name = user_data.name.strip()
    normalized_username = _normalize_username(user_data.username)
    normalized_email = _normalize_email(user_data.email)

    if not normalized_name:
        raise ValueError("Name must not be blank")
    if not normalized_username:
        raise ValueError("Username must not be blank")
    if len(normalized_username) < 3:
        raise ValueError("Username must be at least 3 characters")

    existing_user = db.query(User).filter(
        or_(
            User.email == normalized_email,
            User.username == normalized_username,
        )
    ).first()
    if existing_user:
        if existing_user.email == normalized_email:
            raise ValueError("Email already registered")
        raise ValueError("Username already taken")

    user = User(
        name=normalized_name,
        username=normalized_username,
        email=normalized_email,
        password_hash=hash_password(user_data.password),
        role="buyer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user and verify_password(password, user.password_hash):
        return user
    return None
