from typing import Dict

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class SweetKeyboardMarkup:
    def __init__(self):
        self._keyboard_buttons = None
        self._keyboard_markup = None


    def set_button_value(self, button: str, value: str) -> bool:
        if not button in self._keyboard_buttons:
            return False

        self._keyboard_buttons[button] = KeyboardButton(text=value)
        return True


    def update_markup(self, *sizes) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder().add(
            *[button for _, button in self._keyboard_buttons.items()]
        ).adjust(*sizes)

        self._keyboard_markup = builder.as_markup()
        self._keyboard_markup.resize_keyboard = True
        self._keyboard_markup.one_time_keyboard = True
        return self.get_current_markup()


    def get_current_markup(self) -> ReplyKeyboardMarkup:
        assert self._keyboard_markup is not None
        return self._keyboard_markup


    def get_button_text(self, key: str):
        return self._keyboard_buttons.get(key).text