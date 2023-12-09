from dataclasses import dataclass
from src.users.seeker_profile import SeekerProfile
from src.users.recruiter_profile import RecruiterProfile
from src.databases.psql_connection import PsqlConnection

@dataclass
class UserProfile:
    user_id: int
    first_name: str
    last_name: str
    seeker_ref: SeekerProfile = None
    recruiter_ref: RecruiterProfile = None


    def __init__(self, user_id: int, first_name: str, last_name: str, seeker_ref: SeekerProfile = None, recruiter_ref: RecruiterProfile = None):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.seeker_ref = seeker_ref
        self.recruiter_ref = recruiter_ref


    def update(self, sql_connection: PsqlConnection):
        sql_connection.execute_query(f"""
            UPDATE user_profiles 
            SET first_name = \"{self.first_name}\", last_name = \"{self.last_name}\" 
            WHERE user_id = {self.user_id}""")



