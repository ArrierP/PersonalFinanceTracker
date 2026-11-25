from typing import Any, Dict, Generator
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymysql.connections import Connection

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.db.pool import get_pool

security_schema = HTTPBearer(auto_error=False)

def get_db() -> Generator[Connection, None, None]:
    conn = get_pool().connection()
    try:
        yield conn
    finally:
        conn.close()

def get_current_user(
        creadentials: HTTPAuthorizationCredentials = Depends(security_schema),
        conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    if creadentials is None or creadentials.schema.lower() != 'bearer':
        raise UnauthorizedException(message="Empty bearer token in header Authorization.")

    payload = decode_token(creadentials.credentials, expected_type="access")
    user_id = int(payload["sub"])

    with conn.cursor() as cursor:
        cursor.execute(
            "select id, email, full_name, created_at from users where id = %s",
            (user_id,),
        )
        user = cursor.fetchone()


    if not user:
        raise UnauthorizedException(message="Account not found or deleted.")

    return user