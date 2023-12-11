from typing import Dict

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class SweetKeyboardMarkup:
    def set_buttons_value(self, data: Dict[str, KeyboardButton]) -> bool:
        if len(set(data.keys()).intersection(set(self._keyboard_buttons.keys()))) != len(data):
            return False

        self._keyboard_buttons.update(data)
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