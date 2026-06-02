"""
Middleware‌های ربات
"""

from aiogram import Dispatcher
from .auth import AuthMiddleware
from .rate_limit import RateLimitMiddleware
from .logging_mw import LoggingMiddleware
from .db_session import DBSessionMiddleware


def setup_middlewares(dp: Dispatcher) -> None:
    """تنظیم تمام middleware‌ها"""
    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(DBSessionMiddleware())
    dp.update.middleware(AuthMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())
