"""
Middleware محدودیت نرخ درخواست (Rate Limiting)
"""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from app.redis_client import get_redis, RedisCache
from config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """محدودیت تعداد درخواست‌های کاربر"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if not settings.RATE_LIMIT_REQUESTS:
            return await handler(event, data)

        # دریافت آیدی کاربر
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None

        if not user_id:
            return await handler(event, data)

        try:
            redis = await get_redis()
            cache = RedisCache(redis, prefix="rate_limit")
            key = f"{user_id}"

            # بررسی محدودیت
            current_count = await cache.get_int(key, 0)

            if current_count >= settings.RATE_LIMIT_REQUESTS:
                # کاربر به حد مجاز رسیده
                if isinstance(event, CallbackQuery):
                    await event.answer(
                        "⚠️ تعداد درخواست‌های شما زیاد است. لطفاً چند لحظه صبر کنید.",
                        show_alert=True
                    )
                elif isinstance(event, Message):
                    await event.reply(
                        "⚠️ <b>تعداد درخواست‌های شما زیاد است!</b>\n"
                        f"لطفاً {settings.RATE_LIMIT_PERIOD} ثانیه صبر کنید."
                    )
                return

            # افزایش شمارنده
            new_count = await cache.increment(key)
            if new_count == 1:
                # تنظیم زمان انقضا فقط برای اولین درخواست
                await cache.expire(key, settings.RATE_LIMIT_PERIOD)

        except Exception as e:
            logger.error(f"خطا در RateLimitMiddleware: {e}")

        return await handler(event, data)
