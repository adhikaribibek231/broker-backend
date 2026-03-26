from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.domains.users.model import User
from app.domains.users.schema import UserCreate
from app.core.security import hash_password, verify_password


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    normalized_email = email.lower().strip()
    return db.query(User).filter(User.email == normalized_email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    normalized_username = username.strip()
    return db.query(User).filter(User.username == normalized_username).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    normalized_name = user_data.name.strip()
    normalized_username = user_data.username.strip()
    normalized_email = user_data.email.lower().strip()

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

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user