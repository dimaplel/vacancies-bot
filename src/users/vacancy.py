import logging
from typing import Dict, Any
from src.connections import PsqlConnection, MongoDBConnection, Neo4jConnection


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


    def get_applicants(self, neo4j_connection: Neo4jConnection):
        applicants_id_list = neo4j_connection.run_query("MATCH (s:Seeker)-[:applied_to]->(v:Vacancy {vacancy_id: $vacancy_id})"
                                   " RETURN DISTINCT s.user_id AS user_id_list",
                                   {"vacancy_id": self._vacancy_id})

        if len(applicants_id_list) == 0:
            return applicants_id_list

        return [node["user_id_list"] for node in applicants_id_list]


    def add_applicant(self, seeker_node_ref: str, neo4j_connection: Neo4jConnection) -> bool:
        res = neo4j_connection.run_query(
            """
            MATCH (s:Seeker), (v:Vacancy)
            WHERE ID(s) = $seeker_node_ref AND v.vacancy_id = $vacancy_id
            OPTIONAL MATCH (s)-[r:applied_to]->(v)
            WITH s, v, r
            WHERE r IS NULL
            CREATE (s)-[:applied_to]->(v)
            return s
            """,
            {"vacancy_id": self._vacancy_id, "seeker_node_ref": seeker_node_ref})

        if len(res) == 0:
            return False

        return True


    def filter_suitable(self, salary: tuple[int, int], position_regex, mongodb_connection: MongoDBConnection) -> bool:
        data = self.get_vacancy_data(mongodb_connection)
        # Shouldnt happen
        if data is None:
            logging.error(f"Data is none for vacancy {self.get_id()}")
            return False

        data_salary = data['salary']
        data_position = data['position']

        is_suitable = True
        if salary is not None:
            min_salary, max_salary = salary
            if not (min_salary <= data_salary <= max_salary):
                is_suitable = False

        if position_regex is not None and position_regex.search(data_position) is None:
            is_suitable = False

        return is_suitable

    

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