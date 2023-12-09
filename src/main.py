import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from sweet_home import entry_router
from config import cfg


dp = Dispatcher()
dp.include_router(entry_router)


async def main() -> None:
    bot = Bot(token=cfg.token.get_secret_value())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.getLogger().setLevel(logging.INFO)
    asyncio.run(main())