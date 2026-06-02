"""
مدل رسانه
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime,
    Integer, Text, Float, JSON, ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Media(Base):
    """مدل فایل‌های رسانه"""

    __tablename__ = "media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    unique_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    # اطلاعات فایل تلگرام
    file_id: Mapped[str] = mapped_column(String(256), nullable=False)
    file_unique_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    media_type: Mapped[str] = mapped_column(String(32), nullable=False)
    # انواع: photo, video, audio, document, animation, voice, video_note

    # اطلاعات فایل
    file_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # کپشن و توضیحات
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # تامبنیل
    thumbnail_file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    custom_thumbnail_file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    thumbnail_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # فولدر
    folder_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("folders.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # آپلود کننده
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="SET NULL"), nullable=True
    )

    # آمار
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    share_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # فیلترها
    has_links_removed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_usernames_removed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # حذف خودکار
    auto_delete_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auto_delete_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # وضعیت
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # زمان‌ها
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )

    # روابط
    folder: Mapped[Optional["Folder"]] = relationship("Folder", back_populates="media")
    download_links: Mapped[list["DownloadLink"]] = relationship(
        "DownloadLink", back_populates="media", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Media {self.unique_id} ({self.media_type})>"

    @property
    def file_size_human(self) -> str:
        """اندازه فایل به فرمت خوانا"""
        if not self.file_size:
            return "نامشخص"
        size = self.file_size
        for unit in ['بایت', 'کیلوبایت', 'مگابایت', 'گیگابایت']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} ترابایت"
