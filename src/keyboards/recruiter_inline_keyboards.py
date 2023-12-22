from src.keyboards.inline_keyboard_markup import SweetInlineKeyboardMarkup, InlineKeyboardBuilder
from src.users.company import Company
from src.users.seeker_profile import SeekerProfile
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class SearchOrRegisterInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "register_button": InlineKeyboardButton(text="Register new company 🏢", callback_data="company-reg"),
            "retry_button": InlineKeyboardButton(text="Try again 🔁", callback_data="search-again")
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
        companies_buttons = [button for button in
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


    def get_companies(self):
        return self._companies

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
            

class ConfirmOrChangeDescriptionInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "confirm_button": InlineKeyboardButton(text="Confirm description ✅", callback_data="confirm"),
            "retry_button": InlineKeyboardButton(text="Enter again 🔁", callback_data="retry")
        }
        self.update_keyboard(2)


class KeepThePreviousDescriptionInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "back_button": InlineKeyboardButton(text="I changed my mind, keep the previous one 🔁",
                                                callback_data="back")
        }
        self.update_keyboard()


class GoBackInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "back_button": InlineKeyboardButton(text="Go back ⬅️", callback_data="back")
        }
        self.update_keyboard()


class VacancyDisplayInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "back_button": InlineKeyboardButton(text="Go back ⬅️", callback_data="back"),
            "delete_button": InlineKeyboardButton(text="Delete vacancy ♻️", callback_data="delete"),
            "applicants_button": InlineKeyboardButton(text="See applicants 👥", callback_data="applicants")
        }
        self.update_keyboard()


class DeleteVacancyOrGoBackInlineKeyboardMarkup(SweetInlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "delete_button": InlineKeyboardButton(text="I'm sure, delete it ♻️", callback_data="confirm"),
            "back_button": InlineKeyboardButton(text="Go back ⬅️", callback_data="back"),
        }
        self.update_keyboard(2)


class ApplicantsListDisplayInlineKeyboard(SweetInlineKeyboardMarkup):
    def __init__(self, applicants_length: int):
        super().__init__()
        self._cur_applicant: int = 0
        self._applicants_length: int = applicants_length
        self._keyboard_buttons: dict[str, InlineKeyboardButton] = {
            "previous_button": InlineKeyboardButton(text="Previous ⬅️", callback_data="back"),
            "close_display": InlineKeyboardButton(text="Stop displaying ❌", callback_data="exit"),
            "next_button": InlineKeyboardButton(text="Next ➡️", callback_data="next"),
        }
        self.update_keyboard()


    def update_keyboard(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        if self._cur_applicant != 0:
            builder.add(self._keyboard_buttons.get("previous_button"))

        builder.add(self._keyboard_buttons.get("close_display"))

        if self._cur_applicant != self._applicants_length - 1:
            builder.add(self._keyboard_buttons.get("next_button"))

        self._keyboard_markup = builder.adjust(3).as_markup()
        return self.get_current_markup()


    def flip_page(self, is_next: bool):
        self._cur_applicant += 1 if is_next else -1
        self.update_keyboard()


    def get_current_applicant(self):
        return self._cur_applicant
