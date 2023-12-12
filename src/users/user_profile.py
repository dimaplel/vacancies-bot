import logging
from dataclasses import dataclass

from src.users.seeker_profile import SeekerProfile
from src.users.recruiter_profile import RecruiterProfile
from src.connections import PsqlConnection, Neo4jConnection, MongoDBConnection
from src.keyboards.profile_keyboards import UserProfileKeyboardMarkup

@dataclass
class UserProfile:
    _user_id: int
    first_name: str
    last_name: str
    seeker_ref: SeekerProfile = None
    recruiter_ref: RecruiterProfile = None
    user_markup = UserProfileKeyboardMarkup()


    def get_full_name(self):
        return self.first_name + " " + self.last_name


    def update(self, sql_connection: PsqlConnection):
        sql_connection.execute_query(f"""
            UPDATE user_profiles 
            SET first_name = %s, last_name = %s 
            WHERE user_id = {self.get_id()}""", self.first_name, self.last_name)


    def get_id(self) -> int:
        return self._user_id


    def add_seeker_profile(self, portfolio: dict, mongodb_connection: MongoDBConnection, neo4j_connection: Neo4jConnection,
                           psql_connection: PsqlConnection):
        user_id = self.get_id()
        portfolio_ref = mongodb_connection.insert_document("portfolios", portfolio)
        result = neo4j_connection.run_query("CREATE (s:Seeker {user_id: $user_id}) RETURN ID(s) AS seeker_id",
                                            {"user_id": user_id})
        if len(result) == 0:
            logging.error("Error while adding portfolio into Neo4J")
            return

        seeker_node_ref = result[0]["seeker_id"]
        psql_connection.execute_query("INSERT INTO seeker_profiles VALUES (%s, %s, %s)",
                                      user_id, portfolio_ref, seeker_node_ref)
        self._set_seeker_profile(SeekerProfile(user_id, portfolio_ref, seeker_node_ref))


    def request_seeker_profile(self, psql_connection: PsqlConnection) -> bool:
        """
        Returns False if the seeker profile was not set for a provided user
        Calling this method when user's seeker profile was already set results in runtime error
        A profile won't be set, thus returning False, if:
           - there is no seeker profile associated with the provided user_id

        Otherwise, the method should return True
        """
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


    def request_recruiter_profile(self, psql_connection: PsqlConnection) -> bool:
        """
        Returns False is the recruiter profile was not set for a provided user
        Calling this method when user's recruiter profile was already set results in runtime error
        A profile won't be set, thus returning False, if:
          - there is no recruiter profile associated with the provided user_id

        Otherwise, the method should return True
        """
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
        self.user_markup.set_button_value("seeker_button", "Seeker Menu 🔍")
        self.seeker_ref = seeker_profile


    def _set_recruiter_profile(self, recruiter_profile: RecruiterProfile):
        # This is unexpected behavior if we try to set a recruiter profile while there is already one
        assert not self.has_recruiter_profile()
        assert recruiter_profile.get_id() == self.get_id() # They should have same id
        self.user_markup.set_button_value("recruiter_button", "Recruiter Menu 📝")
        self.recruiter_ref = recruiter_profile



