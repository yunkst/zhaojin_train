from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
import logging
from core.config import settings
class AuthService:
    """认证服务"""
    
    @staticmethod
    def create_access_token(
        employee_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建访问令牌
        :param employee_id: 工号
        :param expires_delta: 过期时间
        :return: JWT token
        """
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode = {
            "exp": expire,
            "sub": employee_id
        }
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    async def verify_token(token: str) -> str:
        """
        验证令牌
        :param token: JWT token
        :return: 工号
        :raises: ValueError 如果令牌无效或过期
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            employee_id = payload.get("sub")
            if not isinstance(employee_id, str):
                raise ValueError("Could not validate credentials")
            return employee_id
        except JWTError as e:
            from api.app import AppContext
            logger: logging.Logger = AppContext.get_state("truthai_logger", logging.getLogger("truthai_logger"))
            logger.error(f"JWTError: {e}")
            raise ValueError("Could not validate credentials") 