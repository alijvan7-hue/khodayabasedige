"""
مدل لاگ اقدامات
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime,
    Integer, Text, JSON, ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Log(Base):
    """مدل لاگ اقدامات ادمین و کاربران"""

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # سطح لاگ
    level: Mapped[str] = mapped_column(String(16), nullable=False, default="info")
    # سطح‌ها: debug, info, warning, error, critical

    # دسته‌بندی
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="general")
    # دسته‌ها: admin_action, user_action, media, broadcast, security, system

    # اقدام
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # کاربر
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="SET NULL"), nullable=True
    )
    user_telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # اطلاعات اضافه
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # زمان
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # روابط
    user: Mapped[Optional["User"]] = relationship("User", back_populates="logs")

    def __repr__(self) -> str:
        return f"<Log [{self.level}] {self.action}>"
