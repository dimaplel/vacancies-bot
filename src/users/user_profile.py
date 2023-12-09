from dataclasses import dataclass
from src.users.SeekerProfile import SeekerProfile
from src.users.RecruiterProfile import RecruiterProfile
from src.databases.psql_connection import PsqlConnection

@dataclass
class UserProfile:
    first_name: str
    last_name: str
    seeker_ref: SeekerProfile
    recruiter_ref: RecruiterProfile = None

    def __init__(self, first_name: str, last_name: str, seeker_ref: SeekerProfile = None, recruiter_ref: RecruiterProfile = None):
        self.first_name = first_name
        self.last_name = last_name
        self.seeker_ref = seeker_ref
        self.recruiter_ref = recruiter_ref


    def update_entry(self, user_id: int, sql_connection: PsqlConnection):
        sql_connection.execute_query("UPDATE user_profiles "
                                     "SET first_name = %s, last_name = %s "
                                     "WHERE user_id = %s",
                                     (self.first_name, self.last_name, user_id))



