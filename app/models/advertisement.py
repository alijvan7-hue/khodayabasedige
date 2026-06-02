"""
مدل تبلیغات
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime,
    Integer, Text, JSON, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Advertisement(Base):
    """مدل سیستم تبلیغات"""

    __tablename__ = "advertisements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)

    # نوع تبلیغ
    ad_type: Mapped[str] = mapped_column(String(32), nullable=False, default="text")
    # انواع: text, banner, button, mixed

    # محتوا
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    video_file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    # دکمه‌های کیبورد
    buttons: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # فرمت: [{"text": "متن دکمه", "url": "https://..."}, ...]

    # زمان‌بندی
    is_scheduled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    schedule_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    schedule_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    schedule_interval_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # موقعیت نمایش
    show_before_download: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    show_in_rotation: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ترتیب چرخش
    rotation_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # وضعیت
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # آمار
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    click_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ایجاد کننده
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # زمان‌ها
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Advertisement {self.title} ({self.ad_type})>"
