class RecruiterProfile:
    _user_id: int
    _recruiter_node_ref: str
    _company_id: int # Can be used to retrieve company object from companies table in sql connection

    def __init__(self, user_id: int, recruiter_node_ref: str, company_ref: str):
        self._user_id = user_id
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


