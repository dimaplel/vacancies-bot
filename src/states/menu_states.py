from aiogram.filters.state import State, StatesGroup


class MenuStates(StatesGroup):
    profile_home = State()
    seeker_home = State()
    seeker_profile_editing = State()
    seeker_vacancy_search = State()
    recruiter_home = State()
    user_profile_editing = State()


class RecruiterMenuStates(StatesGroup):
    choose_vacancy = State()
    vacancy_position = State()
    vacancy_description = State()
    confirm_or_retry_description = State()
    vacancy_salary = State()