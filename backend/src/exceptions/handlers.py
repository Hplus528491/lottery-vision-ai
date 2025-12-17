"""
異常處理模組

定義自定義異常和全局異常處理器
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from enum import Enum
from typing import Any, Optional


class ErrorCode(str, Enum):
    """錯誤代碼枚舉"""
    
    # 通用錯誤 (1000-1999)
    INTERNAL_ERROR = "E1000"
    VALIDATION_ERROR = "E1001"
    NOT_FOUND = "E1002"
    PERMISSION_DENIED = "E1003"
    
    # 認證錯誤 (2000-2999)
    INVALID_CREDENTIALS = "E2000"
    TOKEN_EXPIRED = "E2001"
    TOKEN_INVALID = "E2002"
    USER_NOT_FOUND = "E2003"
    USER_INACTIVE = "E2004"
    EMAIL_ALREADY_EXISTS = "E2005"
    USERNAME_ALREADY_EXISTS = "E2006"
    
    # 積分錯誤 (3000-3999)
    INSUFFICIENT_CREDITS = "E3000"
    INVALID_TRANSACTION = "E3001"
    PACKAGE_NOT_FOUND = "E3002"
    
    # 彩券錯誤 (4000-4999)
    LOTTERY_NOT_FOUND = "E4000"
    INVALID_LOTTERY_TYPE = "E4001"
    DRAW_NOT_FOUND = "E4002"
    
    # 推薦錯誤 (5000-5999)
    RECOMMENDATION_FAILED = "E5000"
    AI_SERVICE_ERROR = "E5001"
    STRATEGY_NOT_FOUND = "E5002"


class AppException(HTTPException):
    """應用自定義異常"""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        status_code: int = 400,
        details: Optional[Any] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details
        super().__init__(status_code=status_code, detail=message)


class AuthenticationError(AppException):
    """認證錯誤"""
    
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.INVALID_CREDENTIALS,
        message: str = "認證失敗"
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=401
        )


class AuthorizationError(AppException):
    """授權錯誤"""
    
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.PERMISSION_DENIED,
        message: str = "權限不足"
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=403
        )


class NotFoundError(AppException):
    """資源不存在錯誤"""
    
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.NOT_FOUND,
        message: str = "資源不存在"
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=404
        )


class InsufficientCreditsError(AppException):
    """積分不足錯誤"""
    
    def __init__(
        self,
        message: str = "積分不足",
        required: int = 0,
        available: int = 0
    ):
        super().__init__(
            error_code=ErrorCode.INSUFFICIENT_CREDITS,
            message=message,
            status_code=402,
            details={"required": required, "available": available}
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    應用異常處理器
    
    Args:
        request: 請求對象
        exc: 異常對象
        
    Returns:
        JSONResponse: JSON 響應
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code.value,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    通用異常處理器
    
    Args:
        request: 請求對象
        exc: 異常對象
        
    Returns:
        JSONResponse: JSON 響應
    """
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.INTERNAL_ERROR.value,
                "message": "內部服務器錯誤",
                "details": str(exc) if request.app.debug else None
            }
        }
    )
