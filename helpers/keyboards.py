from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class FilmCallback(CallbackData, prefix="film", sep=";"):
    id: int


def films_keyboard_markup(films_list: list[dict], offset: int | None = None, skip: int | None = None):
    # """
    # Створює клавіатуру на основі отриманого списку фільмів
    # Приклад використання
    # >>> await message.answer(
    #         text="Some text",
    #         reply_markup=films_keyboard_markup(films_list)
    #     )
    # """

    # Створюємо та налаштовуємо клавіатуру
    builder = InlineKeyboardBuilder()

    for index, film_data in enumerate(films_list):
        # Створюємо об'єкт CallbackData
        callback_data = FilmCallback(id=index, **film_data)
        # Додаємо кнопку до клавіатури
        builder.button(
            text=f"{film_data["name"]}",
            callback_data=callback_data.pack()
        )
    # Повертаємо клавіатуру у вигляді InlineKeyboardMarkup
    builder.adjust(1, repeat=True)
    return builder.as_markup()

def filter_criteria_markup():
    buttons = [
        [InlineKeyboardButton(text="За назвою", callback_data="search_by:title")],
        [InlineKeyboardButton(text="За жанром", callback_data="search_by:genre")],
        [InlineKeyboardButton(text="За актором", callback_data="search_by:actors")],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
    