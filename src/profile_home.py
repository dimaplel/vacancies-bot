import logging

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Italic

from users.user_profile import UserProfile
from keyboards.function_choice_keyboard import function_choice_keyboard
from keyboards.no_experience_keyboard import no_experience_keyboard
from states.seeker_registration_states import SeekerRegistrationStates


function_choice_buttons = [button.text for row in function_choice_keyboard().keyboard for button in row]


profile_router = Router()

@profile_router.message(F.text == function_choice_buttons[0]) # Seeker menu button
async def register_seeker(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_profile: UserProfile = data["profile"]
    if user_profile.has_seeker_profile():
        # TODO: implement menu for existing seeker
        return
    await message.answer("To become a seeker, you should make a portfolio.\n\n"
                         "Enter the position you would like to apply for.")
    await state.set_state(SeekerRegistrationStates.position)


@profile_router.message(F.text & SeekerRegistrationStates.position)
async def ask_experience_title(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer(f"OK, now we proceed with your working experience.\n\n"
                         f"Enter your experience title {Italic('For instance: Developer at ABC Inc.').as_html()}",
                         parse_mode="HTML", reply_markup=no_experience_keyboard())
    await state.set_state(SeekerRegistrationStates.experience_title)



@profile_router.callback_query((F.data == "no-exp") & SeekerRegistrationStates.experience_title)
async def no_prior_experience(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    portfolio = {"position": data["position"]}
