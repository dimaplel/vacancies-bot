from aiogram.filters.state import State, StatesGroup


class EntryRegistrationStates(StatesGroup):
    first_name = State()
    last_name = State()
    options_handle = State()


class SeekerRegistrationStates(StatesGroup):
    position = State()
    experience_title = State()
    experience_desc = State()
    experience_timeline = State()
    confirm_or_add_portfolio = State()


class RecruiterRegistrationStates(StatesGroup):
    enter_company = State()
    register_or_retry = State()
    choose_company = State()