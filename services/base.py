from typing import TypeVar, Generic, Type, Optional, Sequence, Any, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseService(Generic[ModelType]):
    """基础服务类，提供通用的 CRUD 操作"""
    
    def __init__(self, model: Type[ModelType]):
        """
        初始化服务
        :param model: SQLAlchemy 模型类
        """
        self.model = model
    
    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """
        通过 ID 获取记录
        """
        stmt = select(self.model).where(self.model.id == id) # type: ignore
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[ModelType]:
        """
        获取多条记录
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, *, obj_in: Dict[str, Any]) -> ModelType:
        """
        创建记录
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """
        更新记录
        """
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        """
        删除记录
        """
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj 