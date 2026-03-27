import logging

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


def get_current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer),db: Session = Depends(get_db)) -> User:
    if not creds or creds.scheme.lower() != "bearer":
        logger.warning("Authentication failed: missing or invalid bearer token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Missing or invalid bearer token")

    try:
        claims = decode_token(creds.credentials)
    except JWTError:
        logger.warning("Authentication failed: invalid or expired JWT")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid or expired token")

    sub = claims.get("sub")
    if not sub:
        logger.warning("Authentication failed: JWT subject claim missing")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        logger.warning(
            "Authentication failed: JWT subject claim not an integer: sub=%s",sub)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

    token_version = claims.get("token_version", 0)
    try:
        token_version = int(token_version)
    except (TypeError, ValueError):
        logger.warning("Authentication failed: invalid token version claim")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

    user = get_user_by_id(db, user_id)
    if not user:
        logger.warning("Authentication failed: unknown user_id=%s", user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

    if token_version != user.token_version:
        logger.warning(
            "Authentication failed: token version mismatch user_id=%s token_version=%s current_version=%s",
            user_id,
            token_version,
            user.token_version,
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid or expired token")
    
    return user


def require_role(required_role: str):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            logger.warning("Authorization failed: user_id=%s role=%s required_role=%s",current_user.id,current_user.role,required_role)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not enough permissions")
        return current_user

    return checker
