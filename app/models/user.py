"""
مدل کاربر
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime,
    Integer, Text, JSON, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """مدل کاربران ربات"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False, default="کاربر ناشناس")
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False, default="fa")

    # وضعیت
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ban_reason: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # نقش ادمین
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="user", nullable=False)
    # نقش‌ها: user, support_admin, content_admin, super_admin, owner

    # برچسب‌ها
    labels: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # آمار
    total_downloads: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_uploads: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_messages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # زمان‌ها
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    banned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # روابط
    downloads: Mapped[List["DownloadLink"]] = relationship(
        "DownloadLink", back_populates="user", lazy="select"
    )
    logs: Mapped[List["Log"]] = relationship(
        "Log", back_populates="user", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} ({self.username or self.full_name})>"

    @property
    def mention(self) -> str:
        """لینک منشن کاربر"""
        return f'<a href="tg://user?id={self.telegram_id}">{self.full_name}</a>'

    @property
    def is_owner(self) -> bool:
        return self.role == "owner"

    @property
    def is_super_admin(self) -> bool:
        return self.role in ("owner", "super_admin")
