import logging
import asyncio
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)

from aiogram import Bot, Dispatcher

from routers.entry_router import entry_router
from routers.profile_router import profile_router
from routers.seeker_router import seeker_router
from routers.recruiter_router import recruiter_router
from config import cfg


dp = Dispatcher()
dp.include_routers(entry_router, profile_router, seeker_router, recruiter_router)


async def main() -> None:
    bot = Bot(token=cfg.token.get_secret_value())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())