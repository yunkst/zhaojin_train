from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class APIError(HTTPException):
    """API 错误基类"""
    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=status_code, detail=message, headers=headers)

class AuthenticationError(APIError):
    """认证错误"""
    def __init__(self, message: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            headers={"WWW-Authenticate": "Bearer"}
        )

class NotFoundError(APIError):
    """资源未找到错误"""
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message
        )

class ValidationError(APIError):
    """数据验证错误"""
    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message
        )

class PermissionError(APIError):
    """权限错误"""
    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message
        ) 