from aiogram.filters.state import State, StatesGroup


class MenuStates(StatesGroup):
    profile_home = State()
    seeker_home = State()
    seeker_profile_editing = State()
    recruiter_home = State()
    user_profile_editing = State()


class RecruiterMenuStates(StatesGroup):
    vacancy_position = State()
    vacancy_description = State()
    confirm_or_retry_description = State()
    vacancy_salary = State()