from typing import Dict, Any
from src.connections import MongoDBConnection


class Vacancy:
    def __init__(self, recruiter_id: int, vacancy_id: int):
        self._recruiter_id = recruiter_id
        self._vacancy_id = vacancy_id


    def get_id(self) -> int:
        return self._vacancy_id

    def get_recruiter_id(self) -> int:
        return self._recruiter_id


    def get_vacancy_data(self, mongodb_connection: MongoDBConnection) -> (Dict[str, Any] | None):
        return mongodb_connection.get_document("vacancies", str(self._vacancy_id))
    