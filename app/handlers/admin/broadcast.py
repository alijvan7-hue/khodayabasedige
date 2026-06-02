"""
هندلر ارسال همگانی
"""

import logging
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.admin_kb import broadcast_menu, cancel_button, back_button, confirm_action
from app.repositories.user_repo import UserRepository
from app.repositories.broadcast_repo import BroadcastRepository

logger = logging.getLogger(__name__)
router = Router(name="admin_broadcast")

# متغیر برای کنترل توقف ارسال
_broadcast_running = {}


class BroadcastState(StatesGroup):
    """وضعیت‌های ارسال همگانی"""
    waiting_for_content = State()
    waiting_for_confirmation = State()
    waiting_for_forward = State()


@router.callback_query(F.data == "broadcast:new")
async def start_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    """شروع ارسال همگانی جدید"""
    await state.set_state(BroadcastState.waiting_for_content)
    await callback.message.edit_text(
        "📣 <b>ارسال همگانی جدید</b>\n\n"
        "پیام خود را ارسال کنید:\n"
        "• می‌توانید متن، عکس، ویدیو یا ترکیب آن‌ها ارسال کنید\n"
        "• کپشن عکس/ویدیو به عنوان متن ارسال می‌شود\n\n"
        "⚠️ این پیام برای <b>همه کاربران</b> ارسال می‌شود!",
        reply_markup=cancel_button()
    )
    await callback.answer()


@router.message(BroadcastState.waiting_for_content)
async def handle_broadcast_content(
    message: Message, state: FSMContext, session: AsyncSession, db_user
) -> None:
    """دریافت محتوای ارسال همگانی"""
    user_repo = UserRepository(session)
    total_users = await user_repo.count_active()

    # ذخیره محتوا
    content = {
        "text": message.text or message.caption,
        "photo_file_id": message.photo[-1].file_id if message.photo else None,
        "video_file_id": message.video.file_id if message.video else None,
        "document_file_id": message.document.file_id if message.document else None,
    }
    await state.update_data(broadcast_content=content)
    await state.set_state(BroadcastState.waiting_for_confirmation)

    # نمایش پیش‌نمایش
    await message.reply(
        f"📋 <b>پیش‌نمایش ارسال همگانی</b>\n\n"
        f"👥 تعداد گیرندگان: <b>{total_users:,}</b> کاربر\n\n"
        f"آیا از ارسال این پیام مطمئن هستید؟",
        reply_markup=confirm_action("broadcast_send", "all")
    )


@router.callback_query(F.data == "confirm:broadcast_send:all")
async def execute_broadcast(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession,
    db_user, bot: Bot
) -> None:
    """اجرای ارسال همگانی"""
    data = await state.get_data()
    content = data.get("broadcast_content", {})
    await state.clear()

    if not content:
        await callback.answer("❌ خطا: محتوا یافت نشد", show_alert=True)
        return

    # ذخیره در دیتابیس
    broadcast_repo = BroadcastRepository(session)
    broadcast = await broadcast_repo.create(
        broadcast_type="normal",
        text=content.get("text"),
        photo_file_id=content.get("photo_file_id"),
        video_file_id=content.get("video_file_id"),
        document_file_id=content.get("document_file_id"),
        created_by=db_user.telegram_id,
        status="running"
    )

    await callback.message.edit_text(
        f"📣 <b>ارسال همگانی شروع شد!</b>\n\n"
        f"🆔 شناسه: {broadcast.id}\n"
        f"⏳ در حال ارسال...\n\n"
        "برای توقف از /stop_broadcast استفاده کنید."
    )
    await callback.answer()

    # ارسال در background
    asyncio.create_task(
        _run_broadcast(bot, broadcast.id, content, session, db_user.telegram_id)
    )


async def _run_broadcast(
    bot: Bot, broadcast_id: int, content: dict,
    session: AsyncSession, admin_id: int
) -> None:
    """اجرای ارسال همگانی در background"""
    _broadcast_running[broadcast_id] = True

    success_count = 0
    failed_count = 0
    blocked_count = 0

    try:
        user_repo = UserRepository(session)
        broadcast_repo = BroadcastRepository(session)

        users = await user_repo.get_all_active()
        total = len(users)

        for i, user in enumerate(users):
            if not _broadcast_running.get(broadcast_id):
                break

            try:
                if content.get("photo_file_id"):
                    await bot.send_photo(
                        chat_id=user.telegram_id,
                        photo=content["photo_file_id"],
                        caption=content.get("text")
                    )
                elif content.get("video_file_id"):
                    await bot.send_video(
                        chat_id=user.telegram_id,
                        video=content["video_file_id"],
                        caption=content.get("text")
                    )
                elif content.get("document_file_id"):
                    await bot.send_document(
                        chat_id=user.telegram_id,
                        document=content["document_file_id"],
                        caption=content.get("text")
                    )
                elif content.get("text"):
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=content["text"]
                    )

                success_count += 1

            except Exception as e:
                error_str = str(e).lower()
                if "blocked" in error_str or "deactivated" in error_str:
                    blocked_count += 1
                else:
                    failed_count += 1

            # تأخیر برای جلوگیری از flood
            if (i + 1) % 25 == 0:
                await asyncio.sleep(1)

        # ارسال گزارش به ادمین
        status = "متوقف شد" if not _broadcast_running.get(broadcast_id) else "کامل شد"
        await bot.send_message(
            chat_id=admin_id,
            text=(
                f"📊 <b>گزارش ارسال همگانی #{broadcast_id}</b>\n\n"
                f"📤 وضعیت: {status}\n"
                f"👥 کل گیرندگان: {total}\n"
                f"✅ موفق: {success_count}\n"
                f"❌ ناموفق: {failed_count}\n"
                f"🚫 بلاک کرده: {blocked_count}"
            )
        )

        # بروزرسانی دیتابیس
        await broadcast_repo.update_stats(
            broadcast_id,
            success_count=success_count,
            failed_count=failed_count,
            blocked_count=blocked_count,
            status="completed" if _broadcast_running.get(broadcast_id) else "cancelled"
        )

    except Exception as e:
        logger.error(f"خطا در ارسال همگانی: {e}")
    finally:
        _broadcast_running.pop(broadcast_id, None)


@router.callback_query(F.data == "broadcast:stop")
async def stop_broadcast(callback: CallbackQuery) -> None:
    """توقف ارسال جاری"""
    if not _broadcast_running:
        await callback.answer("هیچ ارسالی در حال اجرا نیست", show_alert=True)
        return

    # توقف تمام ارسال‌های جاری
    for broadcast_id in list(_broadcast_running.keys()):
        _broadcast_running[broadcast_id] = False

    await callback.message.edit_text(
        "⏹️ <b>دستور توقف ارسال ارسال شد.</b>\n\n"
        "ارسال‌های جاری متوقف خواهند شد.",
        reply_markup=back_button("admin:broadcast")
    )
    await callback.answer("متوقف شد")
