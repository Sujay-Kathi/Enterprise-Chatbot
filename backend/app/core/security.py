"""JWT generation, OTP management, and password hashing utilities."""

import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory OTP store: { email: (otp, expiry_datetime) }
_otp_store: dict[str, tuple[str, datetime]] = {}


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── OTP helpers ───────────────────────────────────────────────────────────────

def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def store_otp(email: str, otp: str) -> None:
    expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.otp_expire_minutes)
    _otp_store[email] = (otp, expiry)


def verify_otp(email: str, otp: str) -> bool:
    """Return True if the OTP is correct and not expired."""
    entry = _otp_store.get(email)
    if not entry:
        return False
    stored_otp, expiry = entry
    if datetime.now(timezone.utc) > expiry:
        _otp_store.pop(email, None)
        return False
    if stored_otp != otp:
        return False
    _otp_store.pop(email, None)  # single-use
    return True


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Optional[str]:
    """Decode JWT and return the 'sub' claim, or None if invalid/expired."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload.get("sub")
    except JWTError:
        return None
