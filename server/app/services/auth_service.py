from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from pymysql.connections import Connection

from app.core.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from ..repositories.auth_repo import AuthRepository
from ..schemas.auth_schema import TokenResponse, UserLoginRequest, UserRegisterRequest


class AuthService:
    def __init__(self, conn: Connection):
        self.conn = conn
        self.repo = AuthRepository(conn)

    def _issue_token_pair(self, user_id: int) -> TokenResponse:
        """Tạo cặp Access + Refresh Token mới và ghi nhận vào DB (chưa commit)"""
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)
        token_hashed = hash_token(refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        self.repo.insert_refresh_token(
            user_id=user_id,
            token_hash=token_hashed,
            expires_at=expires_at,
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def register_user(self, payload: UserRegisterRequest) -> Dict[str, Any]:
        if self.repo.get_user_by_email(payload.email):
            raise ConflictException(message="Email này đã được sử dụng")

        try:
            hashed_pw = hash_password(payload.password)
            new_user_id = self.repo.create_user(
                email=payload.email,
                hashed_password=hashed_pw,
                full_name=payload.full_name,
            )
            self.conn.commit()
            return self.repo.get_user_by_id(new_user_id)
        except Exception:
            self.conn.rollback()
            raise

    def login_user(self, payload: UserLoginRequest) -> TokenResponse:
        user = self.repo.get_user_by_email(payload.email)
        if not user or not verify_password(payload.password, user["hashed_password"]):
            raise UnauthorizedException(message="Email hoặc mật khẩu không chính xác")

        try:
            tokens = self._issue_token_pair(user_id=user["id"])
            self.conn.commit()
            return tokens
        except Exception:
            self.conn.rollback()
            raise

    def rotate_refresh_token(self, raw_refresh_token: str) -> TokenResponse:
        """Kiểm tra token cũ -> thu hồi -> cấp cặp token mới trong cùng 1 transaction"""
        decoded = decode_token(raw_refresh_token, expected_type="refresh")
        user_id = int(decoded["sub"])
        old_token_hash = hash_token(raw_refresh_token)

        db_token = self.repo.get_refresh_token(token_hash=old_token_hash, user_id=user_id)
        if not db_token:
            raise UnauthorizedException(message="Refresh token không tồn tại trong hệ thống")

        # Nếu token đã bị thu hồi trước đó -> nghi ngờ bị lộ token -> thu hồi toàn bộ phiên của user
        if db_token["revoked"] == 1:
            self.repo.revoke_all_user_tokens(user_id=user_id)
            self.conn.commit()
            raise UnauthorizedException(
                message="Phát hiện tái sử dụng refresh token đã thu hồi. Vui lòng đăng nhập lại!"
            )

        try:
            self.repo.revoke_token_by_id(token_id=db_token["id"])
            new_tokens = self._issue_token_pair(user_id=user_id)
            self.conn.commit()
            return new_tokens
        except Exception:
            self.conn.rollback()
            raise

    def logout_user(self, raw_refresh_token: str, user_id: int) -> None:
        token_hashed = hash_token(raw_refresh_token)
        try:
            self.repo.revoke_token_by_hash(token_hash=token_hashed, user_id=user_id)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise