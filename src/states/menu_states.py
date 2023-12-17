from aiogram.filters.state import State, StatesGroup


class MenuStates(StatesGroup):
    profile_home = State()
    seeker_home = State()
    recruiter_home = State()
    seeker_profile_editing = State()