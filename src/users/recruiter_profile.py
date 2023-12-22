import logging
from dataclasses import dataclass

from src.users.company_registry import CompanyRegistry
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


    def update_vacancies(self, psql_connection: PsqlConnection, neo4j_connection: Neo4jConnection) -> None:
        vacancies_id_list = neo4j_connection.run_query("MATCH (v:Vacancy)-[:published_by]->(r:Recruiter "
                                                       "{user_id: $user_id})"
                                                        "RETURN DISTINCT v.vacancy_id AS vacancy_id",
                                                       {"user_id": self._user_id})
        vacancies_id_tuple = tuple([vid["vacancy_id"] for vid in vacancies_id_list])

        vacancies_rows = psql_connection.execute_query("SELECT * FROM vacancies "
                                                       "WHERE vacancy_id IN %s", vacancies_id_tuple)

        if len(vacancies_rows) == 0:
            logging.info(f"No vacancies were found for seeker profile {self._user_id}")
            return

        self._cached_vacancies: dict[int, Vacancy] = {}
        for vacancy in vacancies_rows:
            self._cached_vacancies[vacancy["vacancy_id"]] = Vacancy(vacancy["vacancy_id"],
                                                                    self._user_id,
                                                                    vacancy["vacancy_doc_ref"])

        logging.info(f"Updated vacancies cache: {self._cached_vacancies}")

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

        vacancy = Vacancy(vacancy_id, self._user_id, document_ref)
        self._add_vacancy_to_cache(vacancy)


    def get_vacancies_data(self, psql_connection:PsqlConnection, mongodb_connection: MongoDBConnection):
        vacancies_rows = psql_connection.execute_query("SELECT vacancy_doc_ref, vacancy_id FROM vacancies "
                                                          "WHERE recruiter_id = %s",self._user_id)
        if len(vacancies_rows) == 0:
            return None

        vacancies_doc_refs = [row["vacancy_doc_ref"] for row in vacancies_rows if row["vacancy_doc_ref"] is not None]
        vacancies_ids = [row["vacancy_id"] for row in vacancies_rows]
        vacancies_data = mongodb_connection.find("vacancies", vacancies_doc_refs)
        return list(zip(vacancies_ids, vacancies_data))


    def delete_vacancy(self, psql_connection: PsqlConnection, mongodb_connection: MongoDBConnection,
                    neo4j_connection: Neo4jConnection, redis_connection: RedisConnection,
                    company_registry: CompanyRegistry, vacancy_data: tuple):
        vacancy_id, vacancy_doc_ref = vacancy_data

        neo4j_connection.run_query("MATCH (vacancy:Vacancy {vacancy_id: $vacancy_id}) "
                                   "OPTIONAL MATCH (vacancy)-[published_by:published_by]->() "
                                   "OPTIONAL MATCH (vacancy)<-[applied_to:applied_to]-() "
                                   "DETACH DELETE vacancy, published_by, applied_to",
                                   {"vacancy_id": vacancy_id})
        psql_connection.execute_query(f"DELETE FROM vacancies WHERE vacancy_id = {vacancy_id}")
        mongodb_connection.delete_document("vacancies", vacancy_doc_ref["_id"])

        self.get_company(company_registry).metrics.decrement_num_vacancies(redis_connection)
        self._cached_vacancies.pop(vacancy_id)


    def get_vacancy_applicants(self, neo4j_connection: Neo4jConnection, vacancy_id: int):
        if self._cached_vacancies is not None:
            return self._cached_vacancies[vacancy_id].get_applicants(neo4j_connection)
        return []


    def _add_vacancy_to_cache(self, vacancy: Vacancy) -> None:
        if self._cached_vacancies is None:
            self._cached_vacancies = {}

        self._cached_vacancies[vacancy.get_id()] = vacancy