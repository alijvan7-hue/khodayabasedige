"""
کیبوردهای پنل ادمین - کاملاً فارسی
"""

from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def admin_main_menu() -> InlineKeyboardMarkup:
    """منوی اصلی پنل ادمین"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📁 مدیریت رسانه", callback_data="admin:media"),
        InlineKeyboardButton(text="👥 مدیریت کاربران", callback_data="admin:users"),
    )
    builder.row(
        InlineKeyboardButton(text="📣 ارسال همگانی", callback_data="admin:broadcast"),
        InlineKeyboardButton(text="📢 مدیریت تبلیغات", callback_data="admin:ads"),
    )
    builder.row(
        InlineKeyboardButton(text="🔒 عضویت اجباری", callback_data="admin:force_join"),
        InlineKeyboardButton(text="📊 آمار ربات", callback_data="admin:stats"),
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ تنظیمات ربات", callback_data="admin:settings"),
        InlineKeyboardButton(text="💾 پشتیبان‌گیری", callback_data="admin:backup"),
    )
    builder.row(
        InlineKeyboardButton(text="📋 لاگ‌های سیستم", callback_data="admin:logs"),
        InlineKeyboardButton(text="👑 مدیریت ادمین‌ها", callback_data="admin:admins"),
    )
    return builder.as_markup()


def media_management_menu() -> InlineKeyboardMarkup:
    """منوی مدیریت رسانه"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📤 آپلود رسانه", callback_data="media:upload"),
        InlineKeyboardButton(text="📂 فولدرها", callback_data="media:folders"),
    )
    builder.row(
        InlineKeyboardButton(text="🔍 جستجوی رسانه", callback_data="media:search"),
        InlineKeyboardButton(text="📊 آمار رسانه", callback_data="media:stats"),
    )
    builder.row(
        InlineKeyboardButton(text="🖼️ مدیریت تامبنیل", callback_data="media:thumbnail"),
        InlineKeyboardButton(text="🔗 لینک‌های دانلود", callback_data="media:links"),
    )
    builder.row(
        InlineKeyboardButton(text="🗑️ حذف خودکار", callback_data="media:auto_delete"),
        InlineKeyboardButton(text="🔤 فیلتر متن", callback_data="media:text_filter"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin:main"),
    )
    return builder.as_markup()


def users_management_menu() -> InlineKeyboardMarkup:
    """منوی مدیریت کاربران"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔍 جستجوی کاربر", callback_data="users:search"),
        InlineKeyboardButton(text="📋 لیست کاربران", callback_data="users:list"),
    )
    builder.row(
        InlineKeyboardButton(text="🚫 کاربران بن‌شده", callback_data="users:banned"),
        InlineKeyboardButton(text="👑 ادمین‌ها", callback_data="users:admins"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 آمار کاربران", callback_data="users:stats"),
        InlineKeyboardButton(text="🏷️ برچسب‌گذاری", callback_data="users:labels"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin:main"),
    )
    return builder.as_markup()


def user_profile_menu(user_id: int, is_banned: bool = False, is_admin: bool = False) -> InlineKeyboardMarkup:
    """منوی پروفایل کاربر"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 آمار کاربر", callback_data=f"user:stats:{user_id}"),
        InlineKeyboardButton(text="📝 تاریخچه", callback_data=f"user:history:{user_id}"),
    )
    if is_banned:
        builder.row(
            InlineKeyboardButton(text="✅ رفع بن", callback_data=f"user:unban:{user_id}"),
        )
    else:
        builder.row(
            InlineKeyboardButton(text="🚫 بن کاربر", callback_data=f"user:ban:{user_id}"),
        )
    if is_admin:
        builder.row(
            InlineKeyboardButton(text="❌ حذف از ادمین", callback_data=f"user:remove_admin:{user_id}"),
        )
    else:
        builder.row(
            InlineKeyboardButton(text="⬆️ ارتقا به ادمین", callback_data=f"user:make_admin:{user_id}"),
        )
    builder.row(
        InlineKeyboardButton(text="📤 ارسال پیام", callback_data=f"user:message:{user_id}"),
        InlineKeyboardButton(text="🏷️ برچسب", callback_data=f"user:label:{user_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin:users"),
    )
    return builder.as_markup()


def broadcast_menu() -> InlineKeyboardMarkup:
    """منوی ارسال همگانی"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📝 ارسال جدید", callback_data="broadcast:new"),
        InlineKeyboardButton(text="↩️ فوروارد", callback_data="broadcast:forward"),
    )
    builder.row(
        InlineKeyboardButton(text="⏰ ارسال زمان‌بندی‌شده", callback_data="broadcast:schedule"),
        InlineKeyboardButton(text="📋 لیست ارسال‌ها", callback_data="broadcast:list"),
    )
    builder.row(
        InlineKeyboardButton(text="⏹️ توقف ارسال جاری", callback_data="broadcast:stop"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin:main"),
    )
    return builder.as_markup()


def ads_menu() -> InlineKeyboardMarkup:
    """منوی مدیریت تبلیغات"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ تبلیغ جدید", callback_data="ads:new"),
        InlineKeyboardButton(text="📋 لیست تبلیغات", callback_data="ads:list"),
    )
    builder.row(
        InlineKeyboardButton(text="🔄 تبلیغات چرخشی", callback_data="ads:rotation"),
        InlineKeyboardButton(text="⏰ تبلیغات زمان‌بندی", callback_data="ads:schedule"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 آمار تبلیغات", callback_data="ads:stats"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin:main"),
    )
    return builder.as_markup()


def force_join_menu(is_enabled: bool = False) -> InlineKeyboardMarkup:
    """منوی عضویت اجباری"""
    builder = InlineKeyboardBuilder()
    status_text = "🔴 غیرفعال کردن" if is_enabled else "🟢 فعال کردن"
    builder.row(
        InlineKeyboardButton(text=status_text, callback_data="fj:toggle"),
    )
    builder.row(
        InlineKeyboardButton(text="➕ افزودن کانال", callback_data="fj:add_channel"),
        InlineKeyboardButton(text="📋 لیست کانال‌ها", callback_data="fj:list"),
    )
    builder.row(
        InlineKeyboardButton(text="🗑️ حذف کانال", callback_data="fj:remove_channel"),
        InlineKeyboardButton(text="✅ تست عضویت", callback_data="fj:test"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin:main"),
    )
    return builder.as_markup()


def settings_menu() -> InlineKeyboardMarkup:
    """منوی تنظیمات"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💬 پیام‌های ربات", callback_data="settings:messages"),
        InlineKeyboardButton(text="🔤 فیلتر متن", callback_data="settings:filters"),
    )
    builder.row(
        InlineKeyboardButton(text="🗑️ حذف خودکار", callback_data="settings:auto_delete"),
        InlineKeyboardButton(text="🖼️ تامبنیل", callback_data="settings:thumbnail"),
    )
    builder.row(
        InlineKeyboardButton(text="🛡️ امنیت و محدودیت", callback_data="settings:security"),
        InlineKeyboardButton(text="📁 مدیریت فولدر", callback_data="settings:folders"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin:main"),
    )
    return builder.as_markup()


def stats_menu() -> InlineKeyboardMarkup:
    """منوی آمار"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👥 آمار کاربران", callback_data="stats:users"),
        InlineKeyboardButton(text="📁 آمار رسانه", callback_data="stats:media"),
    )
    builder.row(
        InlineKeyboardButton(text="📥 آمار دانلودها", callback_data="stats:downloads"),
        InlineKeyboardButton(text="📊 نمودار فعالیت", callback_data="stats:activity"),
    )
    builder.row(
        InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="stats:refresh"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin:main"),
    )
    return builder.as_markup()


def backup_menu() -> InlineKeyboardMarkup:
    """منوی پشتیبان‌گیری"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💾 پشتیبان از دیتابیس", callback_data="backup:database"),
        InlineKeyboardButton(text="📁 پشتیبان از رسانه", callback_data="backup:media"),
    )
    builder.row(
        InlineKeyboardButton(text="🗂️ پشتیبان کامل", callback_data="backup:full"),
        InlineKeyboardButton(text="📋 لیست پشتیبان‌ها", callback_data="backup:list"),
    )
    builder.row(
        InlineKeyboardButton(text="↩️ بازیابی پشتیبان", callback_data="backup:restore"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin:main"),
    )
    return builder.as_markup()


def confirm_action(action: str, extra: str = "") -> InlineKeyboardMarkup:
    """کیبورد تأیید اقدام"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ تایید", callback_data=f"confirm:{action}:{extra}"),
        InlineKeyboardButton(text="❌ لغو", callback_data="cancel"),
    )
    return builder.as_markup()


def media_item_menu(media_id: int) -> InlineKeyboardMarkup:
    """منوی مدیریت یک رسانه"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ ویرایش کپشن", callback_data=f"media:edit_caption:{media_id}"),
        InlineKeyboardButton(text="📂 جابجایی فولدر", callback_data=f"media:move:{media_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🔗 ساخت لینک", callback_data=f"media:create_link:{media_id}"),
        InlineKeyboardButton(text="🖼️ تامبنیل", callback_data=f"media:thumbnail:{media_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 آمار", callback_data=f"media:stats:{media_id}"),
        InlineKeyboardButton(text="🗑️ حذف", callback_data=f"media:delete:{media_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin:media"),
    )
    return builder.as_markup()


def folder_menu(folder_id: int) -> InlineKeyboardMarkup:
    """منوی مدیریت فولدر"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ ویرایش نام", callback_data=f"folder:rename:{folder_id}"),
        InlineKeyboardButton(text="📊 آمار فولدر", callback_data=f"folder:stats:{folder_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="📋 محتوای فولدر", callback_data=f"folder:contents:{folder_id}"),
        InlineKeyboardButton(text="🗑️ حذف فولدر", callback_data=f"folder:delete:{folder_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="media:folders"),
    )
    return builder.as_markup()


def cancel_button() -> InlineKeyboardMarkup:
    """دکمه لغو"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ لغو", callback_data="cancel"),
    )
    return builder.as_markup()


def back_button(callback: str = "admin:main") -> InlineKeyboardMarkup:
    """دکمه بازگشت"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data=callback),
    )
    return builder.as_markup()
