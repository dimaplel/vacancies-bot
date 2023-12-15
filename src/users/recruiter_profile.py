from dataclasses import dataclass
from src.keyboards.profile_keyboards import RecruiterProfileKeyboardMarkup
from src.users.vacancy import Vacancy

@dataclass
class RecruiterProfile:
    _user_id: int
    _company_id: int # Can be used to retrieve company object from companies table in sql connection
    _recruiter_node_ref: str
    _cached_vacancies: (dict[str, Vacancy] | None) = None
    recruiter_markup = RecruiterProfileKeyboardMarkup()


    def get_id(self) -> int:
        return self._user_id