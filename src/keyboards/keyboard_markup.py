from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class SweetKeyboardMarkup:
    def set_button_value(self, button: str, value: str) -> bool:
        if not button in self._keyboard_buttons:
            return False

        self._keyboard_buttons[button] = value
        return True


    def update_markup(self, *sizes) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder().add(
            [KeyboardButton(text=value) for _, value in self._keyboard_buttons.items()]
        ).adjust(sizes=sizes)

        self._keyboard_markup = builder.as_markup()
        self._keyboard_markup.resize_keyboard = True
        self._keyboard_markup.one_time_keyboard = True
        return self.get_current_markup()


    def get_current_markup(self) -> ReplyKeyboardMarkup:
        assert self._keyboard_markup is not None
        return self._keyboard_markup