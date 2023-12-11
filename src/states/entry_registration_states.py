from aiogram.filters.state import State, StatesGroup


class EntryRegistrationStates(StatesGroup):
    first_name = State()
    last_name = State()
    options_handle = State()
