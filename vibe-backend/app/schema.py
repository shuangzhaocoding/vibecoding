# -*- coding: utf-8 -*-
"""通用响应体与业务异常。"""
from typing import Any, Optional

from pydantic import BaseModel


class ResponseSuccess(BaseModel):
    code: int = 1200
    message: str = "success"
    data: Any = None


class ResponseFailed(BaseModel):
    code: int = 1100
    message: str = "failed"
    detail: Any = None


class BaseAppException(Exception):
    """业务异常基类，由全局 handler 转换。"""

    def __init__(
        self,
        message: str = "error",
        code: int = 1100,
        detail: Any = None,
        error_code: Optional[str] = None,
    ):
        self.message = message
        self.code = code
        self.detail = detail
        self.error_code = error_code or "BUSINESS_ERROR"
        super().__init__(message)


class AuthException(BaseAppException):
    def __init__(
        self,
        message: str = "unauthorized",
        detail: Any = None,
        error_code: str = "AUTH_ERROR",
    ):
        super().__init__(message=message, code=1100, detail=detail, error_code=error_code)


class PermissionException(BaseAppException):
    def __init__(
        self,
        message: str = "permission denied",
        detail: Any = None,
        error_code: str = "PERMISSION_DENIED",
    ):
        super().__init__(message=message, code=1100, detail=detail, error_code=error_code)


class NotFoundException(BaseAppException):
    def __init__(
        self,
        message: str = "not found",
        detail: Any = None,
        error_code: str = "NOT_FOUND",
    ):
        super().__init__(message=message, code=1100, detail=detail, error_code=error_code)
