from dataclasses import dataclass


@dataclass
class RecruiterProfile:
    _user_id: int
    _company_id: int # Can be used to retrieve company object from companies table in sql connection
    _recruiter_node_ref: str


    def get_id(self) -> int:
        return self._user_id