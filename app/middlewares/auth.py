"""
Middleware احراز هویت و ثبت کاربر
"""

import logging
from typing import Any, Awaitable, Callable, Dict
from datetime import datetime

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TelegramUser

from app.database import AsyncSessionLocal
from app.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """ثبت خودکار کاربر و بروزرسانی اطلاعات"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # دریافت کاربر تلگرام
        tg_user: TelegramUser | None = data.get("event_from_user")

        if tg_user and not tg_user.is_bot:
            session = data.get("session")
            if session:
                user_repo = UserRepository(session)
                try:
                    # ثبت یا بروزرسانی کاربر
                    user = await user_repo.create_or_update(
                        telegram_id=tg_user.id,
                        username=tg_user.username,
                        full_name=tg_user.full_name,
                        language_code=tg_user.language_code or "fa",
                        last_seen=datetime.utcnow()
                    )
                    data["db_user"] = user

                    # بررسی بن بودن کاربر
                    if user.is_banned:
                        # ارسال پیام بن بودن
                        if hasattr(event, "answer"):
                            try:
                                await event.answer(
                                    f"🚫 <b>دسترسی شما مسدود شده است.</b>\n\n"
                                    f"📝 دلیل: {user.ban_reason or 'نقض قوانین'}",
                                    show_alert=True
                                )
                            except Exception:
                                pass
                        elif hasattr(event, "reply"):
                            try:
                                await event.reply(
                                    f"🚫 <b>دسترسی شما مسدود شده است.</b>\n\n"
                                    f"📝 دلیل: {user.ban_reason or 'نقض قوانین'}"
                                )
                            except Exception:
                                pass
                        return  # توقف پردازش

                except Exception as e:
                    logger.error(f"خطا در AuthMiddleware: {e}")

        return await handler(event, data)
