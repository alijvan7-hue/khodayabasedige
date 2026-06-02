"""
هندلرهای ربات
"""

from aiogram import Dispatcher
from .user.start import router as start_router
from .user.media import router as user_media_router
from .user.download import router as download_router
from .admin.panel import router as admin_panel_router
from .admin.media import router as admin_media_router
from .admin.users import router as admin_users_router
from .admin.broadcast import router as broadcast_router
from .admin.ads import router as ads_router
from .admin.force_join import router as force_join_router
from .admin.settings import router as settings_router
from .admin.backup import router as backup_router
from .admin.stats import router as stats_router


def setup_routers(dp: Dispatcher) -> None:
    """ثبت تمام روترها"""
    # روترهای کاربری
    dp.include_router(start_router)
    dp.include_router(user_media_router)
    dp.include_router(download_router)

    # روترهای ادمین
    dp.include_router(admin_panel_router)
    dp.include_router(admin_media_router)
    dp.include_router(admin_users_router)
    dp.include_router(broadcast_router)
    dp.include_router(ads_router)
    dp.include_router(force_join_router)
    dp.include_router(settings_router)
    dp.include_router(backup_router)
    dp.include_router(stats_router)
