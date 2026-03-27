import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    refresh_expires_at,
)
from app.domains.auth.model import RefreshToken
from app.domains.users.model import User
from app.domains.users.service import get_user_by_id

logger = logging.getLogger(__name__)


def issue_access_token(user: User) -> str:
    return create_access_token(
        sub=str(user.id),
        claims={
            "role": user.role,
            "email": user.email,
            "token_version": user.token_version,
        },
    )


def issue_refresh_token(db: Session, user_id: int) -> str:
    logger.debug("Issuing refresh token: user_id=%s", user_id)
    raw = generate_refresh_token()
    row = RefreshToken(
        user_id=user_id,
        token_hash=hash_refresh_token(raw),
        revoked=False,
        replaced_by_hash=None,
        created_at=datetime.now(timezone.utc),
        expires_at=refresh_expires_at(),
    )
    db.add(row)
    db.commit()
    logger.info("Refresh token issued: user_id=%s token_id=%s", user_id, row.id)
    return raw


def find_refresh_token(db: Session, raw_token: str) -> RefreshToken | None:
    row = db.query(RefreshToken).filter(RefreshToken.token_hash == hash_refresh_token(raw_token)).one_or_none()
    if row is None:
        logger.debug("Refresh token lookup miss")
    return row


def get_active_refresh_session(db: Session, raw_token: str) -> tuple[RefreshToken, User] | None:
    row = find_refresh_token(db, raw_token)
    if row is None or not is_refresh_token_valid(row):
        return None

    user = get_user_by_id(db, row.user_id)
    if user is None:
        logger.warning("Refresh token orphaned: token_id=%s user_id=%s", row.id, row.user_id)
        return None

    return row, user


def is_refresh_token_valid(row: RefreshToken) -> bool:
    if row.revoked:
        logger.debug("Refresh token invalid: revoked token_id=%s user_id=%s", row.id, row.user_id)
        return False

    expires_at = row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= datetime.now(timezone.utc):
        logger.debug("Refresh token invalid: expired token_id=%s user_id=%s", row.id, row.user_id)
        return False
    return True


def rotate_refresh_token(db: Session, row: RefreshToken) -> str:
    logger.info("Rotating refresh token: token_id=%s user_id=%s", row.id, row.user_id)
    new_raw = generate_refresh_token()
    new_hash = hash_refresh_token(new_raw)

    row.revoked = True
    row.replaced_by_hash = new_hash

    new_row = RefreshToken(
        user_id=row.user_id,
        token_hash=new_hash,
        revoked=False,
        replaced_by_hash=None,
        created_at=datetime.now(timezone.utc),
        expires_at=refresh_expires_at(),
    )
    db.add(new_row)
    db.commit()
    logger.info(
        "Refresh token rotated: old_token_id=%s new_token_id=%s user_id=%s",
        row.id,
        new_row.id,
        row.user_id,
    )
    return new_raw


def revoke_user_session(db: Session, row: RefreshToken, user: User) -> None:
    user.token_version += 1
    row.revoked = True
    db.commit()
    logger.info("Refresh token revoked: token_id=%s user_id=%s", row.id, row.user_id)
