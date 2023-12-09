from dataclasses import dataclass
from src.users.seeker_profile import SeekerProfile
from src.users.recruiter_profile import RecruiterProfile
from src.databases.psql_connection import PsqlConnection

@dataclass
class UserProfile:
    _user_id: int
    first_name: str
    last_name: str
    seeker_ref: SeekerProfile = None
    recruiter_ref: RecruiterProfile = None


    def update(self, sql_connection: PsqlConnection):
        sql_connection.execute_query(f"""
            UPDATE user_profiles 
            SET first_name = \"{self.first_name}\", last_name = \"{self.last_name}\" 
            WHERE user_id = {self.user_id}""")


    def get_id(self) -> int:
        return self._user_id

     
    # Returns False if the seeker profile was not set for a provided user
    # Calling this method when user's seeker profile was already set results in runtime error
    # A profile won't be set, thus returning False, if:
    #   - there is no seeker profile associated with the provided user_id
    # 
    # Otherwise the method should return True
    def request_seeker_profile(self, psql_connection: PsqlConnection) -> bool:
        assert psql_connection is not None

        user_id = self.get_id()
        queryResult = psql_connection.execute_query(f"SELECT * FROM seeker_profiles WHERE user_id = {user_id}")
        if queryResult is None:
            return False

        assert len(queryResult) == 1
        row = queryResult[0]
        portfolio_ref = row['portfolio_ref']
        seeker_node_ref = row['seeker_node_ref']
        self._set_seeker_profile(SeekerProfile(user_id, portfolio_ref, seeker_node_ref))
        return True


    # Returns False is the recruiter profile was not set for a provided user
    # Calling this method when user's recruiter profile was already set results in runtime error
    # A profile won't be set, thus returning False, if:
    #   - there is no recruiter profile associated with the provided user_id
    # 
    # Otherwise the method should return True
    def request_recruiter_profile(self, psql_connection: PsqlConnection) -> bool:
        assert psql_connection is not None

        user_id = self.get_id()
        queryResult = psql_connection.execute_query(f"SELECT * FROM recruiter_profiles WHERE user_id = {user_id}")
        if queryResult is None:
            return False

        assert len(queryResult) == 1
        row = queryResult[0]
        company_id: int = int(row['company_id'])
        recruiter_node_ref = row['recruiter_node_ref']
        self._set_recruiter_profile(RecruiterProfile(user_id, company_id, recruiter_node_ref))
        return True


    def has_seeker_profile(self) -> bool:
        return self.seeker_ref is not None


    def has_recruiter_profile(self) -> bool:
        return self.recruiter_ref is not None


    def _set_seeker_profile(self, seeker_profile: SeekerProfile):
        # This is unexpected behavior if we try to set a seeker profile while there is already one
        assert not self.has_seeker_profile()
        assert seeker_profile.get_id() == self.get_id() # They should have same id
        self.seeker_ref = seeker_profile


    def _set_recruiter_profile(self, recruiter_profile: RecruiterProfile):
        # This is unexpected behavior if we try to set a recruiter profile while there is already one
        assert not self.has_recruiter_profile()
        assert recruiter_profile.get_id() == self.get_id() # They should have same id
        self.recruiter_ref = recruiter_profile



