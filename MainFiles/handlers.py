from aiogram import Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardRemove,
    URLInputFile,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from mainFiles.states import FilmForm, MovieStates, MovieRatingStates, MovieFilterStates
from utils.data import (
    get_films,
    add_film,
    delete_film_by_name,
    update_film_description,
    update_film_rating,
)
from utils.external import async_log_function_call
from helpers.keyboards import films_keyboard_markup, filter_criteria_markup, FilmCallback
from helpers.models import Film
from helpers.commands import (
    FILMS_COMMAND,
    START_COMMAND,
    FILM_CREATE_COMMAND,
)

# === ІНІЦІАЛІЗАЦІЯ ===
dp = Dispatcher()


# === СТАРТ ===
@dp.message(START_COMMAND)
@async_log_function_call
async def start(message: Message) -> None:
    await message.answer(
        f"Вітаю, {message.from_user.full_name}!\n"
        "Я перший бот Python розробника [ПІБ студента]."
    )

# === ОСНОВНА КОМАНДА ФІЛЬМІВ ===
@dp.message(FILMS_COMMAND)
@async_log_function_call
async def films(message: Message) -> None:
    data = get_films()
    markup = films_keyboard_markup(films_list=data)
    await message.answer(
        "Перелік фільмів. Натисніть на назву фільму для отримання деталей.",
        reply_markup=markup,
    )


@dp.callback_query(FilmCallback.filter())
async def callb_film(callback: CallbackQuery, callback_data: FilmCallback) -> None:
    film_id = callback_data.id
    film_data = get_films(film_id=film_id)
    film = Film(**film_data)

    text = f"Фільм: {film.name}\n" \
           f"Опис: {film.description}\n" \
           f"Рейтинг: {film.rating}\n" \
           f"Жанр: {film.genre}\n" \
           f"Актори: {', '.join(film.actors)}\n"

    await callback.message.answer_photo(
        caption=text,
        photo=URLInputFile(
            film.poster,
            filename=f"{film.name}_poster.{film.poster.split('.')[-1]}"
        )
    )


# === РЕКОМЕНДАЦІЇ ===
@dp.message(Command('recommend_movie'))
@async_log_function_call
async def recommend_movie(message: Message) -> None:
    films = get_films()
    rated_films = [film for film in films if film.get('rating') is not None]

    if rated_films:
        recommended = max(rated_films, key=lambda film: film['rating'])
        await message.answer(
            f"Рекомендуємо переглянути:\n"
            f"{recommended['name']} - {recommended['description']} "
            f"(Рейтинг: {recommended['rating']})"
        )
    else:
        await message.answer("Наразі немає фільмів з рейтингом для рекомендацій.")

# === ПОШУК ФІЛЬМУ ===
@dp.message(Command('search_movie'))
@async_log_function_call
async def search_movie(message: Message, state: FSMContext) -> None:
    await message.reply("Введіть назву фільму для пошуку:")
    await state.set_state(MovieStates.search_query)

@dp.message(MovieStates.search_query)
@async_log_function_call
async def get_search_query(message: Message, state: FSMContext) -> None:
    query = message.text.lower()
    films_data = get_films()
    results = [film for film in films_data if query in film['name'].lower()]

    if results:
        for film in results:
            await message.reply(f"Знайдено: {film['name']} - {film['description']}")
    else:
        await message.reply("Фільм не знайдено.")

    await state.clear()

# === ФІЛЬТРАЦІЯ ===
@dp.message(Command('filter_movies'))
async def filter_movies(message: Message, state: FSMContext) -> None:
    markup = filter_criteria_markup()
    await message.answer(
        "Оберіть критерій для фільтрації:",
        reply_markup=markup
    )
    await state.set_state(MovieFilterStates.filter_criteria)


@dp.callback_query(F.data.startswith("search_by:"), MovieFilterStates.filter_criteria)
async def process_filter_criteria(callback: CallbackQuery, state: FSMContext):
    criteria = callback.data.split(":")[1]

    await state.update_data(selected_criteria=criteria)
    await state.set_state(MovieFilterStates.filter_value)
    
    await callback.message.answer(
        f"Введіть значення для фільтрації по {criteria}:",
        reply_markup=None
    )
    
    await callback.answer()


@dp.message(MovieFilterStates.filter_value)
async def get_filter_criteria(message: Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    criteria = user_data.get("selected_criteria")
    value = message.text.lower()

    films_data = get_films()
    
    if criteria == "genre":
        filtered = [f for f in films_data if value in f['genre'].lower()]
    elif criteria == "title":
        filtered = [f for f in films_data if value.lower() in f['name'].lower()]
    elif criteria == "actors":
        filtered = [f for f in films_data if any(
            value.lower() in str(actor).lower()
            for actor in f.get('actors', [])
        )]
    else:
        filtered = []

    if filtered:
        for film in filtered:
            response = (f"<b>{film['name']}</b>\n"
                       f"Рік: {film.get('year', 'Невідомо')}\n"
                       f"Рейтинг: {film.get('rating', '?')}/10\n"
                       f"Жанр: {film.get('genre', 'Невідомо')}\n"
                       f"{film.get('description', 'Опис відсутній')}")
            
            await message.answer(response)
    else:
        await message.answer("Нічого не знайдено за вашим запитом")

    await state.clear()

# === ВИДАЛЕННЯ ФІЛЬМУ ===
@dp.message(Command('delete_movie'))
@async_log_function_call
async def delete_movie(message: Message, state: FSMContext) -> None:
    await message.reply("Введіть назву фільму, який бажаєте видалити:")
    await state.set_state(MovieStates.delete_query)

@dp.message(MovieStates.delete_query)
@async_log_function_call
async def get_delete_query(message: Message, state: FSMContext) -> None:
    film_to_delete = message.text
    if delete_film_by_name(film_to_delete):
        await message.reply(f"Фільм '{film_to_delete}' видалено.")
    else:
        await message.reply("Фільм не знайдено.")
    await state.clear()

# === РЕДАГУВАННЯ ОПИСУ ===
@dp.message(Command('edit_movie'))
@async_log_function_call
async def edit_movie(message: Message, state: FSMContext) -> None:
    await message.reply("Введіть назву фільму, який бажаєте редагувати:")
    await state.set_state(MovieStates.edit_query)


@dp.message(MovieStates.edit_query)
@async_log_function_call
async def get_edit_query(message: Message, state: FSMContext) -> None:
    film_to_edit = message.text.lower()
    films = get_films()
    for film in films:
        if film_to_edit == film['name'].lower():
            await state.update_data(film_name=film['name'])
            await message.reply("Введіть новий опис фільму:")
            await state.set_state(MovieStates.edit_description)
            return
    await message.reply("Фільм не знайдено.")
    await state.clear()


@dp.message(MovieStates.edit_description)
@async_log_function_call
async def update_description(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    film = data['film_name']
    if update_film_description(film, message.text):
        await message.reply(f"Фільм '{film}' оновлено.")
    else:
        await message.reply("Виникла помилка...")
    await state.clear()

# === ОЦІНКА ФІЛЬМУ ===
@dp.message(Command('rate_movie'))
@async_log_function_call
async def rate_movie(message: Message, state: FSMContext) -> None:
    await message.reply("Введіть назву фільму, щоб оцінити:")
    await state.set_state(MovieRatingStates.rate_query)

@dp.message(MovieRatingStates.rate_query)
@async_log_function_call
async def get_rate_query(message: Message, state: FSMContext) -> None:
    film_to_rate = message.text.lower()
    films_data = get_films()
    for film in films_data:
        if film_to_rate == film['name'].lower():
            await state.update_data(film_name=film['name'])
            await message.reply("Введіть рейтинг від 1 до 10:")
            await state.set_state(MovieRatingStates.set_rating)
            return
    await message.reply("Фільм не знайдено.")
    await state.clear()


@dp.message(MovieRatingStates.set_rating)
@async_log_function_call
async def set_rating(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    film = data['film_name']
    try:
        rating = int(message.text)
        if 1 <= rating <= 10:
            update_film_rating(film, rating)
            await message.reply(f"Рейтинг для '{film}' оновлено на {rating}.")
            await state.clear()
        else:
            await message.reply("Введіть рейтинг від 1 до 10.")
    except ValueError:
        await message.reply("Введіть число.")

# === СТВОРЕННЯ ФІЛЬМУ ===
@dp.message(FILM_CREATE_COMMAND)
async def film_create(message: Message, state: FSMContext) -> None:
   await state.set_state(FilmForm.name)
   await message.answer(
       f"Введіть назву фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.name)
async def film_name(message: Message, state: FSMContext) -> None:
   await state.update_data(name=message.text)
   await state.set_state(FilmForm.description)
   await message.answer(
       f"Введіть опис фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.description)
async def film_description(message: Message, state: FSMContext) -> None:
   await state.update_data(description=message.text)
   await state.set_state(FilmForm.rating)
   await message.answer(
       f"Вкажіть рейтинг фільму від 0 до 10.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.rating)
async def film_rating(message: Message, state: FSMContext) -> None:
   await state.update_data(rating=float(message.text))
   await state.set_state(FilmForm.genre)
   await message.answer(
       f"Введіть жанр фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.genre)
async def film_genre(message: Message, state: FSMContext) -> None:
   await state.update_data(genre=message.text)
   await state.set_state(FilmForm.actors)
   await message.answer(
       text=f"Введіть акторів фільму через роздільник ', '\nОбов'язкова кома та відступ після неї.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.actors)
async def film_actors(message: Message, state: FSMContext) -> None:
   await state.update_data(actors=[x for x in message.text.split(", ")])
   await state.set_state(FilmForm.poster)
   await message.answer(
       f"Введіть посилання на постер фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.poster)
async def film_poster(message: Message, state: FSMContext) -> None:
   data = await state.update_data(poster=message.text)
   film = Film(**data)
   add_film(film.model_dump())
   await state.clear()
   await message.answer(
       f"Фільм {film.name} успішно додано!",
       reply_markup=ReplyKeyboardRemove(),
   )
