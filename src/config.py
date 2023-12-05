import json
import logging

from pydantic import SecretStr
from pydantic_settings import BaseSettings

from enum import StrEnum

class ConfigField(StrEnum):
    BOT_TOKEN = "bot.token",
    SQL_HOST = "sql.db_host",
    SQL_NAME = "sql.db_name",
    SQL_USER = "sql.db_user",
    SQL_PSWD = "sql.db_pswd",
    REDIS_HOST = "redis.db_host",
    REDIS_USER = "redis.db_user",
    REDIS_PASSWORD = "redis.db_pswd",
    COUCHDB_URL = "couchdb.db_url",
    COUCHDB_NAME = "couchdb.db_name"


class Config(BaseSettings):
    token: SecretStr
    postgres_host: str
    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str
    mongodb_initdb_root_username: str
    mongodb_initdb_root_password: str


    class Config:
        env_file = ".env"
        case_sensitive = False


