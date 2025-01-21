from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext
from models.user import (
    User
)
from models.auth import JWTAuth
from models.organization import Department
from .base import BaseService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService(BaseService[User]):
    """用户服务"""
    def __init__(self):
        super().__init__(User)
    
    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[User]:
        """通过 ID 获取用户"""
        stmt = select(self.model).where(
            self.model.id == id
        ).options(
            selectinload(User.class_),
            selectinload(User.department),
            selectinload(User.company),
            selectinload(User.points),
            selectinload(User.online_days)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_employee_id(
        self,
        db: AsyncSession,
        employee_id: str
    ) -> Optional[User]:
        """通过工号获取用户"""
        stmt = select(JWTAuth).where(
            JWTAuth.id == employee_id
        ).options(
            selectinload(JWTAuth.user).options(
                selectinload(User.class_),
                selectinload(User.department),
                selectinload(User.company),
                selectinload(User.points),
                selectinload(User.online_days)
            )
        )
        result = await db.execute(stmt)
        auth = result.scalar_one_or_none()
        if not auth:
            return None
        return auth.user
    
    async def authenticate(
        self,
        db: AsyncSession,
        *,
        employee_id: str,
        password: str
    ) -> Optional[User]:
        """验证用户"""
        stmt = select(JWTAuth).where(
            JWTAuth.id == employee_id
        ).options(selectinload(JWTAuth.user))
        result = await db.execute(stmt)
        auth = result.scalar_one_or_none()
        if not auth:
            return None
        if auth.password != password:
            return None
        return auth.user
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        department_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[User]:
        """获取用户列表"""
        stmt = select(self.model)
        if department_name:
            stmt = stmt.join(Department).where(
                Department.name == department_name
            )
        stmt = stmt.options(
            selectinload(User.class_),
            selectinload(User.department),
            selectinload(User.company),
            selectinload(User.points),
            selectinload(User.online_days)
        ).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
    
