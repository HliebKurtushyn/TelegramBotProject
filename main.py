import asyncio
from asyncio.exceptions import CancelledError
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN as TOKEN
from handlers import dp

async def main() -> None:
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, CancelledError):
        print("---Bot stopped---")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())