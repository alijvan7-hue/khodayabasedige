"""
هندلر پنل اصلی ادمین
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters import Filter
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.admin_kb import (
    admin_main_menu, media_management_menu, users_management_menu,
    broadcast_menu, ads_menu, force_join_menu, settings_menu,
    stats_menu, backup_menu
)

logger = logging.getLogger(__name__)
router = Router(name="admin_panel")


class IsAdmin(Filter):
    """فیلتر بررسی ادمین بودن"""
    async def __call__(self, event, db_user=None) -> bool:
        return db_user is not None and db_user.is_admin


# اعمال فیلتر ادمین به تمام هندلرهای این روتر
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "admin:main")
async def admin_main(callback: CallbackQuery) -> None:
    """منوی اصلی پنل ادمین"""
    await callback.message.edit_text(
        "👑 <b>پنل مدیریت ربات</b>\n\nیک بخش را انتخاب کنید:",
        reply_markup=admin_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:media")
async def admin_media(callback: CallbackQuery) -> None:
    """منوی مدیریت رسانه"""
    await callback.message.edit_text(
        "📁 <b>مدیریت رسانه</b>\n\nچه اقدامی می‌خواهید انجام دهید؟",
        reply_markup=media_management_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:users")
async def admin_users(callback: CallbackQuery) -> None:
    """منوی مدیریت کاربران"""
    await callback.message.edit_text(
        "👥 <b>مدیریت کاربران</b>\n\nچه اقدامی می‌خواهید انجام دهید؟",
        reply_markup=users_management_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast(callback: CallbackQuery) -> None:
    """منوی ارسال همگانی"""
    await callback.message.edit_text(
        "📣 <b>ارسال همگانی</b>\n\nچه اقدامی می‌خواهید انجام دهید؟",
        reply_markup=broadcast_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:ads")
async def admin_ads(callback: CallbackQuery) -> None:
    """منوی تبلیغات"""
    await callback.message.edit_text(
        "📢 <b>مدیریت تبلیغات</b>\n\nچه اقدامی می‌خواهید انجام دهید؟",
        reply_markup=ads_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:force_join")
async def admin_force_join(callback: CallbackQuery, session: AsyncSession) -> None:
    """منوی عضویت اجباری"""
    from app.repositories.setting_repo import SettingRepository
    setting_repo = SettingRepository(session)
    is_enabled = (await setting_repo.get_value("force_join_enabled", "false")) == "true"

    status = "🟢 فعال" if is_enabled else "🔴 غیرفعال"
    await callback.message.edit_text(
        f"🔒 <b>عضویت اجباری</b>\n\nوضعیت: {status}\n\nچه اقدامی می‌خواهید انجام دهید؟",
        reply_markup=force_join_menu(is_enabled)
    )
    await callback.answer()


@router.callback_query(F.data == "admin:settings")
async def admin_settings(callback: CallbackQuery) -> None:
    """منوی تنظیمات"""
    await callback.message.edit_text(
        "⚙️ <b>تنظیمات ربات</b>\n\nچه بخشی را می‌خواهید تنظیم کنید؟",
        reply_markup=settings_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery, session: AsyncSession) -> None:
    """نمایش آمار ربات"""
    from app.repositories.user_repo import UserRepository
    from app.repositories.media_repo import MediaRepository
    from app.repositories.download_link_repo import DownloadLinkRepository

    user_repo = UserRepository(session)
    media_repo = MediaRepository(session)

    total_users = await user_repo.count()
    active_today = await user_repo.count_active_today()
    active_month = await user_repo.count_active_month()
    total_media = await media_repo.count()
    total_banned = await user_repo.count_banned()

    await callback.message.edit_text(
        f"📊 <b>آمار ربات</b>\n\n"
        f"👥 کل کاربران: <b>{total_users:,}</b>\n"
        f"📅 فعال امروز: <b>{active_today:,}</b>\n"
        f"📆 فعال این ماه: <b>{active_month:,}</b>\n"
        f"🚫 کاربران بن‌شده: <b>{total_banned:,}</b>\n\n"
        f"📁 کل رسانه‌ها: <b>{total_media:,}</b>\n",
        reply_markup=stats_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:backup")
async def admin_backup(callback: CallbackQuery) -> None:
    """منوی پشتیبان‌گیری"""
    await callback.message.edit_text(
        "💾 <b>سیستم پشتیبان‌گیری</b>\n\nچه اقدامی می‌خواهید انجام دهید؟",
        reply_markup=backup_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery) -> None:
    """لغو اقدام جاری"""
    await callback.message.edit_text(
        "❌ <b>اقدام لغو شد.</b>",
        reply_markup=admin_main_menu()
    )
    await callback.answer("لغو شد")
