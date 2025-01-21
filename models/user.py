from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Index

from .base import BaseModel

if TYPE_CHECKING:
    from .organization import Class, Department, Company
    from .auth import JWTAuth

class User(BaseModel):
    """用户"""
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    class_id: Mapped[int] = mapped_column(ForeignKey("class.id"), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id"), nullable=False)
    # 关系
    auth: Mapped[Optional["JWTAuth"]] = relationship(back_populates="user")
    class_: Mapped[Optional["Class"]] = relationship()
    department: Mapped[Optional["Department"]] = relationship()
    company: Mapped[Optional["Company"]] = relationship()
    points: Mapped[Optional["UserPoints"]] = relationship(back_populates="user")
    points_records: Mapped[List["UserPointsRecord"]] = relationship(back_populates="user")
    online_days: Mapped[Optional["OnlineDays"]] = relationship(back_populates="user")
    online_days_records: Mapped[List["OnlineDaysRecord"]] = relationship(back_populates="user")

    # 索引
    __table_args__ = (
        Index("ix_user_class_id", "class_id"),
        Index("ix_user_department_id", "department_id"),
        Index("ix_user_company_id", "company_id"),
    )

    # 从meta中提取的属性
    @property
    def avatar(self) -> str:
        """用户头像URL"""
        return self.meta.get("avatar", "")
    
    @property
    def employee_id(self) -> str:
        """工号"""
        return self.meta.get("employee_id", "")
    
    @property
    def job_title(self) -> str:
        """职位"""
        return self.meta.get("job_title", "")

    @property
    def class_name(self) -> str:
        """获取班级名称"""
        return self.class_.name if self.class_ else ""

    @property
    def department_name(self) -> str:
        """获取部门名称"""
        return self.department.name if self.department else ""

class UserPoints(BaseModel):
    """用户积分"""
    __tablename__ = "user_points"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    total: Mapped[int] = mapped_column(nullable=False, default=0)

    # 关系
    user: Mapped[Optional[User]] = relationship(back_populates="points")
    records: Mapped[List["UserPointsRecord"]] = relationship(back_populates="points")

    # 索引
    __table_args__ = (
        Index("ix_user_points_user_id", "user_id"),
        Index("ix_user_points_total", "total"),
    )

class UserPointsRecord(BaseModel):
    """用户积分记录"""
    __tablename__ = "user_points_record"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    points_id: Mapped[int] = mapped_column(ForeignKey("user_points.id"), nullable=False)
    value: Mapped[int] = mapped_column(nullable=False)

    # 关系
    user: Mapped[Optional[User]] = relationship(back_populates="points_records")
    points: Mapped[Optional[UserPoints]] = relationship(back_populates="records")

    # 索引
    __table_args__ = (
        Index("ix_user_points_record_user_id", "user_id"),
        Index("ix_user_points_record_points_id", "points_id"),
        Index("ix_user_points_record_created_at", "created_at"),
    )

class OnlineDays(BaseModel):
    """用户在线天数"""
    __tablename__ = "online_days"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    days: Mapped[int] = mapped_column(nullable=False, default=0)

    # 关系
    user: Mapped[Optional[User]] = relationship(back_populates="online_days")
    records: Mapped[List["OnlineDaysRecord"]] = relationship(back_populates="online_days")

    # 索引
    __table_args__ = (
        Index("ix_online_days_user_id", "user_id"),
        Index("ix_online_days_days", "days"),
    )

class OnlineDaysRecord(BaseModel):
    """用户在线天数记录"""
    __tablename__ = "online_days_record"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    online_days_id: Mapped[int] = mapped_column(ForeignKey("online_days.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(nullable=False)

    # 关系
    user: Mapped[Optional[User]] = relationship(back_populates="online_days_records")
    online_days: Mapped[Optional[OnlineDays]] = relationship(back_populates="records")

    # 索引
    __table_args__ = (
        Index("ix_online_days_record_user_id", "user_id"),
        Index("ix_online_days_record_online_days_id", "online_days_id"),
        Index("ix_online_days_record_created_at", "created_at"),
    ) 