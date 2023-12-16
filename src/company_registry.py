from typing import Dict

from connections import PsqlConnection
from users.company import Company


class CompanyRegistry:
    def __init__(self, psql_connection: PsqlConnection):
        self._sql_connection = psql_connection
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
        self._add_company_to_cache(company)
        return company


    def search_by_name(self, name: str) -> (list[Company] | None):
        rows = self._sql_connection.execute_query(f"SELECT * FROM companies WHERE name ILIKE %s",
                                                 name + '%',)
        if rows is None:
            return None

        companies = [Company(row["company_id"], row["name"]) for row in rows]
        return companies


    def _get_company_from_cache(self, company_id: int) -> (Company | None):
        return self._companies.get(company_id)


    def _add_company_to_cache(self, company: Company):
        self._companies[company.get_id()] = company