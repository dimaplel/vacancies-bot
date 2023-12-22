from src.keyboards.inline_keyboard_markup import SweetInlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class NoExperienceInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "no_experience_button": InlineKeyboardButton(text="I have no experience ❌", callback_data='no-exp')
        }
        self.update_keyboard()


class PortfolioAdditionInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "add_experience_button": InlineKeyboardButton(text="Add another experience 📌", callback_data="add-exp"),
            "confirm_experience_button": InlineKeyboardButton(text="Confirm added experiences ✅", callback_data="conf-exp")
        }
        self.update_keyboard(1, 1)


class SeekerPortfolioEditingInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "update_portfolio_button": InlineKeyboardButton(text="Update Portfolio ✅", callback_data="portfolio"),
            "back_button": InlineKeyboardButton(text="Back to Seeker menu ⬅️", callback_data="back")
        }
        self.update_keyboard()


class SeekerVacancySearchingInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "prev_vacancy_button": InlineKeyboardButton(text="Prev ⬅️", callback_data="prev"),
            "next_vacancy_button": InlineKeyboardButton(text="Next ➡️", callback_data="next"),
            "back_button": InlineKeyboardButton(text="Back to Seeker menu ❌", callback_data="back")
        }
        self.update_keyboard()