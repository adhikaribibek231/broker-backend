from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session

from app.core.security import generate_refresh_token, hash_refresh_token, refresh_expires_at
from app.domains.auth.model import RefreshToken

logger = logging.getLogger(__name__)


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
    h = hash_refresh_token(raw_token)
    row = db.query(RefreshToken).filter(RefreshToken.token_hash == h).one_or_none()
    if row is None:
        logger.debug("Refresh token lookup miss")
    return row

def is_refresh_token_valid(row: RefreshToken) -> bool:
    if row.revoked:
        logger.debug("Refresh token invalid: revoked token_id=%s user_id=%s", row.id, row.user_id)
        return False
    if row.expires_at <= datetime.now(timezone.utc):
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

def revoke_refresh_token(db: Session, row: RefreshToken) -> None:
    if row.revoked:
        logger.debug("Refresh token already revoked: token_id=%s user_id=%s", row.id, row.user_id)
        return
    row.revoked = True
    db.commit()
    logger.info("Refresh token revoked: token_id=%s user_id=%s", row.id, row.user_id)