import json
import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher, types, F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.profile_states import ProfileStates

dp = Dispatcher()
state_router = Router()

with open('config.json') as f:
    TOKEN = json.load(f)['token']

@dp.message(Command("start"))
async def command_start_handler(message: types.Message, state: FSMContext) -> None:
    # TODO: start command interaction
    await state.set_state(ProfileStates.name)
    await message.reply(f"Hello, {message.from_user.full_name}! Welcome to job-search bot. "
                        f"Let's complete your profile together, enter your full name.")


@dp.message(ProfileStates.name)
async def name_handler(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.reply(f"Nice to meet you, {html.quote(message.text)}! Now load your resume.", parse_mode='HTML')

async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())