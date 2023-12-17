import logging

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Italic, Bold

from src.states.menu_states import MenuStates
from src.users.user_profile import UserProfile
from src.users.recruiter_profile import RecruiterProfile
from src.sweet_home import sweet_home


recruiter_router = Router(name="Recruiter Router")


@recruiter_router.message(F.text, MenuStates.recruiter_home)
async def recruiter_home(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    
    recruiter_profile: RecruiterProfile = user_profile.recruiter_ref
    assert recruiter_profile is not None

    recruiter_markup = recruiter_profile.recruiter_markup
    if message.text == recruiter_markup.get_button_text("add_vacancy_button"):
        # TODO: Handle adding vacancies
        pass
    elif message.text == recruiter_markup.get_button_text("your_vacancies_button"):
        # TODO: Handle vacancies list info
        pass
    elif message.text == recruiter_markup.get_button_text("back_button"):
        await message.answer("Returning back to user profile menu", reply_markup=user_profile.user_markup.get_current_markup())
        await state.set_state(MenuStates.profile_home)