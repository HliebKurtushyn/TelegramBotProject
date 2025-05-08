import asyncio
from asyncio.exceptions import CancelledError
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN as TOKEN
from mainFiles.handlers import dp
from helpers.commands import BOT_COMMANDS


async def main() -> None:
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    await bot.set_my_commands(BOT_COMMANDS)
    
    try:
        print("---Bot started---")
        await dp.start_polling(bot)
    except (KeyboardInterrupt, CancelledError):
        print("---Bot stopped---")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
