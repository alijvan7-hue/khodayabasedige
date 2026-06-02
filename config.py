"""
تنظیمات پروژه با Pydantic Settings
"""

from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """تنظیمات کلی پروژه"""

    # ==================== ربات تلگرام ====================
    BOT_TOKEN: str
    BOT_VERSION: str = "1.0.0"
    BOT_NAME: str = "ربات رسانه‌ای تلگرام"

    # ==================== ادمین ====================
    OWNER_ID: int
    ADMIN_IDS: List[int] = []

    # ==================== دیتابیس ====================
    DATABASE_URL: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        """تبدیل URL دیتابیس برای SQLAlchemy Async"""
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://") and "+asyncpg" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # ==================== Redis ====================
    REDIS_URL: str = "redis://localhost:6379/0"

    # ==================== تنظیمات فایل ====================
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [
        "jpg", "jpeg", "png", "gif", "webp",
        "mp4", "avi", "mov", "mkv", "webm",
        "mp3", "ogg", "wav", "flac", "m4a",
        "pdf", "doc", "docx", "xls", "xlsx",
        "zip", "rar", "7z", "tar", "gz"
    ]

    # ==================== لینک دانلود ====================
    DEFAULT_EXPIRE_HOURS: int = 24
    SHORT_LINK_LENGTH: int = 8
    MAX_DOWNLOADS_PER_LINK: int = 100

    # ==================== محدودیت نرخ ====================
    RATE_LIMIT_REQUESTS: int = 30
    RATE_LIMIT_PERIOD: int = 60
    SPAM_THRESHOLD: int = 10

    # ==================== عضویت اجباری ====================
    FORCE_JOIN_ENABLED: bool = False
    FORCE_JOIN_CHANNELS: List[str] = []

    # ==================== تبلیغات ====================
    ADS_ENABLED: bool = True
    ADS_ROTATE_INTERVAL: int = 5
    ADS_SHOW_BEFORE_DOWNLOAD: bool = True

    # ==================== پشتیبان‌گیری ====================
    BACKUP_ENABLED: bool = True
    BACKUP_INTERVAL_HOURS: int = 24
    BACKUP_CHAT_ID: int = 0

    # ==================== حذف خودکار ====================
    AUTO_DELETE_ENABLED: bool = False
    AUTO_DELETE_SECONDS: int = 300

    # ==================== تامبنیل ====================
    THUMBNAIL_ENABLED: bool = True
    THUMBNAIL_SIZE: tuple = (320, 320)

    # ==================== لاگ ====================
    LOG_LEVEL: str = "INFO"
    LOG_CHAT_ID: int = 0
    LOG_TO_FILE: bool = False
    LOG_FILE_PATH: str = "logs/bot.log"

    # ==================== امنیت ====================
    SECRET_KEY: str = "change-me-in-production-please-use-random-string"
    LINK_SECRET: str = "change-link-secret-too"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """دریافت تنظیمات (با کش)"""
    return Settings()


settings = get_settings()
