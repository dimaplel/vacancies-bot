import logging
import asyncio
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from src.config import Config
from src.config import ConfigField
from src.psql_database import PsqlDatabase

dp = Dispatcher()

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.reply(f"Hello, {message.from_user.full_name}!")

@dp.message()
async def handler(message: Message) -> None:
    await message.reply(f"Sup!")


cfg = Config(os.path.abspath(os.getcwd()) + r"/config.json")
db: PsqlDatabase = None


@dp.startup()
async def on_startup() -> None:
    logging.info("Starting up the bot")

    db_host = cfg.get_field(ConfigField.SQL_HOST)
    db_name = cfg.get_field(ConfigField.SQL_NAME)
    db_user = cfg.get_field(ConfigField.SQL_USER)
    db_pswd = cfg.get_field(ConfigField.SQL_PSWD)
    db = PsqlDatabase(db_name, db_host)
    db.open(db_user, db_pswd)
    

@dp.shutdown()
async def on_shutdown() -> None:
    logging.info("Shutting down the bot")
    db.close()


async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    bot = Bot(token=cfg.get_field(ConfigField.BOT_TOKEN))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())