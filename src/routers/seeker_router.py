import logging

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Italic, Bold

from src.states.menu_states import MenuStates
from src.users.user_profile import UserProfile
from src.users.seeker_profile import SeekerProfile
from src.sweet_home import sweet_home

from src.keyboards.seeker_inline_keyboards import SeekerPortfolioEdittingInlineKeyboardMarkup


seeker_router = Router(name="Seeker Router")


@seeker_router.message(F.text, MenuStates.seeker_home)
async def seeker_home(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    
    seeker_profile: SeekerProfile = user_profile.seeker_ref
    assert seeker_profile is not None
    
    seeker_markup = seeker_profile.seeker_markup
    if message.text == seeker_markup.get_button_text("edit_portfolio_button"):
        # TODO: Handle portfolio editting logic
        await message.answer("You are about to update your portfolio "
            "(This will discard your current data and set a new one in its place)", 
            reply_markup=SeekerPortfolioEdittingInlineKeyboardMarkup().get_current_markup())
        await state.set_state(MenuStates.seeker_profile_editting)

    elif message.text == seeker_markup.get_button_text("search_vacancies_button"):
        # TODO: Handle vacancy searching logic
        pass
    elif message.text == seeker_markup.get_button_text("back_button"):
        await message.answer("Returning back to user profile menu", 
            reply_markup=user_profile.user_markup.get_current_markup())
        await state.set_state(MenuStates.profile_home)
        

@seeker_router.callback_query(F.data == "portfolio", MenuStates.seeker_profile_editting)
async def on_portfolio_edit(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    
    seeker_profile: SeekerProfile = user_profile.seeker_ref
    assert seeker_profile is not None

    await call.message.answer("NOIMPL", reply_markup=seeker_profile.seeker_markup.get_current_markup())
    await call.message.delete()
    await state.set_state(MenuStates.seeker_home)


@seeker_router.callback_query(F.data == "position", MenuStates.seeker_profile_editting)
async def on_position_update(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    
    seeker_profile: SeekerProfile = user_profile.seeker_ref
    assert seeker_profile is not None

    await call.message.answer("NOIMPL", reply_markup=seeker_profile.seeker_markup.get_current_markup())
    await call.message.delete()
    await state.set_state(MenuStates.seeker_home)


@seeker_router.callback_query(F.data == "back", MenuStates.seeker_profile_editting)
async def on_position_update(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    
    seeker_profile: SeekerProfile = user_profile.seeker_ref
    assert seeker_profile is not None

    await call.message.answer("Returning back to seeker home menu", 
        reply_markup=seeker_profile.seeker_markup.get_current_markup())
    await call.message.delete()
    await state.set_state(MenuStates.seeker_home)