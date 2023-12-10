from aiogram.types import KeyboardButton
from keyboard_markup import SweetKeyboardMarkup


class UserProfileKeyboardMarkup(SweetKeyboardMarkup):
    def __init__(self):
        self._keyboard_buttons: dict[KeyboardButton] = {
            "seeker_button" : KeyboardButton(text="Create Seeker Profile"),
            "recruiter_button" : KeyboardButton(text="Create Recruiter Profile"),
            "edit_profile_button" : KeyboardButton(text="Edit Profile 👤")
        }
        self.update_markup()


class SeekerProfileKeyboardMarkup(SweetKeyboardMarkup):
    def __init__(self):
        self._keyboard_buttons: dict[KeyboardButton] = {
            "edit_portfolio_button" : KeyboardButton(text="Edit Portfolio"),
            "search_vacancies_button" : KeyboardButton(text="Search Vacancies")
        }
        self.update_markup()