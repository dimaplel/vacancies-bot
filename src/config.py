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
    mongo_initdb_root_username: str
    mongo_initdb_root_password: str
    redis_host: str


    class Config:
        env_file = ".env"
        case_sensitive = False


