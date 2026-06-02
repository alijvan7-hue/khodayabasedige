"""
Middleware Session دیتابیس
"""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class DBSessionMiddleware(BaseMiddleware):
    """اتاچ کردن session دیتابیس به هر درخواست"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with AsyncSessionLocal() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f"خطا در transaction: {e}")
                raise
            finally:
                await session.close()
