import logging
import asyncio
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from config import Config
from databases.psql_connection import PsqlConnection

dp = Dispatcher()

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.reply(f"Hello, {message.from_user.full_name}!")

@dp.message()
async def handler(message: Message) -> None:
    await message.reply(f"Sup!")


cfg = Config()
db: PsqlConnection = None


@dp.startup()
async def on_startup() -> None:
    logging.info("Starting up the bot")

    db_host = cfg.postgres_host
    db_name = cfg.postgres_db
    db_user = cfg.postgres_user
    db_pswd = cfg.postgres_password.get_secret_value()
    db = PsqlConnection(db_host=db_host, db_name=db_name, db_user=db_user, db_pswd=db_pswd)
    db.open()

@dp.shutdown()
async def on_shutdown() -> None:
    logging.info("Shutting down the bot")
    db.close()


async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    bot = Bot(token=cfg.token.get_secret_value())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())