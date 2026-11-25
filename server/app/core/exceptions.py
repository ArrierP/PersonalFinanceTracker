from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import pymysql


class AppException(Exception):
    """Base exception cho toàn bộ ứng dụng"""
    def __init__(
        self,
        status_code: int,
        message: str,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.detail = detail
        self.headers = headers

class BadRequestException(AppException):
    def __init__(self, message: str = "Yêu cầu không hợp lệ", detail: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, message=message, detail=detail)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Chưa xác thực hoặc token không hợp lệ", detail: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "Bạn không có quyền thực hiện thao tác này", detail: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, message=message, detail=detail)


class NotFoundException(AppException):
    def __init__(self, message: str = "Không tìm thấy dữ liệu yêu cầu", detail: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message, detail=detail)


class ConflictException(AppException):
    def __init__(self, message: str = "Dữ liệu đã tồn tại hoặc bị xung đột", detail: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_409_CONFLICT, message=message, detail=detail)


def register_exception_handlers(app: FastAPI) -> None:
    """Đăng ký các global exception handlers vào FastAPI app (gọi trong main.py)"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.message,
                "detail": exc.detail,
            },
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = [
            {"field": ".".join(str(loc) for loc in err["loc"]), "msg": err["msg"]}
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "error",
                "message": "Dữ liệu đầu vào không hợp lệ",
                "detail": errors,
            },
        )

    @app.exception_handler(pymysql.err.IntegrityError)
    async def mysql_integrity_error_handler(request: Request, exc: pymysql.err.IntegrityError):
        # Mã lỗi 1062: Duplicate entry (VD: trùng email, trùng budget trong cùng tháng)
        # Mã lỗi 1452: Foreign key constraint fails (VD: category_id không tồn tại)
        err_code = exc.args[0] if exc.args else 0
        if err_code == 1062:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "status": "error",
                    "message": "Dữ liệu bị trùng lặp (vi phạm ràng buộc duy nhất)",
                    "detail": str(exc.args[1]) if len(exc.args) > 1 else None,
                },
            )
        if err_code == 1452:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "error",
                    "message": "Dữ liệu tham chiếu (khóa ngoại) không tồn tại",
                    "detail": str(exc.args[1]) if len(exc.args) > 1 else None,
                },
            )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": "Lỗi ràng buộc dữ liệu trong Database",
                "detail": str(exc),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Lỗi hệ thống nội bộ (Internal Server Error)",
                "detail": str(exc),  # Nên ẩn khi deploy production nếu cần
            },
        )