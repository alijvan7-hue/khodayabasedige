"""
مدل پشتیبان‌گیری
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime,
    Integer, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Backup(Base):
    """مدل فایل‌های پشتیبان"""

    __tablename__ = "backups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # نوع پشتیبان
    backup_type: Mapped[str] = mapped_column(String(32), nullable=False, default="database")
    # انواع: database, media, full

    # اطلاعات فایل
    file_name: Mapped[str] = mapped_column(String(256), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # آیدی فایل در تلگرام (پس از ارسال)
    telegram_file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    sent_to_chat: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # وضعیت
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    # وضعیت‌ها: pending, processing, completed, failed

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # آیا به‌صورت خودکار ایجاد شده
    is_automatic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ایجاد کننده
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # زمان‌ها
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Backup {self.file_name} ({self.status})>"
