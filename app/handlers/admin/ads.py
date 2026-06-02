"""
هندلر مدیریت تبلیغات
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.admin_kb import ads_menu, cancel_button, back_button, confirm_action
from app.repositories.ads_repo import AdsRepository

logger = logging.getLogger(__name__)
router = Router(name="admin_ads")


class AdsCreateState(StatesGroup):
    waiting_for_title = State()
    waiting_for_type = State()
    waiting_for_content = State()


@router.callback_query(F.data == "ads:new")
async def new_ad(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdsCreateState.waiting_for_title)
    await callback.message.edit_text(
        "📢 <b>تبلیغ جدید</b>\n\nعنوان تبلیغ را وارد کنید:",
        reply_markup=cancel_button()
    )
    await callback.answer()


@router.message(AdsCreateState.waiting_for_title)
async def handle_ad_title(message: Message, state: FSMContext) -> None:
    await state.update_data(ad_title=message.text.strip())
    await state.set_state(AdsCreateState.waiting_for_content)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📝 متنی", callback_data="ad_type:text"),
        InlineKeyboardButton(text="🖼️ بنری", callback_data="ad_type:banner"),
    )
    builder.row(
        InlineKeyboardButton(text="🔘 دکمه‌ای", callback_data="ad_type:button"),
        InlineKeyboardButton(text="❌ لغو", callback_data="cancel"),
    )

    await message.reply(
        "نوع تبلیغ را انتخاب کنید:",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.startswith("ad_type:"))
async def handle_ad_type(callback: CallbackQuery, state: FSMContext) -> None:
    ad_type = callback.data.split(":")[1]
    await state.update_data(ad_type=ad_type)
    await state.set_state(AdsCreateState.waiting_for_content)

    await callback.message.edit_text(
        "محتوای تبلیغ را وارد کنید (متن یا فایل):",
        reply_markup=cancel_button()
    )
    await callback.answer()


@router.message(AdsCreateState.waiting_for_content)
async def handle_ad_content(
    message: Message, state: FSMContext, session: AsyncSession, db_user
) -> None:
    data = await state.get_data()
    ads_repo = AdsRepository(session)

    content = {
        "title": data.get("ad_title", "تبلیغ جدید"),
        "ad_type": data.get("ad_type", "text"),
        "text": message.text or message.caption,
        "photo_file_id": message.photo[-1].file_id if message.photo else None,
        "created_by": db_user.telegram_id,
        "is_active": True,
        "show_in_rotation": True,
    }

    ad = await ads_repo.create(**content)
    await state.clear()

    await message.reply(
        f"✅ <b>تبلیغ با موفقیت ذخیره شد!</b>\n\n"
        f"🆔 شناسه: {ad.id}\n"
        f"📛 عنوان: {ad.title}\n"
        f"📂 نوع: {ad.ad_type}"
    )


@router.callback_query(F.data == "ads:list")
async def show_ads_list(callback: CallbackQuery, session: AsyncSession) -> None:
    ads_repo = AdsRepository(session)
    ads = await ads_repo.get_all()

    if not ads:
        await callback.message.edit_text(
            "📢 <b>تبلیغات</b>\n\nهیچ تبلیغی ثبت نشده است.",
            reply_markup=back_button("admin:ads")
        )
    else:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        text = f"📢 <b>لیست تبلیغات ({len(ads)} عدد)</b>\n\n"
        for ad in ads:
            status = "🟢" if ad.is_active else "🔴"
            text += f"{status} [{ad.id}] {ad.title} ({ad.ad_type})\n"
            builder.row(
                InlineKeyboardButton(
                    text=f"{'🟢' if ad.is_active else '🔴'} {ad.title}",
                    callback_data=f"ad:view:{ad.id}"
                )
            )
        builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin:ads"))
        await callback.message.edit_text(text, reply_markup=builder.as_markup())

    await callback.answer()
