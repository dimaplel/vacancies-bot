from aiogram.filters.state import State, StatesGroup


class ProfileStates(StatesGroup):
    first_name = State()
    last_name = State()