from aiogram.filters.state import State, StatesGroup


class RecruiterRegistrationStates(StatesGroup):
    enter_company = State()
    register_or_retry = State()
    choose_company = State()