import logging

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Italic, Bold

from src.states.menu_states import MenuStates
from src.states.registration_states import SeekerPortfolioUpdateStates
from src.users.user_profile import UserProfile
from src.users.seeker_profile import SeekerProfile
from src.sweet_home import sweet_home

from src.keyboards.seeker_inline_keyboards import (NoExperienceInlineKeyboardMarkup, 
                                                SeekerPortfolioEditingInlineKeyboardMarkup, 
                                                PortfolioAdditionInlineKeyboardMarkup,
                                                SeekerVacancySearchingInlineKeyboardMarkup)


seeker_router = Router(name="Seeker Router")


@seeker_router.message(F.text, MenuStates.seeker_home)
async def seeker_home(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    
    seeker_profile: SeekerProfile = user_profile.seeker_ref
    assert seeker_profile is not None
    
    seeker_markup = seeker_profile.seeker_markup
    if message.text == seeker_markup.get_button_text("edit_portfolio_button"):
        await message.answer("You are about to update your portfolio "
            "(This will discard your current data and set a new one in its place).",
                             reply_markup=SeekerPortfolioEditingInlineKeyboardMarkup().get_current_markup())
        await state.set_state(MenuStates.seeker_profile_editing)

    elif message.text == seeker_markup.get_button_text("search_vacancies_button"):
        vsc = sweet_home.seeker_home.add_search_context(user_id)
        if vsc is None:
            await message.answer("Failed to request valid vacancy search context",
                reply_markup=seeker_profile.seeker_markup.get_current_markup())
            await state.set_state(MenuStates.seeker_home)
            return

        first_vacancy = vsc.get_current_vacancy()
        if first_vacancy is None:
            await message.answer("There is no vacancies here!",
                reply_markup=seeker_profile.seeker_markup.get_current_markup())
            await state.set_state(MenuStates.seeker_home)
            return

        await message.answer(f"Welcome to vacancies search. First vacancy is: {first_vacancy.get_id()}", 
            reply_markup=SeekerVacancySearchingInlineKeyboardMarkup().get_current_markup())
        await state.set_state(MenuStates.seeker_vacancy_search)
    
    elif message.text == seeker_markup.get_button_text("back_button"):
        await message.answer("Returning back to user profile menu", 
            reply_markup=user_profile.user_markup.get_current_markup())
        await state.set_state(MenuStates.profile_home)
        

@seeker_router.callback_query(F.data == "portfolio", MenuStates.seeker_profile_editing)
async def on_portfolio_edit(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    
    seeker_profile: SeekerProfile = user_profile.seeker_ref
    assert seeker_profile is not None
    
    portfolio = sweet_home.seeker_home.request_seeker_portfolio(seeker_profile)
    if portfolio is None:
        logging.error("Failed to retrieve portfolio...")
        await call.message.answer("Failed to retrieve portfolio!", 
            reply_markup=seeker_profile.seeker_markup.get_current_markup())
            
        await call.message.delete()
        await state.set_state(MenuStates.seeker_home)
        return

    await call.message.answer("Enter the position you are looking for:")
    await call.message.delete()

    await state.set_data({})
    await state.update_data(portfolio_ref=portfolio)
    
    await state.set_state(SeekerPortfolioUpdateStates.position)


@seeker_router.callback_query(F.data == "back", MenuStates.seeker_profile_editing)
async def on_back(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    
    seeker_profile: SeekerProfile = user_profile.seeker_ref
    assert seeker_profile is not None

    await call.message.answer("Returning back to seeker home menu", 
        reply_markup=seeker_profile.seeker_markup.get_current_markup())
    await call.message.delete()
    await state.set_state(MenuStates.seeker_home)


@seeker_router.message(F.text, SeekerPortfolioUpdateStates.position)
async def on_portfolio_position_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    portfolio_ref = data['portfolio_ref']

    updated_position: str = message.text
    portfolio_ref['position'] = updated_position

    await message.answer(f"OK, now we proceed with your working experience.\n\n"
                         f"Enter your experience title {Italic('For instance: Developer at ABC Inc.').as_html()} "
                         f"if you have one or press the button below.",
                         parse_mode="HTML", 
                         reply_markup=NoExperienceInlineKeyboardMarkup().get_current_markup())
    await state.set_state(SeekerPortfolioUpdateStates.experience_title)


@seeker_router.callback_query(F.data == "no-exp", SeekerPortfolioUpdateStates.experience_title)
async def no_prior_experience(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    
    seeker_profile: SeekerProfile = user_profile.seeker_ref
    assert seeker_profile is not None

    data = await state.get_data()
    portfolio_ref = data['portfolio_ref']
    sweet_home.seeker_home.update_seeker_portfolio(seeker_profile, portfolio_ref)

    await call.message.answer(f"{Bold('You have successfully updated your portfolio.').as_html()}\n\n"
                              f"{Bold('— Name:').as_html()} {user_profile.get_full_name()}\n"
                              f"{Bold('— Desired position:').as_html()} {portfolio_ref['position']}",
                              parse_mode="HTML",
                              reply_markup=seeker_profile.seeker_markup.get_current_markup())
                              
    await call.message.delete()
    await state.set_data({})
    await state.set_state(state=MenuStates.seeker_home)


@seeker_router.message(F.text, SeekerPortfolioUpdateStates.experience_title)
async def on_portfolio_experience_title_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    portfolio_ref = data['portfolio_ref']

    if portfolio_ref.get("experiences") is None:
        portfolio_ref["experiences"] = [{"title": message.text}]
    else:
        portfolio_ref["experiences"].append({"title": message.text})

    await message.answer("Noted! Now, enter the description of your previous experience.")
    await state.set_state(SeekerPortfolioUpdateStates.experience_desc)
    

@seeker_router.message(F.text, SeekerPortfolioUpdateStates.experience_desc)
async def add_experience_desc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    portfolio_ref = data['portfolio_ref']

    logging.info(f"Current portfolio: {portfolio_ref.get('experiences')}")
    
    experiences = portfolio_ref.get("experiences")
    exp_idx = len(experiences) - 1
    
    experiences[exp_idx].update(desc = message.text)

    await message.answer("Good one! Now enter a time frame you have had this experience at.")
    await state.set_state(SeekerPortfolioUpdateStates.experience_timeline)


@seeker_router.message(F.text, SeekerPortfolioUpdateStates.experience_timeline)
async def add_experience_timeline(message: types.Message, state: FSMContext):
    data = await state.get_data()
    portfolio_ref = data['portfolio_ref']
    
    experiences = portfolio_ref.get("experiences")
    exp_idx = len(experiences) - 1

    experiences[exp_idx].update({"timeline": message.text})
    experiences_text = ""
    for exp in experiences:
        experiences_text += (f"{Bold('— Title: ').as_html()} {exp['title']}\n"
                             f"{Bold('— Description: ').as_html()} {exp['desc']}\n"
                             f"{Bold('— Duration: ').as_html()} {exp['timeline']}\n\n")
    await message.answer(f"{Bold('Your current experiences: ').as_html()}\n\n{experiences_text}"
                         f"Please choose an option and press a button below.",
                         parse_mode='HTML', 
                         reply_markup=PortfolioAdditionInlineKeyboardMarkup().get_current_markup())
    await state.set_state(SeekerPortfolioUpdateStates.confirm_or_add_portfolio)


@seeker_router.callback_query(F.data == "conf-exp", SeekerPortfolioUpdateStates.confirm_or_add_portfolio)
async def confirm_portfolio(call: types.CallbackQuery, state: FSMContext):

    user_id = call.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    
    seeker_profile: SeekerProfile = user_profile.seeker_ref
    assert seeker_profile is not None

    data = await state.get_data()
    portfolio_ref = data["portfolio_ref"]
    if not sweet_home.seeker_home.update_seeker_portfolio(seeker_profile, portfolio_ref):
        # TODO: Handle this somehow
        logging.error("Failed to update seeker's portfolio!")
    
    experiences_text = ""
    for exp in portfolio_ref.get("experiences"):
        experiences_text += (f"{Bold('— Title: ').as_html()} {exp['title']}\n"
                             f"{Bold('— Description: ').as_html()} {exp['desc']}\n"
                             f"{Bold('— Duration').as_html()} {exp['timeline']}\n\n")
    await call.message.answer(f"{Bold('You have successfully updated your portfolio.').as_html()}\n\n"
                              f"{Bold('— Name:').as_html()} {user_profile.get_full_name()}\n"
                              f"{Bold('— Desired position:').as_html()} {portfolio_ref['position']}\n\n" 
                              f"{Bold('— Portfolio: ').as_html()}\n\n{experiences_text}",
                              parse_mode="HTML",
                              reply_markup=seeker_profile.seeker_markup.get_current_markup())

    await call.message.delete()
    await state.set_data({})
    await state.set_state(state=MenuStates.seeker_home)



@seeker_router.callback_query(F.data == "add-exp", SeekerPortfolioUpdateStates.confirm_or_add_portfolio)
async def add_more_experience(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(f"Let's add another experience!\n\n"
                         f"Enter your experience title {Italic('For instance: Developer at ABC Inc.').as_html()}",
                         parse_mode="HTML")
    await state.set_state(SeekerPortfolioUpdateStates.experience_title)