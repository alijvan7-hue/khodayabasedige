"""
مدل لینک دانلود
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime,
    Integer, ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DownloadLink(Base):
    """مدل لینک‌های دانلود یکتا"""

    __tablename__ = "download_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    # رسانه مرتبط
    media_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("media.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # کاربر ایجادکننده
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="SET NULL"), nullable=True
    )

    # تنظیمات لینک
    max_downloads: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # ۰ = نامحدود

    require_button_click: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    require_view_confirm: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    require_channel_join: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # انقضا
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_expired: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # آمار
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    button_click_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # وضعیت
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # زمان‌ها
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_downloaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # روابط
    media: Mapped["Media"] = relationship("Media", back_populates="download_links")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="downloads")

    def __repr__(self) -> str:
        return f"<DownloadLink {self.token}>"

    @property
    def is_downloadable(self) -> bool:
        """بررسی قابل دانلود بودن"""
        if not self.is_active or self.is_expired:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at.replace(tzinfo=None):
            return False
        if self.max_downloads > 0 and self.download_count >= self.max_downloads:
            return False
        return True

    @property
    def short_link(self) -> str:
        """لینک کوتاه برای ارسال"""
        return f"start={self.token}"
