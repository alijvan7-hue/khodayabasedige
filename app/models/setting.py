"""
مدل تنظیمات ربات
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Boolean, DateTime, Integer, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Setting(Base):
    """مدل تنظیمات ربات"""

    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    value_type: Mapped[str] = mapped_column(String(32), default="string", nullable=False)
    # انواع: string, integer, boolean, json, float
    category: Mapped[str] = mapped_column(String(64), default="general", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # زمان‌ها
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Setting {self.key}={self.value}>"

    @property
    def typed_value(self):
        """مقدار با نوع صحیح"""
        if self.value is None:
            return None
        if self.value_type == "integer":
            return int(self.value)
        if self.value_type == "boolean":
            return self.value.lower() in ("true", "1", "yes")
        if self.value_type == "float":
            return float(self.value)
        if self.value_type == "json":
            import json
            return json.loads(self.value)
        return self.value

    # تنظیمات پیش‌فرض
    DEFAULTS = {
        "bot_welcome_message": {
            "value": "سلام {name} عزیز! 👋\n\nبه ربات رسانه‌ای تلگرام خوش آمدید.",
            "type": "string",
            "category": "messages",
            "description": "پیام خوش‌آمدگویی ربات"
        },
        "force_join_enabled": {
            "value": "false",
            "type": "boolean",
            "category": "force_join",
            "description": "فعال/غیرفعال بودن عضویت اجباری"
        },
        "ads_enabled": {
            "value": "true",
            "type": "boolean",
            "category": "ads",
            "description": "فعال/غیرفعال بودن تبلیغات"
        },
        "auto_delete_enabled": {
            "value": "false",
            "type": "boolean",
            "category": "auto_delete",
            "description": "فعال/غیرفعال بودن حذف خودکار"
        },
        "auto_delete_seconds": {
            "value": "300",
            "type": "integer",
            "category": "auto_delete",
            "description": "زمان حذف خودکار (ثانیه)"
        },
        "thumbnail_enabled": {
            "value": "true",
            "type": "boolean",
            "category": "media",
            "description": "فعال/غیرفعال بودن تامبنیل"
        },
        "max_file_size_mb": {
            "value": "50",
            "type": "integer",
            "category": "media",
            "description": "حداکثر اندازه فایل (مگابایت)"
        },
        "remove_links": {
            "value": "false",
            "type": "boolean",
            "category": "filters",
            "description": "حذف لینک‌ها از کپشن"
        },
        "remove_usernames": {
            "value": "false",
            "type": "boolean",
            "category": "filters",
            "description": "حذف نام‌های کاربری از کپشن"
        },
        "rate_limit_enabled": {
            "value": "true",
            "type": "boolean",
            "category": "security",
            "description": "فعال بودن محدودیت نرخ"
        },
        "backup_enabled": {
            "value": "true",
            "type": "boolean",
            "category": "backup",
            "description": "فعال بودن پشتیبان‌گیری خودکار"
        },
    }
