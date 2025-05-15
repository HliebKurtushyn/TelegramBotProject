from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand

FILMS_COMMAND = Command('films')
START_COMMAND = Command('start')
FILM_CREATE_COMMAND = Command("create_film")

FILMS_BOT_COMMAND = BotCommand(
    command='films', description="Перегляд списку фільмів")
START_BOT_COMMAND = BotCommand(command='start', description="Почати розмову")

BOT_COMMANDS = [
    BotCommand(command="start", description="Почати розмову"),
    BotCommand(command="films", description="Перегляд списку фільмів"),
    BotCommand(command="search_movie", description="Пошук фільма за назвою"),
    BotCommand(command="recommend_movie", description="Рекомендації"),
    BotCommand(command="create_film", description="Додати новий фільм"),
    BotCommand(command="delete_movie", description="Видалити фільм"),
    BotCommand(command="edit_movie", description="Редагувати фільм"),
    BotCommand(command="filter_movies", description="Пошук фільма за жанром"),
    BotCommand(command="rate_movie", description="Оцінити фільм"),
]
