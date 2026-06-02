"""
کیبوردهای کاربر - کاملاً فارسی
"""

from typing import List, Optional
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def user_main_menu() -> ReplyKeyboardMarkup:
    """منوی اصلی کاربر (Reply Keyboard)"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📁 فولدرها"),
        KeyboardButton(text="🔍 جستجو"),
    )
    builder.row(
        KeyboardButton(text="📥 دانلودهای من"),
        KeyboardButton(text="👤 پروفایل من"),
    )
    builder.row(
        KeyboardButton(text="📞 پشتیبانی"),
        KeyboardButton(text="ℹ️ درباره ربات"),
    )
    return builder.as_markup(resize_keyboard=True, persistent=True)


def user_profile_kb(user_id: int) -> InlineKeyboardMarkup:
    """کیبورد پروفایل کاربر"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 آمار من", callback_data="profile:stats"),
        InlineKeyboardButton(text="📥 دانلودهایم", callback_data="profile:downloads"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu:main"),
    )
    return builder.as_markup()


def folders_list_kb(folders: List[dict]) -> InlineKeyboardMarkup:
    """کیبورد لیست فولدرها"""
    builder = InlineKeyboardBuilder()
    for folder in folders:
        builder.row(
            InlineKeyboardButton(
                text=f"{folder.get('icon', '📁')} {folder['name']} ({folder.get('media_count', 0)})",
                callback_data=f"folder:open:{folder['id']}"
            )
        )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="menu:main"),
    )
    return builder.as_markup()


def media_list_kb(
    media_items: List[dict],
    folder_id: Optional[int] = None,
    page: int = 1,
    total_pages: int = 1
) -> InlineKeyboardMarkup:
    """کیبورد لیست رسانه‌ها"""
    builder = InlineKeyboardBuilder()

    for item in media_items:
        type_icon = {
            "photo": "🖼️", "video": "🎬", "audio": "🎵",
            "document": "📄", "animation": "🎞️", "voice": "🔊"
        }.get(item.get("media_type", ""), "📁")

        builder.row(
            InlineKeyboardButton(
                text=f"{type_icon} {item.get('file_name', 'فایل بدون نام')[:40]}",
                callback_data=f"media:view:{item['id']}"
            )
        )

    # دکمه‌های صفحه‌بندی
    if total_pages > 1:
        nav_buttons = []
        if page > 1:
            nav_buttons.append(
                InlineKeyboardButton(text="⬅️ قبلی", callback_data=f"folder:{folder_id}:page:{page-1}")
            )
        nav_buttons.append(
            InlineKeyboardButton(text=f"📄 {page}/{total_pages}", callback_data="noop")
        )
        if page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(text="بعدی ➡️", callback_data=f"folder:{folder_id}:page:{page+1}")
            )
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu:folders"),
    )
    return builder.as_markup()


def download_link_kb(token: str, has_ads: bool = False) -> InlineKeyboardMarkup:
    """کیبورد لینک دانلود"""
    builder = InlineKeyboardBuilder()

    if has_ads:
        builder.row(
            InlineKeyboardButton(text="👁️ مشاهده تبلیغ", callback_data=f"dl:view_ad:{token}"),
        )

    builder.row(
        InlineKeyboardButton(text="📥 دریافت فایل", callback_data=f"dl:download:{token}"),
    )
    return builder.as_markup()


def force_join_kb(channels: List[dict], token: Optional[str] = None) -> InlineKeyboardMarkup:
    """کیبورد عضویت اجباری"""
    builder = InlineKeyboardBuilder()

    for channel in channels:
        invite = channel.get("invite_link") or f"https://t.me/{channel.get('username', '')}"
        builder.row(
            InlineKeyboardButton(
                text=f"📢 عضویت در {channel.get('title', 'کانال')}",
                url=invite
            )
        )

    verify_data = f"fj:verify:{token}" if token else "fj:verify"
    builder.row(
        InlineKeyboardButton(text="✅ بررسی عضویت", callback_data=verify_data),
    )
    return builder.as_markup()


def view_confirm_kb(token: str) -> InlineKeyboardMarkup:
    """کیبورد تأیید مشاهده"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ مشاهده کردم، دریافت فایل", callback_data=f"dl:confirmed:{token}"),
    )
    return builder.as_markup()


def reaction_kb(media_id: int) -> InlineKeyboardMarkup:
    """کیبورد واکنش به رسانه"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👍 پسندیدم", callback_data=f"react:like:{media_id}"),
        InlineKeyboardButton(text="👎 نپسندیدم", callback_data=f"react:dislike:{media_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="📥 دانلود", callback_data=f"media:download:{media_id}"),
        InlineKeyboardButton(text="🔗 اشتراک‌گذاری", callback_data=f"media:share:{media_id}"),
    )
    return builder.as_markup()


def pagination_kb(
    current_page: int,
    total_pages: int,
    base_callback: str
) -> InlineKeyboardMarkup:
    """کیبورد صفحه‌بندی عمومی"""
    builder = InlineKeyboardBuilder()
    buttons = []
    if current_page > 1:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"{base_callback}:{current_page-1}"))
    buttons.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="noop"))
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"{base_callback}:{current_page+1}"))
    builder.row(*buttons)
    return builder.as_markup()


def support_kb() -> InlineKeyboardMarkup:
    """کیبورد پشتیبانی"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❓ سؤال فنی", callback_data="support:technical"),
        InlineKeyboardButton(text="🐛 گزارش مشکل", callback_data="support:bug"),
    )
    builder.row(
        InlineKeyboardButton(text="💡 پیشنهاد", callback_data="support:suggestion"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu:main"),
    )
    return builder.as_markup()
