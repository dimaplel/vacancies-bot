from aiogram.filters.state import State, StatesGroup


class RecruiterRegistrationStates(StatesGroup):
    enter_company = State()