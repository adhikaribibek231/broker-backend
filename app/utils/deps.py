import logging
from typing import NoReturn

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.domains.users.model import User
from app.domains.users.service import get_user_by_id

bearer = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


def _auth_failed(detail: str, message: str, *args: object) -> NoReturn:
    logger.warning(message, *args)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not creds or creds.scheme.lower() != "bearer":
        _auth_failed("Missing or invalid bearer token", "Authentication failed: missing or invalid bearer token")

    try:
        claims = decode_token(creds.credentials)
    except JWTError:
        _auth_failed("Invalid or expired token", "Authentication failed: invalid or expired JWT")

    sub = claims.get("sub")
    if not sub:
        _auth_failed("Invalid token", "Authentication failed: JWT subject claim missing")

    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        _auth_failed("Invalid token", "Authentication failed: JWT subject claim not an integer: sub=%s", sub)

    token_version = claims.get("token_version", 0)
    try:
        token_version = int(token_version)
    except (TypeError, ValueError):
        _auth_failed("Invalid token", "Authentication failed: invalid token version claim")

    user = get_user_by_id(db, user_id)
    if not user:
        _auth_failed("Invalid token", "Authentication failed: unknown user_id=%s", user_id)

    if token_version != user.token_version:
        _auth_failed(
            "Invalid or expired token",
            "Authentication failed: token version mismatch user_id=%s token_version=%s current_version=%s",
            user_id,
            token_version,
            user.token_version,
        )

    return user


def require_role(required_role: str):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            logger.warning(
                "Authorization failed: user_id=%s role=%s required_role=%s",
                current_user.id,
                current_user.role,
                required_role,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return current_user

    return checker
