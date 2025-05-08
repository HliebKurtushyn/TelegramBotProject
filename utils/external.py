import logging
import functools
from datetime import datetime
from aiogram.types import Message, CallbackQuery

def async_log_function_call(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        obj = args[0]

        username = "Unknown"
        content = "Unknown content"

        if isinstance(obj, Message):
            username = obj.from_user.username
            content = obj.text
        elif isinstance(obj, CallbackQuery):
            username = obj.from_user.username
            content = obj.data

        time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open("messages.log", 'a', encoding="utf8") as file:
            file.write(f"{time_now} | {username} | {content}\n")

        logger = logging.getLogger(__name__)
        logger.info(f"Відбувся виклик функції '{func.__name__}'")
        return await func(*args, **kwargs)
    return wrapper


