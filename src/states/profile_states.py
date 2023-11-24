from aiogram.filters.state import State, StatesGroup

class ProfileStates(StatesGroup):
    name = State()
    load_cv = State()