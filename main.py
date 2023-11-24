import json
import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

dp = Dispatcher()

with open('config.json') as f:
    TOKEN = json.load(f)['token']

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.reply(f"Hello, {message.from_user.full_name}!")

@dp.message()
async def handler(message: Message) -> None:
    await message.reply(f"Sup!")


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())