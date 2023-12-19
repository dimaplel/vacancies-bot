import logging

from typing import Dict, Any

from config import cfg
from connections import PsqlConnection, Neo4jConnection, RedisConnection, MongoDBConnection
from users.user_profile import UserProfile
from users.seeker_profile import SeekerProfile
from company_registry import CompanyRegistry


class SweetConnections:
    def __init__(self) -> None:
        self.cfg = cfg
        self.sql_connection = PsqlConnection(
            cfg.postgres_host,
            cfg.postgres_db,
            cfg.postgres_user,
            cfg.postgres_password.get_secret_value()
        )
        self.redis_connection = RedisConnection(
            cfg.redis_host,
            cfg.redis_password.get_secret_value()
        )
        self.mongodb_connection = MongoDBConnection(
            cfg.mongo_host,
            cfg.mongo_initdb_root_username,
            cfg.mongo_initdb_root_password.get_secret_value(),
            cfg.mongo_dbname
        )
        self.neo4j_connection = Neo4jConnection(
            cfg.neo4j_host,
            cfg.neo4j_user,
            cfg.neo4j_password.get_secret_value()
        )

        try:
            logging.info("Opening database connections")
            self.sql_connection.open()
            self.mongodb_connection.open()
            self.redis_connection.open()
            self.neo4j_connection.open()
            self._sql_db_init()
        except Exception as _:
            logging.warning("Failed to open some database connections")
            return
            

    def _sql_db_init(self):
        self.sql_connection.execute_query(f"""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id BIGINT PRIMARY KEY, 
                first_name VARCHAR(255), 
                last_name VARCHAR(255))""")

        # They should be created before because of the relationships between tables
        # For instance recruiter_profiles need companies table to exist 
        self.sql_connection.execute_query(f"""
            CREATE TABLE IF NOT EXISTS vacancies (
                recruiter_id BIGINT, 
                vacancy_doc_ref VARCHAR(255))""")

        self.sql_connection.execute_query(f"""
            CREATE TABLE IF NOT EXISTS companies (
                company_id SERIAL PRIMARY KEY, 
                name VARCHAR(255))""")

        self.sql_connection.execute_query(f"""
            CREATE TABLE IF NOT EXISTS seeker_profiles (
                user_id BIGINT PRIMARY KEY, 
                portfolio_ref VARCHAR(255) NOT NULL, 
                seeker_node_ref BIGINT NOT NULL)""")
            
        self.sql_connection.execute_query(f"""
            CREATE TABLE IF NOT EXISTS recruiter_profiles (
                user_id BIGINT PRIMARY KEY, 
                recruiter_node_ref BIGINT, 
                company_id INT,
                FOREIGN KEY (company_id) REFERENCES companies(company_id))""")



sweet_connections = SweetConnections()


class ProfileHome:
    def __init__(self, sweet_connections: SweetConnections):
        self._sweet_connections = sweet_connections
        self._company_registry = CompanyRegistry(self._sweet_connections.sql_connection,
                                                 self._sweet_connections.redis_connection)


    def request_seeker_profile(self, user_profile: UserProfile) -> bool:
        return user_profile.request_seeker_profile(self._sweet_connections.sql_connection)


    def add_seeker_profile(self, user_profile: UserProfile, portfolio: dict):
        user_profile.add_seeker_profile(
            portfolio, 
            self._sweet_connections.mongodb_connection, 
            self._sweet_connections.neo4j_connection, 
            self._sweet_connections.sql_connection
        )


    def add_company(self, company_name: str, company_employees: int, company_vacancies: int = 0):
        return self._company_registry.add_company(company_name, company_employees, company_vacancies)

    
    def request_recruiter_profile(self, user_profile: UserProfile) -> bool:
        return user_profile.request_recruiter_profile(self._sweet_connections.sql_connection)

    
    def add_recruiter_profile(self, user_profile: UserProfile, company_id: int):
        user_profile.add_recruiter_profile(
            company_id,
            self._sweet_connections.neo4j_connection,
            self._sweet_connections.sql_connection
        )


    def search_company_by_name(self, company_name: str):
        return self._company_registry.search_by_name(company_name)


    def get_company_metrics(self, company_id: int):
        return self._company_registry.get_metrics(company_id)


    def edit_user_profile(self, user_profile: UserProfile, first_name: str, last_name: str):
        user_profile.update(self._sweet_connections.sql_connection, first_name, last_name)


class SeekerHome:
    def __init__(self, sweet_connections: SweetConnections):
        self._sweet_connections = sweet_connections


    def request_seeker_profile(self, user_profile: UserProfile) -> bool:
        return user_profile.request_seeker_profile(self._sweet_connections.sql_connection)

    
    def request_seeker_portfolio(self, seeker_profile: SeekerProfile):
        # TODO: Add more checks (If portfolio is None?)
        return seeker_profile.get_portfolio(self._sweet_connections.mongodb_connection)


    def update_seeker_portfolio(self, seeker_profile: SeekerProfile, portfolio: Dict[str, Any]) -> bool:
        return seeker_profile.update_portfolio(self._sweet_connections.mongodb_connection, portfolio)


class RecruiterHome:
    def __init__(self, sweet_connections: SweetConnections):
        self._sweet_connections = sweet_connections



class SweetHome:
    def __init__(self, sweet_connections: SweetConnections) -> None:
        self._sweet_connections = sweet_connections
        self._user_cache: dict[int, UserProfile] = {}
        self.seeker_home = SeekerHome(sweet_connections)
        self.profile_home = ProfileHome(sweet_connections)


    def request_user_profile(self, user_id: int) -> (UserProfile | None):
        # Avoid querying sql connection everytime using cached values
        # cached values must ensure they are always up-to-date with sql connection and vice versa
        user_profile: (UserProfile | None) = self._user_cache.get(user_id)
        if user_profile is not None:
            return user_profile

        row = self._sweet_connections.sql_connection.execute_query_fetchone(
            f"SELECT * FROM user_profiles WHERE user_id = {user_id}")
        if row is None:
            return None

        first_name = row['first_name']
        last_name = row['last_name']
        # We do not specify seeker_profile and recruiter_profile here. Those will be set explicitly
        user_profile = UserProfile(user_id, first_name, last_name)
        
        if not user_profile.request_seeker_profile(self._sweet_connections.sql_connection):
            logging.info("Could not set a seeker profile for user with id %d", user_id)
            logging.info("Registration of the seeker profile will be required")

        if not user_profile.request_recruiter_profile(self._sweet_connections.sql_connection):
            logging.info("Could not set a recruiter profile for user with id %d", user_id)
            logging.info("Registration of the recruiter profile will be required")

        # Cache user profile value in map
        self._user_cache[user_id] = user_profile
        return user_profile


    def add_user_profile(self, user_profile: UserProfile):
        assert self.request_user_profile(user_profile.get_id()) is None
        user_id = user_profile.get_id()
        self._user_cache[user_id] = user_profile
        self._sweet_connections.sql_connection.execute_query(f"INSERT INTO user_profiles (user_id, first_name, last_name) "
                                           f"VALUES (%s, %s, %s)",
                                           user_id, user_profile.first_name, user_profile.last_name)


sweet_home = SweetHome(sweet_connections)