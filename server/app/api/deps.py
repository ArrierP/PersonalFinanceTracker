from typing import Any, Dict, Generator
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymysql.connections import Connection

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.db.pool import get_pool
from app.repositories.auth_repo import AuthRepository

security_schema = HTTPBearer(auto_error=False)

def get_db() -> Generator[Connection, None, None]:
    conn = get_pool().connection()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security_schema),
        conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != 'bearer':
        raise UnauthorizedException(message="Empty bearer token in header Authorization.")

    payload = decode_token(credentials.credentials, expected_type="access")
    user_id = int(payload["sub"])

    user = AuthRepository(conn).get_user_by_id(user_id)

    if not user:
        raise UnauthorizedException(message="Account not found or deleted.")

    return user