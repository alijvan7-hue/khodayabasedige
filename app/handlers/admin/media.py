"""
هندلر مدیریت رسانه (ادمین)
"""

import logging
import uuid
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.admin_kb import (
    media_management_menu, media_item_menu, confirm_action,
    cancel_button, back_button, admin_main_menu
)
from app.keyboards.user_kb import media_list_kb
from app.repositories.media_repo import MediaRepository
from app.repositories.folder_repo import FolderRepository
from app.services.media_service import MediaService

logger = logging.getLogger(__name__)
router = Router(name="admin_media")


class MediaUploadState(StatesGroup):
    """وضعیت‌های آپلود رسانه"""
    waiting_for_media = State()
    waiting_for_caption = State()
    waiting_for_folder = State()


class MediaEditState(StatesGroup):
    """وضعیت‌های ویرایش رسانه"""
    waiting_for_caption = State()


class FolderCreateState(StatesGroup):
    """وضعیت‌های ایجاد فولدر"""
    waiting_for_name = State()
    waiting_for_icon = State()


@router.callback_query(F.data == "media:upload")
async def start_upload(callback: CallbackQuery, state: FSMContext) -> None:
    """شروع فرآیند آپلود رسانه"""
    await state.set_state(MediaUploadState.waiting_for_media)
    await callback.message.edit_text(
        "📤 <b>آپلود رسانه</b>\n\n"
        "فایل خود را ارسال کنید:\n"
        "• 🖼️ عکس\n"
        "• 🎬 ویدیو\n"
        "• 🎵 صدا\n"
        "• 📄 سند\n"
        "• 🎞️ GIF\n\n"
        "می‌توانید چندین فایل به صورت گروهی ارسال کنید.",
        reply_markup=cancel_button()
    )
    await callback.answer()


@router.message(MediaUploadState.waiting_for_media, F.media_group_id)
async def handle_media_group(message: Message, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    """دریافت گروه رسانه"""
    data = await state.get_data()
    group_id = message.media_group_id

    # جمع‌آوری تمام فایل‌های گروه
    group_messages = data.get("group_messages", [])
    group_messages.append(message.message_id)

    await state.update_data(
        group_id=group_id,
        group_messages=group_messages
    )

    # پردازش با تأخیر کوتاه برای دریافت همه فایل‌ها
    if len(group_messages) == 1:
        import asyncio
        await asyncio.sleep(1)
        # پردازش گروه
        await process_media_group(message, state, session)


async def process_media_group(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """پردازش گروه رسانه"""
    media_service = MediaService(session)
    data = await state.get_data()

    await message.reply(
        f"✅ <b>{len(data.get('group_messages', []))} فایل دریافت شد!</b>\n\n"
        "کپشن برای تمام فایل‌ها وارد کنید (یا /skip برای رد کردن):",
        reply_markup=cancel_button()
    )
    await state.set_state(MediaUploadState.waiting_for_caption)


@router.message(MediaUploadState.waiting_for_media)
async def handle_single_media(
    message: Message, state: FSMContext, session: AsyncSession, db_user
) -> None:
    """دریافت رسانه تکی"""
    media_service = MediaService(session)

    # تشخیص نوع رسانه
    media_data = None
    media_type = None

    if message.photo:
        photo = message.photo[-1]
        media_data = {
            "file_id": photo.file_id,
            "file_unique_id": photo.file_unique_id,
            "media_type": "photo",
            "file_size": photo.file_size,
            "width": photo.width,
            "height": photo.height,
        }
        media_type = "عکس"

    elif message.video:
        video = message.video
        media_data = {
            "file_id": video.file_id,
            "file_unique_id": video.file_unique_id,
            "media_type": "video",
            "file_name": video.file_name,
            "file_size": video.file_size,
            "mime_type": video.mime_type,
            "duration": video.duration,
            "width": video.width,
            "height": video.height,
        }
        media_type = "ویدیو"

    elif message.audio:
        audio = message.audio
        media_data = {
            "file_id": audio.file_id,
            "file_unique_id": audio.file_unique_id,
            "media_type": "audio",
            "file_name": audio.file_name,
            "file_size": audio.file_size,
            "mime_type": audio.mime_type,
            "duration": audio.duration,
        }
        media_type = "صدا"

    elif message.document:
        doc = message.document
        media_data = {
            "file_id": doc.file_id,
            "file_unique_id": doc.file_unique_id,
            "media_type": "document",
            "file_name": doc.file_name,
            "file_size": doc.file_size,
            "mime_type": doc.mime_type,
        }
        media_type = "سند"

    elif message.animation:
        anim = message.animation
        media_data = {
            "file_id": anim.file_id,
            "file_unique_id": anim.file_unique_id,
            "media_type": "animation",
            "file_name": anim.file_name,
            "file_size": anim.file_size,
            "mime_type": anim.mime_type,
            "duration": anim.duration,
            "width": anim.width,
            "height": anim.height,
        }
        media_type = "GIF"

    else:
        await message.reply(
            "❌ نوع فایل پشتیبانی نمی‌شود.\n"
            "لطفاً عکس، ویدیو، صدا، سند یا GIF ارسال کنید."
        )
        return

    if not media_data:
        return

    # ذخیره اطلاعات رسانه در state
    media_data["uploaded_by"] = db_user.telegram_id
    media_data["caption"] = message.caption
    await state.update_data(media_data=media_data)

    # ذخیره در دیتابیس
    unique_id = str(uuid.uuid4())[:8].upper()
    media_data["unique_id"] = unique_id

    media = await media_service.create_media(**media_data)

    # بروزرسانی آمار کاربر
    from app.repositories.user_repo import UserRepository
    user_repo = UserRepository(session)
    await user_repo.increment_uploads(db_user.telegram_id)

    await message.reply(
        f"✅ <b>{media_type} با موفقیت ذخیره شد!</b>\n\n"
        f"🆔 کد: <code>{media.unique_id}</code>\n"
        f"📁 اندازه: {media.file_size_human}\n\n"
        "می‌خواهید فایل را در فولدری قرار دهید؟",
        reply_markup=media_item_menu(media.id)
    )

    await state.clear()


@router.callback_query(F.data.startswith("media:delete:"))
async def confirm_delete_media(callback: CallbackQuery) -> None:
    """تأیید حذف رسانه"""
    media_id = callback.data.split(":")[2]
    await callback.message.edit_text(
        "⚠️ <b>آیا از حذف این رسانه مطمئن هستید؟</b>\n\n"
        "این عمل قابل بازگشت نیست!",
        reply_markup=confirm_action("delete_media", media_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm:delete_media:"))
async def delete_media(callback: CallbackQuery, session: AsyncSession) -> None:
    """حذف رسانه"""
    media_id = int(callback.data.split(":")[2])
    media_service = MediaService(session)

    success = await media_service.delete_media(media_id)

    if success:
        await callback.message.edit_text(
            "✅ <b>رسانه با موفقیت حذف شد.</b>",
            reply_markup=back_button("admin:media")
        )
        await callback.answer("حذف شد")
    else:
        await callback.answer("❌ خطا در حذف رسانه", show_alert=True)


@router.callback_query(F.data == "media:folders")
async def show_folders(callback: CallbackQuery, session: AsyncSession) -> None:
    """نمایش لیست فولدرها"""
    folder_repo = FolderRepository(session)
    folders = await folder_repo.get_all()

    if not folders:
        from app.keyboards.admin_kb import InlineKeyboardMarkup, InlineKeyboardButton
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="➕ ایجاد فولدر", callback_data="folder:create"),
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin:media"),
        )
        await callback.message.edit_text(
            "📂 <b>فولدرها</b>\n\nهیچ فولدری وجود ندارد.",
            reply_markup=builder.as_markup()
        )
    else:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        for folder in folders:
            builder.row(
                InlineKeyboardButton(
                    text=f"{folder.icon} {folder.name} ({folder.media_count})",
                    callback_data=f"folder:view:{folder.id}"
                )
            )
        builder.row(
            InlineKeyboardButton(text="➕ ایجاد فولدر", callback_data="folder:create"),
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin:media"),
        )
        await callback.message.edit_text(
            f"📂 <b>فولدرها ({len(folders)} عدد)</b>\n\nیک فولدر را انتخاب کنید:",
            reply_markup=builder.as_markup()
        )

    await callback.answer()
