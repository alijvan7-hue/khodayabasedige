"""
نقطه ورود اصلی ربات آپلودر رسانه تلگرام
Telegram Media Uploader Bot - Main Entry Point
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from app.database import engine, Base, AsyncSessionLocal
from app.redis_client import get_redis
from app.handlers import setup_routers
from app.middlewares import setup_middlewares
from app.utils.scheduler import setup_scheduler
from app.repositories.user_repo import UserRepository
from app.repositories.setting_repo import SettingRepository
from config import settings

# تنظیم لاگ
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


async def create_tables() -> None:
    """ایجاد جداول دیتابیس"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ جداول دیتابیس آماده شدند")
    except Exception as e:
        logger.error(f"❌ خطا در ایجاد جداول: {e}")
        raise


async def on_startup(bot: Bot) -> None:
    """اقدامات هنگام استارت ربات"""
    logger.info("🚀 ربات در حال راه‌اندازی...")

    # ایجاد جداول
    await create_tables()

    # بررسی و ثبت ادمین‌های اولیه
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        setting_repo = SettingRepository(session)

        # ایجاد تنظیمات پیش‌فرض
        await setting_repo.initialize_defaults()

        # ثبت مالک
        owner = await user_repo.get_by_telegram_id(settings.OWNER_ID)
        if not owner:
            await user_repo.create_or_update(
                telegram_id=settings.OWNER_ID,
                username="owner",
                full_name="مالک ربات",
                is_admin=True,
                role="owner"
            )
            logger.info(f"✅ مالک ربات ثبت شد: {settings.OWNER_ID}")

        await session.commit()

    # اطلاع‌رسانی به ادمین‌ها
    admin_ids = [settings.OWNER_ID] + settings.ADMIN_IDS
    for admin_id in set(admin_ids):
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=(
                    "🟢 <b>ربات با موفقیت راه‌اندازی شد!</b>\n\n"
                    f"📛 نام: {settings.BOT_NAME}\n"
                    f"🔢 نسخه: {settings.BOT_VERSION}\n"
                    f"🗄️ دیتابیس: متصل ✅\n"
                    f"⚡ Redis: متصل ✅\n\n"
                    "از /admin برای ورود به پنل مدیریت استفاده کنید."
                )
            )
        except Exception as e:
            logger.warning(f"⚠️ نمی‌توان به ادمین {admin_id} پیام ارسال کرد: {e}")

    logger.info(f"✅ ربات {settings.BOT_NAME} v{settings.BOT_VERSION} راه‌اندازی شد")


async def on_shutdown(bot: Bot) -> None:
    """اقدامات هنگام خاموش شدن ربات"""
    logger.info("🔴 ربات در حال خاموش شدن...")

    # اطلاع‌رسانی به ادمین‌ها
    for admin_id in [settings.OWNER_ID]:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text="🔴 <b>ربات خاموش شد!</b>"
            )
        except Exception:
            pass

    logger.info("✅ ربات با موفقیت خاموش شد")


async def main() -> None:
    """تابع اصلی"""
    logger.info("⚡ شروع بارگذاری ربات...")

    # اتصال به Redis
    redis = await get_redis()
    storage = RedisStorage(redis=redis)

    # ساخت Bot
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # ساخت Dispatcher
    dp = Dispatcher(storage=storage)

    # ثبت رویدادهای lifecycle
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # تنظیم middleware‌ها
    setup_middlewares(dp)

    # تنظیم روترها
    setup_routers(dp)

    # تنظیم زمان‌بند
    scheduler = setup_scheduler(bot)
    scheduler.start()

    logger.info("🎯 ربات آماده دریافت پیام است...")

    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True
        )
    finally:
        scheduler.shutdown()
        await bot.session.close()
        await redis.aclose()
        logger.info("✅ تمام اتصالات بسته شدند")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⛔ ربات توسط کاربر متوقف شد")
    except Exception as e:
        logger.critical(f"💥 خطای بحرانی: {e}", exc_info=True)
        sys.exit(1)
