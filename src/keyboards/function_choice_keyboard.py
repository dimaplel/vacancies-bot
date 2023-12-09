from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def function_choice_keyboard() -> ReplyKeyboardMarkup:
    builder =  ReplyKeyboardBuilder().add(KeyboardButton(text="Seeker Menu 🔍"),
                                      KeyboardButton(text="Recruiter Menu 📝"),
                                      KeyboardButton(text="Edit profile 👤")).adjust(2, 1)
    kb = builder.as_markup()
    kb.resize_keyboard = True
    kb.one_time_keyboard = True
    return kb