from aiogram.types import Message
from aiogram.utils.formatting import Italic
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router

from src.states.registration_states import EntryRegistrationStates
from src.states.menu_states import MenuStates
from src.sweet_home import sweet_home
from src.users.user_profile import UserProfile


entry_router = Router(name="Entry Router")


@entry_router.message(CommandStart())
async def entry_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user_profile = sweet_home.request_user_profile(user_id)
    if user_profile is not None:
        markup = user_profile.user_markup.get_current_markup()
        await message.answer("Welcome back! Choose from one of the options below.", reply_markup=markup)
        await state.set_state(MenuStates.options_handle)
        await state.set_data({"profile": user_profile})
        return
    
    await message.answer(f"Welcome to the Vacancies Bot 👨‍💻\n\n"
                         f"For registration purposes, enter your {Italic('first name').as_html()}.", parse_mode="HTML")
    await state.set_state(EntryRegistrationStates.first_name)


@entry_router.message(EntryRegistrationStates.first_name)
async def enter_first_name(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text)
    await message.answer(f"Nice to meet you, {message.text}! You have a lovely first name!\n\n"
                       f"Now, please provide me with your {Italic('last name').as_html()}.", parse_mode="HTML")
    await state.set_state(EntryRegistrationStates.last_name)


@entry_router.message(EntryRegistrationStates.last_name)
async def enter_last_name(message: Message, state: FSMContext) -> None:
    await state.update_data(last_name=message.text)
    data = await state.get_data()
    user_profile = UserProfile(message.from_user.id, data["first_name"], data["last_name"])
    sweet_home.add_user_profile(user_profile=user_profile)
    await message.answer("Your profile has been successfully registered! Choose from one of the options below.",
                         reply_markup=user_profile.user_markup.get_current_markup())
    await state.set_data({"profile": user_profile})
    await state.set_state(MenuStates.options_handle)