from aiogram.filters.state import State, StatesGroup


class MenuStates(StatesGroup):
    options_handle = State()