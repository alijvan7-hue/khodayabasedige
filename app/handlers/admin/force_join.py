"""
هندلر عضویت اجباری
"""
import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.admin_kb import force_join_menu, cancel_button, back_button
from app.repositories.channel_repo import ChannelRepository
from app.repositories.setting_repo import SettingRepository

logger = logging.getLogger(__name__)
router = Router(name="admin_force_join")


class AddChannelState(StatesGroup):
    waiting_for_channel = State()


@router.callback_query(F.data == "fj:toggle")
async def toggle_force_join(callback: CallbackQuery, session: AsyncSession) -> None:
    setting_repo = SettingRepository(session)
    current = (await setting_repo.get_value("force_join_enabled", "false")) == "true"
    new_value = not current

    await setting_repo.set_value("force_join_enabled", str(new_value).lower())

    status = "🟢 فعال" if new_value else "🔴 غیرفعال"
    await callback.message.edit_text(
        f"🔒 <b>عضویت اجباری</b>\n\nوضعیت تغییر یافت: {status}",
        reply_markup=force_join_menu(new_value)
    )
    await callback.answer(f"تغییر یافت: {status}")


@router.callback_query(F.data == "fj:add_channel")
async def add_channel_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddChannelState.waiting_for_channel)
    await callback.message.edit_text(
        "📢 <b>افزودن کانال</b>\n\n"
        "ربات را به کانال اضافه کنید (با سطح ادمین)، سپس:\n"
        "• یوزرنیم کانال را ارسال کنید (مثال: @channel)\n"
        "• یا آیدی عددی کانال را ارسال کنید (مثال: -1001234567890)",
        reply_markup=cancel_button()
    )
    await callback.answer()


@router.message(AddChannelState.waiting_for_channel)
async def handle_add_channel(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot
) -> None:
    channel_input = message.text.strip()
    await state.clear()

    try:
        if channel_input.startswith("@"):
            chat = await bot.get_chat(channel_input)
        elif channel_input.lstrip("-").isdigit():
            chat = await bot.get_chat(int(channel_input))
        else:
            await message.reply("❌ فرمت نادرست. یوزرنیم یا آیدی وارد کنید.")
            return

        channel_repo = ChannelRepository(session)
        channel = await channel_repo.create(
            channel_id=chat.id,
            username=chat.username,
            title=chat.title or "کانال",
            is_active=True,
            is_required=True,
        )

        await message.reply(
            f"✅ <b>کانال افزوده شد!</b>\n\n"
            f"📛 نام: {channel.title}\n"
            f"👤 یوزرنیم: @{channel.username or 'ندارد'}\n"
            f"🆔 آیدی: {channel.channel_id}"
        )

    except Exception as e:
        logger.error(f"خطا در افزودن کانال: {e}")
        await message.reply(
            f"❌ خطا در دریافت اطلاعات کانال.\n"
            "مطمئن شوید ربات به کانال اضافه شده است."
        )


@router.callback_query(F.data == "fj:list")
async def list_channels(callback: CallbackQuery, session: AsyncSession) -> None:
    channel_repo = ChannelRepository(session)
    channels = await channel_repo.get_all()

    if not channels:
        await callback.message.edit_text(
            "🔒 <b>کانال‌های عضویت اجباری</b>\n\nهیچ کانالی تنظیم نشده است.",
            reply_markup=back_button("admin:force_join")
        )
    else:
        text = f"🔒 <b>کانال‌های عضویت اجباری ({len(channels)} عدد)</b>\n\n"
        for ch in channels:
            status = "🟢" if ch.is_active else "🔴"
            text += f"{status} {ch.title}\n"
            if ch.username:
                text += f"   👤 @{ch.username}\n"
            text += f"   🆔 {ch.channel_id}\n\n"

        await callback.message.edit_text(
            text, reply_markup=back_button("admin:force_join")
        )

    await callback.answer()
