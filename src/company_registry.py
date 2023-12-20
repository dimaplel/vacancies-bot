import logging
from typing import Dict

from connections import PsqlConnection, RedisConnection
from users.company import Company


class CompanyRegistry:
    def __init__(self, psql_connection: PsqlConnection, redis_connection: RedisConnection):
        self._sql_connection = psql_connection
        self._redis_connection = redis_connection
        self._companies: Dict[int, Company] = {}


    def get_company(self, company_id: int) -> (Company | None):
        # try to query a company from cache
        company = self._get_company_from_cache(company_id)
        if company is not None:
            return company

        # if there is no company in cache - query psql connection
        row = self._sql_connection.execute_query_fetchone(f"SELECT * FROM companies WHERE company_id = {company_id}")
        if row is None:
            return None

        company_name = row['name']
        company = Company(company_id, company_name)
        company.update_metrics(self._redis_connection)
        self._add_company_to_cache(company)
        return company


    def search_by_name(self, name: str) -> (list[Company] | None):
        rows = self._sql_connection.execute_query(f"SELECT * FROM companies WHERE name ILIKE %s",
                                                 name + '%',)
        if rows is None:
            return None

        companies = [Company(row["company_id"], row["name"]) for row in rows]
        return companies


    def add_company(self, company_name: str, company_employees: int, company_vacancies: int = 0):
        company_id_row = self._sql_connection.execute_query_fetchone(
            f"INSERT INTO companies (name) VALUES (%s) RETURNING company_id;",
            company_name)
        if company_id_row is None:
            logging.error(f"An error occured while adding company {company_name}, as company_id was not retrieved.")
            return

        company_id = company_id_row["company_id"]

        company = Company(company_id, company_name)
        company.metrics.create_metrics(self._redis_connection, company_employees, company_vacancies)
        self._add_company_to_cache(company)

        return company


    def get_metrics(self, company_id: int) -> dict[str, int]:
        company = self._get_company_from_cache(company_id)
        if company is not None:
            employees = company.metrics.num_employees
            vacancies = company.metrics.num_vacancies
        else:
            employees = int(self._redis_connection.get(f"company:{company_id}:employees"))
            vacancies = int(self._redis_connection.get(f"company:{company_id}:vacancies"))
        return {"employees": employees, "open_vacancies": vacancies}


    def _get_company_from_cache(self, company_id: int) -> (Company | None):
        return self._companies.get(company_id)


    def _add_company_to_cache(self, company: Company):
        self._companies[company.get_id()] = company