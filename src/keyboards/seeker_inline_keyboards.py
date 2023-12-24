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
        self._toggleable_keyboard_buttons: dict[str, (bool, InlineKeyboardButton)] = {
            "prev_vacancy_button":  (True, InlineKeyboardButton(text="Prev ⬅️", callback_data="prev")),
            "back_button":          (True, InlineKeyboardButton(text="Back ❌", callback_data="back")),
            "apply_button":         (True, InlineKeyboardButton(text="Apply ✅", callback_data="apply")),
            "next_vacancy_button":  (True, InlineKeyboardButton(text="Next ➡️", callback_data="next")),
        }
        self.update_keyboard()

    
    def update_keyboard(self, *sizes) -> InlineKeyboardMarkup:
        self._keyboard_buttons = {}
        for key, (toggled, button) in self._toggleable_keyboard_buttons.items():
            if toggled:
                self._keyboard_buttons[key] = button

        return super().update_keyboard(*sizes)

    
    def toggle_button(self, button: str, val: bool):
        tup = self._toggleable_keyboard_buttons[button]
        self._toggleable_keyboard_buttons[button] = (val, tup[1])


class SeekerVacacnyFiltersInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "filter_salary":    InlineKeyboardButton(text="Enter salary", callback_data="filter_salary"),
            "filter_position":  InlineKeyboardButton(text="Enter position", callback_data="filter_position"),
            "done_button":      InlineKeyboardButton(text="Done", callback_data="done"),
        }
        self.update_keyboard()