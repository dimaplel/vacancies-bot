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