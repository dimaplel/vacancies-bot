from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.keyboards.inline_keyboard_markup import SweetInlineKeyboardMarkup


class UserProfileEditingInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "update_profile_button": InlineKeyboardButton(text="Edit Profile ✅", callback_data="profile"),
            "back_button": InlineKeyboardButton(text="Back ⬅️", callback_data="back")
        }
        self.update_keyboard()