from aiogram.fsm.state import State, StatesGroup


class FilmForm(StatesGroup):
    name = State()
    description = State()
    rating = State()
    genre = State()
    actors = State()
    poster = State()


class MovieStates(StatesGroup):
    search_query = State()
    filter_criteria = State()
    delete_query = State()
    edit_query = State()
    edit_description = State()


class MovieRatingStates(StatesGroup):
    rate_query = State()
    set_rating = State()


class MovieFilterStates(StatesGroup):
    filter_criteria = State()
    filter_value = State()