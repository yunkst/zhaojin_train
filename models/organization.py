from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Index

from .base import Base

if TYPE_CHECKING:
    from .user import User

class Corporation(Base):
    """集团"""
    __tablename__ = "corporation"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # 关系
    companies: Mapped[List["Company"]] = relationship(back_populates="corporation")

class Company(Base):
    """公司"""
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    corp_id: Mapped[int] = mapped_column(ForeignKey("corporation.id"), nullable=False)
    
    # 关系
    corporation: Mapped[Optional[Corporation]] = relationship(back_populates="companies")
    departments: Mapped[List["Department"]] = relationship(back_populates="company")

    # 索引
    __table_args__ = (
        Index("ix_company_corp_id", "corp_id"),
    )

class Department(Base):
    """部门"""
    __tablename__ = "department"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id"), nullable=False)
    
    # 关系
    company: Mapped[Optional[Company]] = relationship(back_populates="departments")
    classes: Mapped[List["Class"]] = relationship(back_populates="department")

    # 索引
    __table_args__ = (
        Index("ix_department_company_id", "company_id"),
    )

class Class(Base):
    """班级"""
    __tablename__ = "class"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"), nullable=False)
    
    # 关系
    department: Mapped[Optional[Department]] = relationship(back_populates="classes")
    users: Mapped[List["User"]] = relationship(back_populates="class_")

    # 索引
    __table_args__ = (
        Index("ix_class_department_id", "department_id"),
    ) 