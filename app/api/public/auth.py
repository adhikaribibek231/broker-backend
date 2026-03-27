import logging

from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import Session

from app.utils.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token
from app.domains.users.model import User
from app.domains.users.schema import UserCreate, UserLogin, UserResponse
from app.domains.users.service import get_user_by_id, create_user, authenticate_user
from app.domains.auth.schema import RefreshTokenIn, TokenPairResponse
from app.domains.auth.service import find_refresh_token, is_refresh_token_valid, issue_refresh_token, rotate_refresh_token,revoke_refresh_token

router= APIRouter(prefix="/auth", tags = ["public auth"])
logger = logging.getLogger(__name__)

@router.post("/register", response_model = UserResponse, status_code= status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db))-> User:
    logger.info("Registration attempt: email = %s username=%s", payload.email, payload.username)

    try:
        user = create_user(db, payload)
    except ValueError as exc:
        logger.warning("Registration failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail = str(exc))
    
    logger.info("Registration successful: user_id=%s email=%s", user.id, user.email)
    return user


@router.post("/login", response_model=TokenPairResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenPairResponse:
    logger.info("Login attempt: email=%s", payload.email)

    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        logger.warning("Login failed: invalid credentials for email=%s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,detail="Bad credentials")

    access_token = create_access_token(sub=str(user.id),
                                       claims={"role": user.role,
                                               "email": user.email
                                               })
    refresh_token = issue_refresh_token(db, user.id)

    logger.info("Login successful: user_id=%s", user.id)
    return TokenPairResponse(access_token=access_token,refresh_token=refresh_token,token_type="bearer")


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(payload: RefreshTokenIn, db: Session = Depends(get_db)) -> TokenPairResponse:
    logger.debug("Refresh token request received")

    row = find_refresh_token(db, payload.refresh_token)
    if not row or not is_refresh_token_valid(row):
        logger.warning("Refresh failed: invalid refresh token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid refresh token")

    user = get_user_by_id(db, row.user_id)
    if not user:
        logger.warning("Refresh failed: unknown user_id=%s", row.user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid refresh token")

    new_access_token = create_access_token(sub=str(user.id),
                                           claims={
                                               "role": user.role,
                                               "email": user.email
                                               })
    
    new_refresh_token = rotate_refresh_token(db, row)

    logger.info("Refresh successful: user_id=%s", user.id)
    return TokenPairResponse(access_token=new_access_token,refresh_token=new_refresh_token,token_type="bearer")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshTokenIn, db: Session = Depends(get_db)) -> Response:
    logger.debug("Logout request received")

    row = find_refresh_token(db, payload.refresh_token)
    if row and is_refresh_token_valid(row):
        revoke_refresh_token(db, row)
        logger.info("Logout successful: user_id=%s", row.user_id)
    else:
        logger.debug("Logout skipped: token not found or already invalid")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

