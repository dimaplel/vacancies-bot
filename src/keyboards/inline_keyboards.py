from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def no_experience_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder().add(InlineKeyboardButton(text="I have no experience ❌", callback_data='no-exp'))
    return builder.as_markup()


def portfolio_addition_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder().add(
        InlineKeyboardButton(text="Add another experience 📌", callback_data="add-exp"),
        InlineKeyboardButton(text="Confirm added experiences ✅", callback_data="conf-exp")).adjust(1, 1)
    return builder.as_markup()


def search_or_register_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder().add(
        InlineKeyboardButton(text="Register new company 🏢", callback_data="company-reg"),
        InlineKeyboardButton(text="Try again 🔁", callback_data="search-again")).adjust(2)
    return builder.as_markup()

def companies_choice_keyboard(companies: list, page: int, limit=5) -> InlineKeyboardMarkup:
    upper_limit = len(companies) if len(companies) <= page * limit + limit else page * limit + limit
    companies_buttons_builder = InlineKeyboardBuilder().add(
        *[InlineKeyboardButton(text=c.name, callback_data=str(companies.index(c)))
          for c in companies[page*limit:upper_limit]])

    service_buttons_builder = InlineKeyboardBuilder()
    register_button = None
    if page > 0:
        service_buttons_builder.add(InlineKeyboardButton(text="Previous ⬅️", callback_data="back"))
    if len(companies) > upper_limit:
        service_buttons_builder.add(InlineKeyboardButton(text="Next ➡️", callback_data="next"))
    else:
        register_button = InlineKeyboardButton(text="Register new company 🏢", callback_data="company-reg")

    service_buttons_builder.adjust(2)
    companies_buttons_builder.attach(service_buttons_builder)
    if register_button is not None:
        companies_buttons_builder.add(register_button)

    return companies_buttons_builder.as_markup()