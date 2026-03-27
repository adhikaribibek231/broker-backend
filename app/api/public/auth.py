import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import MessageResponse
from app.domains.auth.model import RefreshToken
from app.domains.auth.schema import RefreshTokenIn, TokenPairResponse
from app.domains.auth.service import (
    get_active_refresh_session,
    issue_access_token,
    issue_refresh_token,
    revoke_user_session,
    rotate_refresh_token,
)
from app.domains.users.model import User
from app.domains.users.schema import UserCreate, UserLogin, UserResponse
from app.domains.users.service import authenticate_user, create_user
from app.utils.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["public auth"])
logger = logging.getLogger(__name__)


def _get_refresh_session_or_401(
    db: Session,
    raw_token: str,
) -> tuple[RefreshToken, User]:
    session = get_active_refresh_session(db, raw_token)
    if session is None:
        logger.warning("Auth failed: invalid refresh token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    return session


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    logger.info("Registration attempt: email=%s username=%s", payload.email, payload.username)
    try:
        user = create_user(db, payload)
    except ValueError as exc:
        logger.warning("Registration failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    logger.info("Registration successful: user_id=%s email=%s", user.id, user.email)
    return user


@router.post("/login", response_model=TokenPairResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenPairResponse:
    logger.info("Login attempt: email=%s", payload.email)
    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        logger.warning("Login failed: invalid credentials for email=%s", payload.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials")

    logger.info("Login successful: user_id=%s", user.id)
    return TokenPairResponse(
        access_token=issue_access_token(user),
        refresh_token=issue_refresh_token(db, user.id),
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(payload: RefreshTokenIn, db: Session = Depends(get_db)) -> TokenPairResponse:
    logger.debug("Refresh token request received")
    row, user = _get_refresh_session_or_401(db, payload.refresh_token)
    logger.info("Refresh successful: user_id=%s", user.id)
    return TokenPairResponse(
        access_token=issue_access_token(user),
        refresh_token=rotate_refresh_token(db, row),
        token_type="bearer",
    )


@router.post("/logout", response_model=MessageResponse)
def logout(payload: RefreshTokenIn, db: Session = Depends(get_db)) -> MessageResponse:
    logger.debug("Logout request received")
    row, user = _get_refresh_session_or_401(db, payload.refresh_token)
    revoke_user_session(db, row, user)
    logger.info("Logout successful: user_id=%s", row.user_id)
    return MessageResponse(detail="Logged out successfully")


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
