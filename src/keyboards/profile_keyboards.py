from aiogram.types import KeyboardButton

from src.keyboards.keyboard_markup import SweetKeyboardMarkup


class UserProfileKeyboardMarkup(SweetKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, KeyboardButton] = {
            "seeker_button" : KeyboardButton(text="Create Seeker Profile"),
            "recruiter_button" : KeyboardButton(text="Create Recruiter Profile"),
            "edit_profile_button" : KeyboardButton(text="Edit Profile 👤")
        }

        self.update_markup(2, 1)



class SeekerProfileKeyboardMarkup(SweetKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, KeyboardButton] = {
            "edit_portfolio_button" : KeyboardButton(text="Edit Portfolio"),
            "search_vacancies_button" : KeyboardButton(text="Search Vacancies"),
            "back_button": KeyboardButton(text="Back ⬅️")
        }
        self.update_markup()
        

class RecruiterProfileKeyboardMarkup(SweetKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self._keyboard_buttons: dict[str, KeyboardButton] = {
            "add_vacancy_button" : KeyboardButton(text="Add Vacancy"),
            "your_vacancies_button" : KeyboardButton(text="Your Vacancies"),
            "back_button": KeyboardButton(text="Back ⬅")
        }
        self.update_markup()