import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.config import config
from app.database import init_db
from app.handlers import router


async def main() -> None:
    """Main function to run the bot."""
    logging.basicConfig(level=logging.INFO)
    
    if not config.BOT_TOKEN:
        logging.error("BOT_TOKEN is not set in .env file")
        return
    
    # Initialize database
    init_db()
    logging.info("Database initialized")
    
    # Create bot and dispatcher
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Include router
    dp.include_router(router)
    
    # Start polling
    logging.info("Bot started polling...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
