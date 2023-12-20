from typing import Dict, Any
from src.connections import PsqlConnection, MongoDBConnection


class Vacancy:
    def __init__(self, vacancy_id: int, recruiter_id: int, vacancy_doc_ref: str):
        self._vacancy_id = vacancy_id
        self._recruiter_id = recruiter_id
        self._vacancy_doc_ref = vacancy_doc_ref


    def get_id(self) -> int:
        return self._vacancy_id


    def get_recruiter_id(self) -> int:
        return self._recruiter_id


    def get_vacancy_data(self, mongodb_connection: MongoDBConnection) -> (Dict[str, Any] | None):
        return mongodb_connection.get_document("vacancies", self._vacancy_doc_ref)
    

class VacanciesChunk:
    """
    Represents a "search" chunk of vacancies. Basically stores an array of vacancies
    Object will query vacancies by the provided offset and limit
    """
    def __init__(self, limit: int, chunk_offset: int):
        self._limit = limit
        self._chunk_offset = chunk_offset
        self._vacancies = []

    
    def query_chunk(self, psql_connection: PsqlConnection) -> list[Vacancy]:
        row_offset = self._chunk_offset * self._limit
        rows = psql_connection.execute_query(f"SELECT * FROM vacancies LIMIT {self._limit} OFFSET {row_offset}")

        vacancies = []
        if rows is None:
            return vacancies

        for row in rows:
            vacancy = Vacancy(
                vacancy_id=row['vacancy_id'], 
                recruiter_id=row['recruiter_id'], 
                vacancy_doc_ref=row['vacancy_doc_ref']
            )
            vacancies.append(vacancy)
        
        self._vacancies = vacancies
        return vacancies


    def get_current_chunk(self) -> list[Vacancy]:
        return self._vacancies