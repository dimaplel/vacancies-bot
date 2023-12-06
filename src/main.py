import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from sweet_home import SweetHome
from config import Config

dp = Dispatcher()


@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await home.on_user_entry(message)


async def main() -> None:
    bot = Bot(token=cfg.token.get_secret_value())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.getLogger().setLevel(logging.INFO)
    cfg = Config()  # type: ignore
    home = SweetHome(cfg)
    asyncio.run(main())