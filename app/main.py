import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.handlers import router
from app.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
RUN_MODE = os.getenv("RUN_MODE", "polling")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
PORT = int(os.getenv("PORT", 8080))
WEBHOOK_PATH = "/webhook"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(router)


async def health(request: web.Request) -> web.Response:
    return web.Response(text="OK")


async def on_startup(app: web.Application) -> None:
    init_db()
    if WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL,
            secret_token=WEBHOOK_SECRET or None,
            drop_pending_updates=True,
        )
        logger.info(f"Webhook set to {WEBHOOK_URL}")


async def on_shutdown(app: web.Application) -> None:
    await bot.session.close()


def main() -> None:
    logger.info(f"Starting in {RUN_MODE} mode on port {PORT}")

    if RUN_MODE == "webhook":
        app = web.Application()
        app.router.add_get("/", health)
        app.router.add_get("/health", health)

        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=WEBHOOK_SECRET or None,
        )
        webhook_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        web.run_app(app, host="0.0.0.0", port=PORT)
    else:
        init_db()
        logger.info("Bot started polling...")
        asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()