from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from jose import jwt
from pwdlib import PasswordHash
from app.core.config import settings

def create_access_token(*, sub: str, claims: dict | None =None)->str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp":int((now+timedelta(minutes=settings.access_token_expire_minutes)).timestamp())
    }
    if claims:
        payload.update(claims)

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=[settings.jwt_algorithm])

def decode_token(token:str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

_pwd = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return _pwd.hash(password)

def verify_password(password:str, password_hash: str) -> bool:
    return _pwd.verify(password, password_hash)

def generate_refresh_token() ->str:
    return secrets.token_urlsafe(48)

def hash_refresh_token(raw_token:str)-> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

def refresh_expires_at()->datetime:
    return datetime.now(timezone.utc) + timedelta(days = settings.refresh_token_expire_days)