"""
هندلر مدیریت کاربران (ادمین)
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.admin_kb import (
    users_management_menu, user_profile_menu,
    confirm_action, cancel_button, back_button
)
from app.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)
router = Router(name="admin_users")


class UserSearchState(StatesGroup):
    """وضعیت جستجوی کاربر"""
    waiting_for_query = State()


class BanUserState(StatesGroup):
    """وضعیت بن کردن کاربر"""
    waiting_for_reason = State()


class MessageUserState(StatesGroup):
    """وضعیت ارسال پیام به کاربر"""
    waiting_for_message = State()


@router.callback_query(F.data == "users:search")
async def start_user_search(callback: CallbackQuery, state: FSMContext) -> None:
    """شروع جستجوی کاربر"""
    await state.set_state(UserSearchState.waiting_for_query)
    await callback.message.edit_text(
        "🔍 <b>جستجوی کاربر</b>\n\n"
        "آیدی عددی، یوزرنیم یا نام کاربر را وارد کنید:",
        reply_markup=cancel_button()
    )
    await callback.answer()


@router.message(UserSearchState.waiting_for_query)
async def handle_user_search(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """پردازش جستجوی کاربر"""
    query = message.text.strip()
    user_repo = UserRepository(session)

    user = None

    # جستجو با آیدی عددی
    if query.isdigit():
        user = await user_repo.get_by_telegram_id(int(query))

    # جستجو با یوزرنیم
    elif query.startswith("@"):
        user = await user_repo.get_by_username(query[1:])
    else:
        user = await user_repo.get_by_username(query)

    await state.clear()

    if not user:
        await message.reply(
            "❌ <b>کاربری با این مشخصات یافت نشد.</b>",
            reply_markup=back_button("admin:users")
        )
        return

    # نمایش پروفایل کاربر
    text = (
        f"👤 <b>پروفایل کاربر</b>\n\n"
        f"🆔 آیدی: <code>{user.telegram_id}</code>\n"
        f"📛 نام: {user.full_name}\n"
        f"👤 یوزرنیم: @{user.username or 'ندارد'}\n"
        f"🏷️ نقش: <code>{user.role}</code>\n"
        f"📅 عضویت: {user.created_at.strftime('%Y/%m/%d') if user.created_at else 'نامشخص'}\n\n"
        f"📊 <b>آمار:</b>\n"
        f"📥 دانلودها: {user.total_downloads}\n"
        f"📤 آپلودها: {user.total_uploads}\n\n"
        f"{'🚫 <b>این کاربر بن شده است!</b>' if user.is_banned else '✅ وضعیت: فعال'}\n"
        f"{'📝 دلیل بن: ' + user.ban_reason if user.is_banned and user.ban_reason else ''}"
    )

    await message.reply(
        text,
        reply_markup=user_profile_menu(
            user.telegram_id,
            is_banned=user.is_banned,
            is_admin=user.is_admin
        )
    )


@router.callback_query(F.data.startswith("user:ban:"))
async def start_ban_user(callback: CallbackQuery, state: FSMContext) -> None:
    """شروع فرآیند بن کردن"""
    user_id = callback.data.split(":")[2]
    await state.update_data(ban_user_id=user_id)
    await state.set_state(BanUserState.waiting_for_reason)

    await callback.message.edit_text(
        f"🚫 <b>بن کردن کاربر {user_id}</b>\n\n"
        "دلیل بن کردن را وارد کنید:",
        reply_markup=cancel_button()
    )
    await callback.answer()


@router.message(BanUserState.waiting_for_reason)
async def handle_ban_reason(
    message: Message, state: FSMContext, session: AsyncSession, db_user
) -> None:
    """اعمال بن کاربر"""
    data = await state.get_data()
    target_id = int(data["ban_user_id"])
    reason = message.text.strip()

    user_repo = UserRepository(session)
    success = await user_repo.ban_user(target_id, reason, by_admin=db_user.telegram_id)

    await state.clear()

    if success:
        # لاگ اقدام
        from app.repositories.log_repo import LogRepository
        log_repo = LogRepository(session)
        await log_repo.create(
            level="warning",
            category="admin_action",
            action="ban_user",
            description=f"کاربر {target_id} توسط {db_user.telegram_id} بن شد. دلیل: {reason}",
            user_id=db_user.telegram_id,
        )

        await message.reply(
            f"✅ <b>کاربر {target_id} با موفقیت بن شد.</b>\n"
            f"📝 دلیل: {reason}"
        )
    else:
        await message.reply("❌ خطا در بن کردن کاربر.")


@router.callback_query(F.data.startswith("user:unban:"))
async def unban_user(callback: CallbackQuery, session: AsyncSession, db_user) -> None:
    """رفع بن کاربر"""
    user_id = int(callback.data.split(":")[2])
    user_repo = UserRepository(session)

    success = await user_repo.unban_user(user_id)

    if success:
        # لاگ اقدام
        from app.repositories.log_repo import LogRepository
        log_repo = LogRepository(session)
        await log_repo.create(
            level="info",
            category="admin_action",
            action="unban_user",
            description=f"بن کاربر {user_id} توسط {db_user.telegram_id} رفع شد",
            user_id=db_user.telegram_id,
        )

        await callback.message.edit_text(
            f"✅ <b>بن کاربر {user_id} با موفقیت رفع شد.</b>",
            reply_markup=back_button("admin:users")
        )
        await callback.answer("رفع بن شد ✅")
    else:
        await callback.answer("❌ خطا در رفع بن", show_alert=True)


@router.callback_query(F.data == "users:list")
async def show_users_list(callback: CallbackQuery, session: AsyncSession) -> None:
    """نمایش لیست کاربران"""
    user_repo = UserRepository(session)
    users = await user_repo.get_recent(limit=10)

    text = "📋 <b>آخرین کاربران</b>\n\n"
    for i, user in enumerate(users, 1):
        status = "🚫" if user.is_banned else ("👑" if user.is_admin else "👤")
        text += f"{i}. {status} {user.full_name} (<code>{user.telegram_id}</code>)\n"

    total = await user_repo.count()
    text += f"\n📊 کل کاربران: <b>{total:,}</b>"

    await callback.message.edit_text(
        text,
        reply_markup=back_button("admin:users")
    )
    await callback.answer()


@router.callback_query(F.data == "users:banned")
async def show_banned_users(callback: CallbackQuery, session: AsyncSession) -> None:
    """نمایش کاربران بن‌شده"""
    user_repo = UserRepository(session)
    banned_users = await user_repo.get_banned()

    if not banned_users:
        await callback.message.edit_text(
            "✅ <b>هیچ کاربر بن‌شده‌ای وجود ندارد.</b>",
            reply_markup=back_button("admin:users")
        )
    else:
        text = f"🚫 <b>کاربران بن‌شده ({len(banned_users)} نفر)</b>\n\n"
        for user in banned_users[:20]:
            text += f"• {user.full_name} (<code>{user.telegram_id}</code>)\n"
            if user.ban_reason:
                text += f"  📝 {user.ban_reason}\n"

        await callback.message.edit_text(
            text,
            reply_markup=back_button("admin:users")
        )

    await callback.answer()
