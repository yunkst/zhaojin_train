from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Index
from typing import Optional
from enum import Enum

class StatType(str, Enum):
    """统计类型"""
    # 用户总体统计
    DURATION = "duration"  # 总学习时长
    PRACTICE = "practice"  # 总练习次数
    CORRECT = "correct"   # 总正确数

    # 知识点相关统计
    PRACTICE_BY_KNOWLEDGE = "practice_by_knowledge"  # 每个知识点的练习次数
    CORRECT_BY_KNOWLEDGE = "correct_by_knowledge"   # 每个知识点的正确数

    @classmethod
    def user_stats(cls) -> list["StatType"]:
        """用户统计类型列表"""
        return [cls.DURATION, cls.PRACTICE, cls.CORRECT]
    
    @classmethod
    def knowledge_stats(cls) -> list["StatType"]:
        """知识点统计类型列表"""
        return [cls.PRACTICE_BY_KNOWLEDGE, cls.CORRECT_BY_KNOWLEDGE]

from .base import BaseModel

class StatInfo(BaseModel):
    """统计信息"""
    __tablename__ = "stat_info"

    type: Mapped[StatType] = mapped_column(String(64), nullable=False)
    source_id: Mapped[Optional[int]]
    target_id: Mapped[Optional[int]]
    total: Mapped[int] = mapped_column(nullable=False, default=0)

    # 索引
    __table_args__ = (
        Index("ix_stat_info_type", "type"),
        Index("ix_stat_info_source_id", "source_id"),
        Index("ix_stat_info_target_id", "target_id"),
        Index("ix_stat_info_total", "total"),
    )

class StatInfoRecord(BaseModel):
    """统计信息记录"""
    __tablename__ = "stat_info_record"

    type: Mapped[StatType] = mapped_column(String(64), nullable=False)
    source_id: Mapped[Optional[int]]
    target_id: Mapped[Optional[int]]
    value: Mapped[int] = mapped_column(nullable=False, default=0)

    # 索引
    __table_args__ = (
        Index("ix_stat_info_record_type", "type"),
        Index("ix_stat_info_record_source_id", "source_id"),
        Index("ix_stat_info_record_target_id", "target_id"),
        Index("ix_stat_info_record_created_at", "created_at"),
    ) 