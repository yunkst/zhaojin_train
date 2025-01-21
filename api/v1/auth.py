from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from core.database import get_session
from schemas.auth import LoginRequest, Token
from services.auth import AuthService
from services.user import UserService
from core.exceptions import AuthenticationError
router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/token", response_model=Token)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_session),
    auth_service: AuthService = Depends(),
    user_service: UserService = Depends()
) -> Token:
    """
    登录接口
    - 验证用户名密码
    - 生成 JWT token
    """
    # 验证用户
    user = await user_service.authenticate(
        db,
        employee_id=request.employee_id,
        password=request.password
    )
    if not user:
        raise AuthenticationError("Incorrect employee_id or password")
    
    # 生成 token
    access_token = auth_service.create_access_token(
        employee_id=request.employee_id
    )
    
    return Token(access_token=access_token) 