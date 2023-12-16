from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class SweetInlineKeyboardMarkup:
    def __init__(self):
        self._keyboard_buttons = None
        self._keyboard_markup = None

    def update_keyboard(self, *sizes) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder().add(
            *[button for _, button in self._keyboard_buttons.items()]
        ).adjust(*sizes)

        self._keyboard_markup = builder.as_markup()
        return self.get_current_markup()


    def get_current_markup(self) -> InlineKeyboardMarkup:
        assert self._keyboard_markup is not None
        return self._keyboard_markup


    def get_button_data(self, key: str):
        return self._keyboard_buttons.get(key).callback_data