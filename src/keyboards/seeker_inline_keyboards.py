from src.keyboards.inline_keyboard_markup import SweetInlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class SeekerPortfolioEditingInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "update_portfolio_button": InlineKeyboardButton(text="Update Portfolio ✅", callback_data="portfolio"),
            "update_position_button": InlineKeyboardButton(text="Update Position", callback_data="position"),
            "back_button": InlineKeyboardButton(text="Back ❌", callback_data="back")
        }
        self.update_keyboard()
