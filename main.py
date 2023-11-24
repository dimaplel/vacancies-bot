import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

import src.config as cfg
from src.config import ConfigField as CfgField

dp = Dispatcher()

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.reply(f"Hello, {message.from_user.full_name}!")

@dp.message()
async def handler(message: Message) -> None:
    await message.reply(f"Sup!")


async def main() -> None:
    config = cfg.Config("config.json")
    bot = Bot(config.get_field(CfgField.BOT_TOKEN))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())