from aiogram import Dispatcher, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import URLInputFile

from MainFiles.states import FilmForm, MovieStates, MovieRatingStates
from utils.data import get_films, add_film, delete_film_by_name, update_film_description, update_film_rating
from keyboards import films_keyboard_markup, FilmCallback
from models import Film
from external import async_log_function_call
from helpers.commands import (
   FILMS_COMMAND,
   START_COMMAND,
   FILM_CREATE_COMMAND,
)

dp = Dispatcher()
router = Router()


@dp.message(START_COMMAND)
@async_log_function_call
async def start(message: Message) -> None:
    await message.answer(
        f"Вітаю, {message.from_user.full_name}!\n"\
        "Я перший бот Python розробника [ПІБ студента]."
    )

#===MAIN FILMS COMMANDS===
@dp.message(FILMS_COMMAND)
@async_log_function_call
async def films(message: Message) -> None:
    data = get_films()
    markup = films_keyboard_markup(films_list=data)
    await message.answer(
        f"Перелік фільмів. Натисніть на назву фільму для отримання деталей.",
        reply_markup=markup
    )


@router.message(Command('recommend_movie'))
@async_log_function_call
async def recommend_movie(message: Message):
    films = get_films()
    rated_films = [film for film in films if film.get('rating') is not None]
    
    if rated_films:
        recommended = max(rated_films, key=lambda film: film['rating'])
        await message.answer(f"Рекомендуємо переглянути: {recommended['name']} - {recommended['description']} (Рейтинг: {recommended['rating']})")
    else:
        await message.answer("Наразі немає фільмів з рейтингом для рекомендацій.")


@dp.message(Command('search_movie'))
@async_log_function_call
async def search_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму для пошуку:")
    await state.set_state(MovieStates.search_query)


@dp.message(MovieStates.search_query)
@async_log_function_call
async def get_search_query(message: Message, state: FSMContext):
    query = message.text.lower()
    films_data = get_films()
    results = [film for film in films_data if query in film['name'].lower()]
    
    if results:
        for film in results:
            await message.reply(f"Знайдено: {film['name']} - {film['description']}")
    else:
        await message.reply("Фільм не знайдено.")
    
    await state.clear()


@dp.message(Command('filter_movies'))
@async_log_function_call
async def filter_movies(message: Message, state: FSMContext):
    await message.reply("Введіть жанр або рік випуску для фільтрації:")
    await state.set_state(MovieStates.filter_criteria)

@dp.message(MovieStates.filter_criteria)
@async_log_function_call
async def get_filter_criteria(message: Message, state: FSMContext):
    criteria = message.text.lower()
    films_data = get_films()
    filtered = list(filter(lambda film: criteria in film['genre'].lower() == criteria, films_data))
    
    if filtered:
        for film in filtered:
            await message.reply(f"Знайдено: {film['name']} - {film['description']}")
    else:
        await message.reply("Фільм не знайдено за цими критеріями.")
    
    await state.clear()


@dp.message(Command('delete_movie'))
@async_log_function_call
async def delete_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму, який бажаєте видалити:")
    await state.set_state(MovieStates.delete_query)


@dp.message(MovieStates.delete_query)
@async_log_function_call
async def get_delete_query(message: Message, state: FSMContext):
    film_to_delete = message.text
    if delete_film_by_name(film_to_delete):
        await message.reply(f"Фільм '{film_to_delete}' видалено.")
        await state.clear()
        return
    await message.reply("Фільм не знайдено.")
    await state.clear()


@dp.message(Command('edit_movie'))
@async_log_function_call
async def edit_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму, який бажаєте редагувати:")
    await state.set_state(MovieStates.edit_query)


@dp.message(MovieStates.edit_query)
@async_log_function_call
async def get_edit_query(message: Message, state: FSMContext):
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
async def update_description(message: Message, state: FSMContext):
    data = await state.get_data()
    film = data['film_name']
    if update_film_description(film, message.text):
        await message.reply(f"Фільм '{film}' оновлено.")
        await state.clear()
        return
    await message.reply("Виникла помилка...")
    await state.clear()


@dp.message(Command('rate_movie'))
@async_log_function_call
async def rate_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму, щоб оцінити:")
    await state.set_state(MovieRatingStates.rate_query)


@dp.message(MovieRatingStates.rate_query)
@async_log_function_call
async def get_rate_query(message: Message, state: FSMContext):
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
async def set_rating(message: Message, state: FSMContext):
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


@dp.message(FILM_CREATE_COMMAND)
@async_log_function_call
async def film_create(message: Message, state: FSMContext) -> None:
   await state.set_state(FilmForm.name)
   await message.answer(
       f"Введіть назву фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )

# ===FILM FORMS===
@dp.message(FilmForm.name)
@async_log_function_call
async def film_name(message: Message, state: FSMContext) -> None:
   await state.update_data(name=message.text)
   await state.set_state(FilmForm.description)
   await message.answer(
       f"Введіть опис фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.description)
@async_log_function_call
async def film_description(message: Message, state: FSMContext) -> None:
   await state.update_data(description=message.text)
   await state.set_state(FilmForm.rating)
   await message.answer(
       f"Вкажіть рейтинг фільму від 0 до 10.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.rating)
@async_log_function_call
async def film_rating(message: Message, state: FSMContext) -> None:
   await state.update_data(rating=float(message.text))
   await state.set_state(FilmForm.genre)
   await message.answer(
       f"Введіть жанр фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.genre)
@async_log_function_call
async def film_genre(message: Message, state: FSMContext) -> None:
   await state.update_data(genre=message.text)
   await state.set_state(FilmForm.actors)
   await message.answer(
       text=f"Введіть акторів фільму через роздільник ', '\n" "Обов'язкова кома та відступ після неї.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.actors)
@async_log_function_call
async def film_actors(message: Message, state: FSMContext) -> None:
   await state.update_data(actors=[x for x in message.text.split(", ")])
   await state.set_state(FilmForm.poster)
   await message.answer(
       f"Введіть посилання на постер фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )


@dp.message(FilmForm.poster)
@async_log_function_call
async def film_poster(message: Message, state: FSMContext) -> None:
   data = await state.update_data(poster=message.text)
   film = Film(**data)
   add_film(film.model_dump())
   await state.clear()
   await message.answer(
       f"Фільм {film.name} успішно додано!",
       reply_markup=ReplyKeyboardRemove(),
   )

#===FILM CALLBACK===
@dp.callback_query(FilmCallback.filter())
@async_log_function_call
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