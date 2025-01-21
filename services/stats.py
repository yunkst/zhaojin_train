from typing import Optional, Sequence, Any
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.stats import StatInfo, StatInfoRecord
from .base import BaseService

class StatInfoService(BaseService[StatInfo]):
    """统计信息服务"""
    def __init__(self):
        super().__init__(StatInfo)
    
    async def get_by_type(
        self,
        db: AsyncSession,
        type_: str,
        source_id: Optional[int] = None,
        target_id: Optional[int] = None,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[StatInfo]:
        """获取指定类型的统计信息"""
        query = select(self.model).where(self.model.type == type_)
        
        if source_id is not None:
            query = query.where(self.model.source_id == source_id)
        if target_id is not None:
            query = query.where(self.model.target_id == target_id)
        
        query = query.offset(skip).limit(limit)
        result = await db.exec(query)
        return result.all()
    
    async def add_value(
        self,
        db: AsyncSession,
        type_: str,
        value: int,
        *,
        source_id: Optional[int] = None,
        target_id: Optional[int] = None,
        meta: dict[str, Any] | None = None
    ) -> tuple[StatInfo, StatInfoRecord]:
        """
        增加统计值
        :return: (统计信息, 统计记录)
        """
        # 获取或创建统计信息
        query = select(self.model).where(
            self.model.type == type_,
            self.model.source_id == source_id,
            self.model.target_id == target_id
        )
        result = await db.exec(query)
        stat_info = result.first()
        
        if not stat_info:
            stat_info = StatInfo(
                type=type_,
                source_id=source_id,
                target_id=target_id,
                total=0
            )
            db.add(stat_info)
        
        # 更新总值
        stat_info.total += value
        
        # 创建统计记录
        record = StatInfoRecord(
            type=type_,
            source_id=source_id,
            target_id=target_id,
            value=value,
            meta=meta or {}
        )
        db.add(record)
        
        await db.commit()
        await db.refresh(stat_info)
        await db.refresh(record)
        
        return stat_info, record 