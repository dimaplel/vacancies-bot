import numbers
from aiogram.types import Message

from config import Config
from psql_connection import PsqlConnection

from hashlib import sha3_256

class SweetHome:
    def __init__(self, cfg: Config) -> None:
        self._cfg = cfg
        self._sql_connection = PsqlConnection(
            cfg.postgres_name,
            cfg.postgres_host,
            cfg.postgres_user,
            cfg.postgres_pswd.get_secret_value()
        )
        
                
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