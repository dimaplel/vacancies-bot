from aiogram.types import KeyboardButton
from enum import StrEnum, auto

from src.keyboards.keyboard_markup import SweetKeyboardMarkup


class UserProfileKeyboardTypes(StrEnum):
    NONE = auto()
    SEEKER = auto()
    RECRUITER = auto()
    FULL = auto()


class UserProfileKeyboardMarkup(SweetKeyboardMarkup):
    def __init__(self):
        self._keyboard_buttons: dict[str, KeyboardButton] = {
            "seeker_button" : KeyboardButton(text="Create Seeker Profile"),
            "recruiter_button" : KeyboardButton(text="Create Recruiter Profile"),
            "edit_profile_button" : KeyboardButton(text="Edit Profile 👤")
        }

        self.update_markup()


    def set_type(self, kb_type):
        if kb_type is UserProfileKeyboardTypes.NONE:
            self.set_buttons_value({
                "seeker_button" : KeyboardButton(text="Create Seeker Profile"),
                "recruiter_button" : KeyboardButton(text="Create Recruiter Profile")
            })
        elif kb_type is UserProfileKeyboardTypes.SEEKER:
            self.set_buttons_value({
                "seeker_button": KeyboardButton(text="Seeker Menu"),
                "recruiter_button": KeyboardButton(text="Create Recruiter Profile")
            })
        elif kb_type is UserProfileKeyboardTypes.RECRUITER:
            self.set_buttons_value({
                "seeker_button" : KeyboardButton(text="Create Seeker Profile"),
                "recruiter_button": KeyboardButton(text="Recruiter Menu")
            })
        else:
            self.set_buttons_value({
                "seeker_button": KeyboardButton(text="Seeker Menu"),
                "recruiter_button": KeyboardButton(text="Recruiter Menu")
            })

        self.update_markup()



class SeekerProfileKeyboardMarkup(SweetKeyboardMarkup):
    def __init__(self):
        self._keyboard_buttons: dict[str, KeyboardButton] = {
            "edit_portfolio_button" : KeyboardButton(text="Edit Portfolio"),
            "search_vacancies_button" : KeyboardButton(text="Search Vacancies")
        }
        self.update_markup()