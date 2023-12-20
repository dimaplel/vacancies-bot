import logging
from dataclasses import dataclass

from src.company_registry import CompanyRegistry
from src.connections import PsqlConnection, Neo4jConnection, MongoDBConnection, RedisConnection
from src.users.company import Company
from src.keyboards.profile_keyboards import RecruiterProfileKeyboardMarkup
from src.users.vacancy import Vacancy

@dataclass
class RecruiterProfile:
    _user_id: int
    _company_id: int # Can be used to retrieve company object from companies table in sql connection
    _recruiter_node_ref: str
    _cached_vacancies: (dict[int, Vacancy] | None) = None
    recruiter_markup = RecruiterProfileKeyboardMarkup()


    def get_id(self) -> int:
        return self._user_id


    def get_vacancies(self) -> list[Vacancy]:
        if self._cached_vacancies is None:
            return []
        return list(self._cached_vacancies.values())


    def get_company(self, company_registry: CompanyRegistry) -> Company:
        return company_registry.get_company(self._company_id)


    def add_vacancy(self, psql_connection: PsqlConnection, mongodb_connection: MongoDBConnection,
                    neo4j_connection: Neo4jConnection, redis_connection: RedisConnection,
                    company_registry: CompanyRegistry, vacancy_data: dict) -> None:
        logging.info(f"Adding vacancy with data {vacancy_data}")
        document_ref = mongodb_connection.insert_document("vacancies", vacancy_data)
        vacancy_id = psql_connection.execute_query_fetchone("INSERT INTO vacancies (recruiter_id, vacancy_doc_ref) "
                                                            "VALUES (%s, %s) RETURNING vacancy_id;",
                                                            self._user_id, document_ref)["vacancy_id"]
        neo4j_connection.run_query("MATCH (r:Recruiter) WHERE id(r) = $recruiter_id "
                                   "CREATE (v: Vacancy {vacancy_id: $vacancy_id})-[:published_by]->(r) "
                                   "RETURN id(v) AS vacancyId",
                                   {"recruiter_id": self._recruiter_node_ref, "vacancy_id": vacancy_id})
        self.get_company(company_registry).metrics.increment_num_vacancies(redis_connection)

        vacancy = Vacancy(self._user_id, vacancy_id)
        self._add_vacancy_to_cache(vacancy)


    def _add_vacancy_to_cache(self, vacancy: Vacancy) -> None:
        if self._cached_vacancies is None:
            self._cached_vacancies = {}

        self._cached_vacancies[vacancy.get_id()] = vacancy