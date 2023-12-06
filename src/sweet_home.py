import logging
from aiogram.types import Message

from config import Config
from databases.psql_connection import PsqlConnection
from databases.redis_connection import RedisConnection
from databases.mongodb_connection import MongoDBConnection
from databases.neo4j_connection import Neo4jConnection


from hashlib import sha3_256

class SweetHome:
    def __init__(self, cfg: Config) -> None:
        self._cfg = cfg
        self._sql_connection = PsqlConnection(
            cfg.postgres_host,
            cfg.postgres_db,
            cfg.postgres_user,
            cfg.postgres_password.get_secret_value()
        )
        self._redis_connection = RedisConnection(
            cfg.redis_host,
            cfg.redis_username,
            cfg.redis_password.get_secret_value()
        )
        self._mongodb_connection = MongoDBConnection(
            cfg.mongo_host,
            cfg.mongo_initdb_root_username,
            cfg.mongo_initdb_root_password.get_secret_value(),
            cfg.mongo_dbname
        )
        self._neo4j_connection = Neo4jConnection(
            cfg.neo4j_host,
            cfg.neo4j_user,
            cfg.neo4j_password.get_secret_value()
        )

        try:
            logging.info("Opening databases connections")
            self._sql_connection.open()
            self._mongodb_connection.open()
            self._redis_connection.open()
            self._neo4j_connection.open()
        except Exception as e:
            pass

                
    async def on_user_entry(self, message: Message) -> None:
        recepient = message.from_user
        assert recepient is not None
        
        telegram_id = recepient.id
        encrypted_id = self.encode_id(telegram_id)
        
        await message.reply(f"Hello, {encrypted_id}")
        
        
    def encode_id(self, telegram_id) -> str:
        num_bytes = str(telegram_id).encode("utf-8")
        sha3_hash = sha3_256(num_bytes)
        return sha3_hash.hexdigest()