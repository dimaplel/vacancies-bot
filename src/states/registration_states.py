from aiogram.filters.state import State, StatesGroup


class EntryRegistrationStates(StatesGroup):
    first_name = State()
    last_name = State()


class UserProfileUpdateStates(StatesGroup):
    first_name = State()
    last_name = State()


class SeekerRegistrationStates(StatesGroup):
    position = State()
    experience_title = State()
    experience_desc = State()
    experience_timeline = State()
    confirm_or_add_portfolio = State()


class SeekerPortfolioUpdateStates(StatesGroup):
    position = State()
    experience_title = State()
    experience_desc = State()
    experience_timeline = State()
    confirm_or_add_portfolio = State()


class RecruiterRegistrationStates(StatesGroup):
    enter_company = State()
    register_or_retry = State()
    choose_company = State()
    register_company = State()