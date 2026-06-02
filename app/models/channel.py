"""
مدل کانال‌های عضویت اجباری
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime,
    Integer, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Channel(Base):
    """مدل کانال‌های عضویت اجباری"""

    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False, default="کانال")
    invite_link: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # ترتیب بررسی عضویت
    check_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # وضعیت
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # آمار
    total_joins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # زمان‌ها
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Channel {self.username or self.channel_id}>"
