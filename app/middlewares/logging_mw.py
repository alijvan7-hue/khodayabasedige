"""
Middleware لاگ‌گذاری
"""

import logging
import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """لاگ‌گذاری تمام درخواست‌های ورودی"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        start_time = time.time()

        # لاگ ورودی
        user = data.get("event_from_user")
        if user:
            logger.debug(
                f"📨 درخواست از کاربر {user.id} ({user.username or user.full_name})"
            )

        try:
            result = await handler(event, data)
            elapsed = time.time() - start_time
            logger.debug(f"✅ پردازش در {elapsed:.3f} ثانیه")
            return result

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"❌ خطا پس از {elapsed:.3f} ثانیه: {type(e).__name__}: {e}",
                exc_info=True
            )
            raise
