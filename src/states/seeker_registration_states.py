from aiogram.filters.state import State, StatesGroup


class SeekerRegistrationStates(StatesGroup):
    position = State()
    experience_title = State()
    experience_desc = State()
    experience_timeline = State()
    confirm_or_add_portfolio = State()