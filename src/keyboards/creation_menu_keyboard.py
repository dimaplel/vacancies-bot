from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

class CreationMenuKeyboard:
    def __get__(self, obg, objtype=None):
        return ReplyKeyboardBuilder().add(KeyboardButton(text="Create seeker profile 🔍"),
                                          KeyboardButton(text="Create recruiter profile 🤓"))