"""
مدل ادمین (اطلاعات اضافه برای ادمین‌ها)
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime,
    Integer, JSON, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Admin(Base):
    """مدل اطلاعات اضافه ادمین‌ها"""

    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)

    # نقش
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="content_admin")
    # نقش‌ها: owner, super_admin, content_admin, support_admin

    # مجوزها
    permissions: Mapped[dict] = mapped_column(JSON, nullable=False, default={
        "can_upload": True,
        "can_delete_media": False,
        "can_ban_users": False,
        "can_broadcast": False,
        "can_manage_ads": False,
        "can_manage_channels": False,
        "can_manage_settings": False,
        "can_view_logs": False,
        "can_backup": False,
    })

    # وضعیت
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # اضافه کننده
    added_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # آمار
    total_actions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # زمان‌ها
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_action_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Admin {self.telegram_id} ({self.role})>"

    # مجوزهای پیش‌فرض هر نقش
    ROLE_PERMISSIONS = {
        "owner": {
            "can_upload": True,
            "can_delete_media": True,
            "can_ban_users": True,
            "can_broadcast": True,
            "can_manage_ads": True,
            "can_manage_channels": True,
            "can_manage_settings": True,
            "can_view_logs": True,
            "can_backup": True,
        },
        "super_admin": {
            "can_upload": True,
            "can_delete_media": True,
            "can_ban_users": True,
            "can_broadcast": True,
            "can_manage_ads": True,
            "can_manage_channels": True,
            "can_manage_settings": False,
            "can_view_logs": True,
            "can_backup": True,
        },
        "content_admin": {
            "can_upload": True,
            "can_delete_media": True,
            "can_ban_users": False,
            "can_broadcast": True,
            "can_manage_ads": True,
            "can_manage_channels": False,
            "can_manage_settings": False,
            "can_view_logs": False,
            "can_backup": False,
        },
        "support_admin": {
            "can_upload": False,
            "can_delete_media": False,
            "can_ban_users": False,
            "can_broadcast": False,
            "can_manage_ads": False,
            "can_manage_channels": False,
            "can_manage_settings": False,
            "can_view_logs": True,
            "can_backup": False,
        },
    }
