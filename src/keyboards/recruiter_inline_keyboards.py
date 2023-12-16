from src.keyboards.inline_keyboard_markup import SweetInlineKeyboardMarkup, InlineKeyboardBuilder
from src.users.company import Company
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


class SearchOrRegisterInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "add_experience_button": InlineKeyboardButton(text="Register new company 🏢", callback_data="company-reg"),
            "confirm_experience_button": InlineKeyboardButton(text="Try again 🔁", callback_data="search-again")
        }
        self.update_keyboard(2)


class CompaniesChoiceInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self, companies: list[Company], limit: int = 5):
        super().__init__()
        self._page_number = 0
        self._companies = companies
        self._companies_len = len(companies)
        self._limit = limit
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "companies": [],
            "previous_button": InlineKeyboardButton(text="Previous ⬅️", callback_data="back"),
            "next_button": InlineKeyboardButton(text="Next ➡️", callback_data="next"),
            "register_button": InlineKeyboardButton(text="Register new company 🏢", callback_data="company-reg"),
        }
        self._fill_companies()
        self.update_keyboard()


    def update_keyboard(self) -> InlineKeyboardMarkup:
        companies_buttons = [button for _, button in
                             self._keyboard_buttons.get("companies")[
                             self._get_lower_limit(): self._get_upper_limit()]
                             ]
        main_builder = InlineKeyboardBuilder().add(*companies_buttons)

        page_flipper_builder = InlineKeyboardBuilder()
        upper_limit = min(self._companies_len, self._get_upper_limit())

        if self._page_number > 0:
            page_flipper_builder.add(self._keyboard_buttons.get("previous_button"))
        if upper_limit < self._companies_len:
            page_flipper_builder.add(self._keyboard_buttons.get("next_button"))
        else:
            page_flipper_builder.add(self._keyboard_buttons.get("register_button"))

        page_flipper_builder.adjust(2)
        main_builder.attach(page_flipper_builder)

        self._keyboard_markup = main_builder.as_markup()
        return self.get_current_markup()


    def flip_page(self, is_next: bool):
        self._page_number += 1 if is_next else -1
        self.update_keyboard()

    def _get_lower_limit(self):
        return self._limit * self._page_number


    def _get_upper_limit(self):
        return self._limit * self._page_number + self._limit


    def _fill_companies(self):
        for i, c in enumerate(
                self._companies[self._get_lower_limit(): self._get_upper_limit()],
        start=self._get_lower_limit()):
            self._keyboard_buttons.get("companies").append(InlineKeyboardButton(text=c.name, callback_data=str(i)))
