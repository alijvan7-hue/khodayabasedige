"""
مدل فولدر
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime,
    Integer, Text, ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Folder(Base):
    """مدل فولدرهای رسانه"""

    __tablename__ = "folders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(8), default="📁", nullable=False)
    color: Mapped[str] = mapped_column(String(16), default="blue", nullable=False)

    # فولدر والد (برای ساختار درختی)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("folders.id", ondelete="SET NULL"), nullable=True
    )

    # مالک فولدر
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="SET NULL"), nullable=True
    )

    # ترتیب نمایش
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # وضعیت
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # آمار
    media_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_downloads: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # زمان‌ها
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )

    # روابط
    media: Mapped[List["Media"]] = relationship("Media", back_populates="folder", lazy="select")
    children: Mapped[List["Folder"]] = relationship("Folder", lazy="select")

    def __repr__(self) -> str:
        return f"<Folder {self.name}>"
