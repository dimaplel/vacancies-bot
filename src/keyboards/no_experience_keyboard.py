from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def no_experience_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder().add(InlineKeyboardButton(text="I have no experience ❌", callback_data='no-exp'))
    return builder.as_markup()