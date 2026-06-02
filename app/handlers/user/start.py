"""
هندلر استارت و منوی اصلی کاربر
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.user_kb import user_main_menu, user_profile_kb
from app.keyboards.admin_kb import admin_main_menu
from app.repositories.user_repo import UserRepository
from app.repositories.setting_repo import SettingRepository
from config import settings

logger = logging.getLogger(__name__)
router = Router(name="user_start")


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, db_user, state: FSMContext) -> None:
    """هندلر دستور /start"""
    await state.clear()

    # دریافت پیام خوش‌آمدگویی از تنظیمات
    setting_repo = SettingRepository(session)
    welcome_text = await setting_repo.get_value(
        "bot_welcome_message",
        default=f"سلام {{name}} عزیز! 👋\n\nبه ربات رسانه‌ای خوش آمدید."
    )

    welcome = welcome_text.format(
        name=message.from_user.full_name,
        username=message.from_user.username or "کاربر",
        id=message.from_user.id,
    )

    # بررسی عضویت اجباری
    fj_enabled = await setting_repo.get_value("force_join_enabled", default="false")
    if fj_enabled == "true":
        from app.services.force_join_service import check_membership
        from app.repositories.channel_repo import ChannelRepository
        channel_repo = ChannelRepository(session)
        channels = await channel_repo.get_active_channels()

        if channels:
            is_member = await check_membership(message.bot, message.from_user.id, channels)
            if not is_member:
                from app.keyboards.user_kb import force_join_kb
                await message.answer(
                    "⚠️ <b>برای استفاده از ربات، ابتدا باید عضو کانال‌های زیر شوید:</b>",
                    reply_markup=force_join_kb([
                        {"title": c.title, "invite_link": c.invite_link, "username": c.username}
                        for c in channels
                    ])
                )
                return

    await message.answer(welcome, reply_markup=user_main_menu())


@router.message(Command("admin"))
async def cmd_admin(message: Message, db_user) -> None:
    """هندلر دستور /admin - پنل ادمین"""
    if not db_user or not db_user.is_admin:
        await message.reply(
            "❌ شما دسترسی به پنل ادمین ندارید."
        )
        return

    await message.answer(
        f"👑 <b>پنل مدیریت ربات</b>\n\n"
        f"👤 سطح دسترسی: <code>{db_user.role}</code>\n"
        f"🔧 یک بخش را انتخاب کنید:",
        reply_markup=admin_main_menu()
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """هندلر دستور /help"""
    await message.answer(
        "📚 <b>راهنمای ربات</b>\n\n"
        "دستورات موجود:\n"
        "/start - شروع ربات\n"
        "/help - نمایش این راهنما\n"
        "/admin - پنل ادمین (فقط ادمین‌ها)\n\n"
        "برای دریافت فایل:\n"
        "• از فولدرها استفاده کنید\n"
        "• از جستجو استفاده کنید\n"
        "• لینک دانلود وارد کنید\n\n"
        "❓ برای پشتیبانی از دکمه «پشتیبانی» استفاده کنید."
    )


@router.message(F.text == "👤 پروفایل من")
async def show_profile(message: Message, db_user) -> None:
    """نمایش پروفایل کاربر"""
    if not db_user:
        await message.reply("❌ خطا در دریافت اطلاعات.")
        return

    text = (
        f"👤 <b>پروفایل شما</b>\n\n"
        f"🆔 آیدی: <code>{db_user.telegram_id}</code>\n"
        f"📛 نام: {db_user.full_name}\n"
        f"👤 یوزرنیم: @{db_user.username or 'ندارد'}\n\n"
        f"📥 دانلودها: <b>{db_user.total_downloads}</b>\n"
        f"📤 آپلودها: <b>{db_user.total_uploads}</b>\n"
        f"💬 پیام‌ها: <b>{db_user.total_messages}</b>\n\n"
        f"📅 عضویت: {db_user.created_at.strftime('%Y/%m/%d') if db_user.created_at else 'نامشخص'}"
    )

    await message.answer(text, reply_markup=user_profile_kb(db_user.telegram_id))


@router.message(F.text == "ℹ️ درباره ربات")
async def about_bot(message: Message) -> None:
    """اطلاعات درباره ربات"""
    await message.answer(
        f"🤖 <b>ربات آپلودر رسانه تلگرام</b>\n\n"
        f"📌 نسخه: {settings.BOT_VERSION}\n"
        f"🔧 ساخته شده با: Python 3.12 + Aiogram 3.x\n"
        f"🗄️ دیتابیس: PostgreSQL\n"
        f"⚡ کش: Redis\n\n"
        f"✨ امکانات:\n"
        f"• آپلود و مدیریت رسانه\n"
        f"• لینک دانلود یکتا\n"
        f"• عضویت اجباری\n"
        f"• ارسال همگانی\n"
        f"• پنل ادمین فارسی\n"
        f"• و بسیاری دیگر..."
    )


@router.message(F.text == "📞 پشتیبانی")
async def support(message: Message) -> None:
    """پشتیبانی"""
    from app.keyboards.user_kb import support_kb
    await message.answer(
        "📞 <b>پشتیبانی</b>\n\n"
        "چه نوع کمکی نیاز دارید؟",
        reply_markup=support_kb()
    )
