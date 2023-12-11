import logging

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Italic, Bold

from users.user_profile import UserProfile
from sweet_home import menu
from keyboards.profile_keyboards import UserProfileKeyboardMarkup, UserProfileKeyboardTypes
from keyboards.no_experience_keyboard import no_experience_keyboard
from states.seeker_registration_states import SeekerRegistrationStates
from states.entry_registration_states import EntryRegistrationStates


profile_markup = UserProfileKeyboardMarkup()
register_profiles_keyboard = profile_markup.get_current_markup()
register_profile_buttons = [button.text for row in register_profiles_keyboard.keyboard for button in row]
profile_markup.set_type(UserProfileKeyboardTypes.SEEKER)
seeker_access_keyboard = profile_markup.get_current_markup()
profile_markup.set_type(UserProfileKeyboardTypes.RECRUITER)
recruiter_access_keyboard = profile_markup.get_current_markup()
profile_markup.set_type(UserProfileKeyboardTypes.FULL)
full_access_keyboard = profile_markup.get_current_markup()


profile_router = Router()

@profile_router.message(F.text == register_profile_buttons[0], EntryRegistrationStates.options_handle) # Seeker menu button
async def register_seeker(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_profile: UserProfile = data["profile"]
    if user_profile.has_seeker_profile():
        # TODO: implement menu for existing seeker
        return
    await message.answer("To become a seeker, you should make a portfolio.\n\n"
                         "Enter the position you would like to apply for.")
    await state.set_state(SeekerRegistrationStates.position)


@profile_router.message(F.text, SeekerRegistrationStates.position)
async def ask_experience_title(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer(f"OK, now we proceed with your working experience.\n\n"
                         f"Enter your experience title {Italic('For instance: Developer at ABC Inc.').as_html()} "
                         f"if you have one or press the button below.",
                         parse_mode="HTML", reply_markup=no_experience_keyboard())
    await state.set_state(SeekerRegistrationStates.experience_title)



@profile_router.callback_query(F.data == "no-exp", SeekerRegistrationStates.experience_title)
async def no_prior_experience(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    portfolio = {"position": data["position"], "experiences": []}
    user_profile: UserProfile = data["profile"]
    menu.add_seeker_profile(call.from_user.id, portfolio)
    await call.message.answer(f"{Bold('You have successfully registered a seeker profile.').as_html()}\n\n"
                              f"{Bold('— Name:').as_html()} {user_profile.get_full_name()}\n"
                              f"{Bold('— Desired position:').as_html()} {data['position']}\n\n" +
                              Italic("You may now access seeker menu!").as_html(),
                              parse_mode="HTML",
                              reply_markup=(full_access_keyboard if user_profile.has_recruiter_profile()
                                            else seeker_access_keyboard))
    await call.message.delete()
