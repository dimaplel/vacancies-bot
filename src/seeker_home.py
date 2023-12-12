from src.users.seeker_profile import SeekerProfile
from src.users.user_profile import UserProfile
from src.connections import PsqlConnection, Neo4jConnection, RedisConnection, MongoDBConnection


class SeekerHome:
    def __init__(self, psql_connection: PsqlConnection, mongodb_connection: MongoDBConnection):
        self._sql_connection = psql_connection
        self._mongodb_connection = mongodb_connection
        return

    
    def request_seeker_portfolio(self, seeker_profile: SeekerProfile):
        self._mongodb_connection.get_document()

