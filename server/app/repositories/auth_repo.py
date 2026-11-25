from datetime import datetime
from typing import Any, Dict, Optional
from pymysql.connections import Connection


class AuthRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    # --- USERS QUERIES ---
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, email, hashed_password, full_name, created_at FROM users WHERE email = %s",
                (email,),
            )
            return cursor.fetchone()

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, email, full_name, created_at FROM users WHERE id = %s",
                (user_id,),
            )
            return cursor.fetchone()

    def create_user(self, email: str, hashed_password: str, full_name: str) -> int:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (email, hashed_password, full_name)
                VALUES (%s, %s, %s)
                """,
                (email, hashed_password, full_name),
            )
            return cursor.lastrowid

    # --- REFRESH TOKENS QUERIES ---
    def insert_refresh_token(self, user_id: int, token_hash: str, expires_at: datetime) -> int:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO refresh_tokens (user_id, token_hash, expires_at, revoked)
                VALUES (%s, %s, %s, 0)
                """,
                (user_id, token_hash, expires_at.strftime("%Y-%m-%d %H:%M:%S")),
            )
            return cursor.lastrowid

    def get_refresh_token(self, token_hash: str, user_id: int) -> Optional[Dict[str, Any]]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, revoked, expires_at
                FROM refresh_tokens
                WHERE token_hash = %s AND user_id = %s
                FOR UPDATE
                """,
                (token_hash, user_id),
            )
            return cursor.fetchone()

    def revoke_token_by_id(self, token_id: int) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE refresh_tokens SET revoked = 1 WHERE id = %s",
                (token_id,),
            )

    def revoke_token_by_hash(self, token_hash: str, user_id: int) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE refresh_tokens
                SET revoked = 1
                WHERE token_hash = %s AND user_id = %s
                """,
                (token_hash, user_id),
            )

    def revoke_all_user_tokens(self, user_id: int) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE refresh_tokens SET revoked = 1 WHERE user_id = %s",
                (user_id,),
            )