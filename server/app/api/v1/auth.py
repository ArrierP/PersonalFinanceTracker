from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from pymysql.connections import Connection

from ..deps import get_current_user, get_db
from ...schemas.auth_schema import (
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserRegisterRequest,
    conn: Connection = Depends(get_db),
):
    service = AuthService(conn)
    return service.register_user(payload)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UserLoginRequest,
    conn: Connection = Depends(get_db),
):
    service = AuthService(conn)
    return service.login_user(payload)


@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(
    payload: RefreshTokenRequest,
    conn: Connection = Depends(get_db),
):
    service = AuthService(conn)
    return service.rotate_refresh_token(payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    payload: RefreshTokenRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    conn: Connection = Depends(get_db),
):
    service = AuthService(conn)
    service.logout_user(raw_refresh_token=payload.refresh_token, user_id=current_user["id"])
    return {"status": "success", "message": "Đăng xuất thành công"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return current_user