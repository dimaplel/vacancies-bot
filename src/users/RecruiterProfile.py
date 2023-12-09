class RecruiterProfile:
    _recruiter_node_ref: str
    _company_sql_ref: str

    def __init__(self, recruiter_node_ref: str, company_ref: str):
        self._recruiter_node_ref = recruiter_node_ref
        self._company_sql_ref = company_ref


    def set_recruiter_node_ref(self, recruiter_node_ref: str):
        self._recruiter_node_ref = recruiter_node_ref


    def set_company_sql_ref(self, company_sql_ref: str):
        self._company_sql_ref = company_sql_ref


    def get_recruiter_node_ref(self) -> str:
        return self._recruiter_node_ref


    def get_company_sql_ref(self) -> str:
        return self._company_sql_ref


