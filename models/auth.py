from datetime import datetime
from typing import Dict, Any, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, JSON

from .base import Base

if TYPE_CHECKING:
    from .user import User

class JWTAuth(Base):
    """JWT认证信息"""
    __tablename__ = "jwt_auth"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    meta: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    deleted: Mapped[bool] = mapped_column(nullable=False, default=False)

    # 关系
    user: Mapped["User"] = relationship(back_populates="auth") 