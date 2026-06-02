"""
مدل ارسال همگانی
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime,
    Integer, Text, JSON, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Broadcast(Base):
    """مدل ارسال همگانی"""

    __tablename__ = "broadcasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False, default="ارسال بدون عنوان")

    # نوع ارسال
    broadcast_type: Mapped[str] = mapped_column(String(32), nullable=False, default="normal")
    # انواع: normal, forward

    # محتوا (برای ارسال معمولی)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    video_file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    document_file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    buttons: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # برای فوروارد
    forward_from_chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    forward_message_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # زمان‌بندی
    is_scheduled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # فیلتر مخاطبان
    target_all: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    target_role: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    target_labels: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # وضعیت
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    # وضعیت‌ها: pending, running, completed, failed, cancelled

    # آمار
    total_recipients: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blocked_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ایجاد کننده
    created_by: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # زمان‌ها
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Broadcast {self.id} ({self.status})>"
