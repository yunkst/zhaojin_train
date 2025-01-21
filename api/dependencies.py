from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from core.database import get_session
from core.exceptions import AuthenticationError, NotFoundError
from models.user import User
from services.auth import AuthService
from services.user import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
    auth_service: AuthService = Depends(),
    user_service: UserService = Depends()
) -> User:
    """
    获取当前用户
    :raises: AuthenticationError 如果认证失败
    :raises: NotFoundError 如果用户不存在
    """
    try:
        # 验证 token
        employee_id = await auth_service.verify_token(token)
        
        # 获取用户
        user = await user_service.get_by_employee_id(db, employee_id)
        if not user:
            raise NotFoundError("User not found")
        return user
    except ValueError as e:
        raise AuthenticationError(str(e)) 