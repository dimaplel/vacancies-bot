from pydantic import SecretStr
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    token: SecretStr
    postgres_host: str
    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str
    postgres_port: int
    pgdata: str
    mongo_host: str
    mongo_dbname: str
    mongo_initdb_root_username: str
    mongo_initdb_root_password: SecretStr
    redis_host: str
    redis_username: str
    redis_password: SecretStr
    neo4j_host: str = "localhost"
    neo4j_user: str
    neo4j_password: SecretStr
    
    class Config:
        env_file = ".env"
        case_sensitive = False


cfg = Config()