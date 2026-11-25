from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Literal
import jwt
from passlib.context import CryptContext
from .config import settings
from .exceptions import UnauthorizedException
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TokenType = Literal["access", "refresh"]

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def _create_token(subject: str | int, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta
    }

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_access_token(subject: str | int, expires_delta: Optional[timedelta] = None):
    delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(subject, token_type="access", expires_delta=delta)

def create_refresh_token(subject: str | int, expires_delta: Optional[timedelta] = None):
    delta = expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(subject, token_type="refresh", expires_delta=delta)

def decode_token(token: str, expected_type: TokenType = "access") -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("sub") is None:
            raise UnauthorizedException(message="Unauthorized.")

        if payload.get("type") != expected_type:
            raise UnauthorizedException(message=f"Invalid token type (Needed {expected_type} token)")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(message="Session login has expired. Please login again." 
                                    if expected_type == "refresh"
                                    else "Access Token expired.")
    except jwt.InvalidTokenError:
        raise UnauthorizedException(message="Invalid Token.")

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()    
    
