import logging
import re

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
                                                SeekerVacacnyFiltersInlineKeyboardMarkup, 
                                                PortfolioAdditionInlineKeyboardMarkup)


seeker_router = Router(name="Seeker Router")


def get_seeker_profile(user_id: int) -> SeekerProfile:
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    
    seeker_profile: SeekerProfile = user_profile.seeker_ref
    assert seeker_profile is not None
    return seeker_profile


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
        res = sweet_home.seeker_home.create_search_context(seeker_profile)
        assert res

        vsc = seeker_profile.vacancies_search_context
        if vsc.empty_context:
            await message.answer("There is no vacancies here!",
                reply_markup=seeker_profile.seeker_markup.get_current_markup())
            await state.set_state(MenuStates.seeker_home)
            return

        await message.answer(
            "Welcome to vacancies search. Do you want to enter filters before entering the search?\n"
            "You can enter the desired annual salary by entering the range (For example \"5000, 10000\")",
            reply_markup=SeekerVacacnyFiltersInlineKeyboardMarkup().get_current_markup())
        await state.set_data({})
        await state.set_state(MenuStates.seeker_vacancy_filters)
    
    elif message.text == seeker_markup.get_button_text("back_button"):
        await message.answer("Returning back to user profile menu", 
            reply_markup=user_profile.user_markup.get_current_markup())
        await state.set_data({})
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
        logging.error("Failed to update seeker's portfolio!")
        await call.message.answer("Unexpected behaviour detected while updating your portfolio, you were returned to "
                                  "the seeker profile menu.",
                                  reply_markup=seeker_profile.seeker_markup.get_current_markup())
        await call.message.delete()
        return

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


def get_vacancy_message(vacancy) -> str:
    data = sweet_home.recruiter_home.get_vacancy_data(vacancy)
    return f"Vacancy is: {vacancy.get_id()} - {data['position']} with annual salary of ${data['salary']}"
    

@seeker_router.callback_query(F.data == "prev", MenuStates.seeker_vacancy_search)
async def on_prev_pressed_search(call: types.CallbackQuery, state: FSMContext):
    seeker_profile = get_seeker_profile(call.from_user.id)
    vsc = seeker_profile.vacancies_search_context
    assert vsc is not None

    data = await state.get_data()
    desired_salary: (tuple[int, int] | None) = data.get('desired_salary')
    desired_position = data.get('desired_position')
    if not vsc.jump_prev_vacancy_with_filters(desired_salary, desired_position):
        logging.error("Failed to decrement")

    vacancy = vsc.get_current_vacancy()
    await call.message.answer(
        get_vacancy_message(vacancy), 
        reply_markup=vsc.inline_markup.get_current_markup())
    await call.message.delete()


@seeker_router.callback_query(F.data == "back", MenuStates.seeker_vacancy_search)
async def on_back_pressed_search(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    
    seeker_profile: SeekerProfile = user_profile.seeker_ref
    assert seeker_profile is not None

    await call.message.answer("Returning back to seeker home", 
        reply_markup=seeker_profile.seeker_markup.get_current_markup())
    await call.message.delete()
    await state.set_state(MenuStates.seeker_home)


@seeker_router.callback_query(F.data == "next", MenuStates.seeker_vacancy_search)
async def on_next_pressed_search(call: types.CallbackQuery, state: FSMContext):
    seeker_profile = get_seeker_profile(call.from_user.id)
    vsc = seeker_profile.vacancies_search_context
    assert vsc is not None

    data = await state.get_data()
    desired_salary: (tuple[int, int] | None) = data.get('desired_salary')
    desired_position = data.get('desired_position')
    if not vsc.jump_next_vacancy_with_filters(desired_salary, desired_position):
        logging.error("Failed to decrement")

    vacancy = vsc.get_current_vacancy()
    await call.message.answer(
        get_vacancy_message(vacancy), 
        reply_markup=vsc.inline_markup.get_current_markup())
    await call.message.delete()


@seeker_router.callback_query(F.data == "filter_salary", MenuStates.seeker_vacancy_filters)
async def on_vacancy_filters_salary(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Enter the desired annual salary by entering the range (For example \"5000, 10000\")")
    await call.message.delete()
    await state.set_state(MenuStates.seeker_vacancy_filters_salary)


salary_regex = r"(\d+)\s*,\s*(\d+)"
@seeker_router.message(F.text.regexp(salary_regex), MenuStates.seeker_vacancy_filters_salary)
async def on_salary_filter_message(message: types.Message, state: FSMContext):
    # The regex groups (min_salary and max_salary) are captured and can be accessed
    match = re.match(salary_regex, message.text)
    if not match:
        logging.error(f"Failed to parse salary for message \"{message.text}\"!")
        await message.answer("Failed to parse salary. Enter the desired annual salary in format \"5000, 10000\")")
        return

    min_salary, max_salary = map(int, match.groups())

    await message.answer(
        f"Salary range set to: {min_salary} - {max_salary}",
        reply_markup=SeekerVacacnyFiltersInlineKeyboardMarkup().get_current_markup())
    await message.delete()
    await state.update_data(desired_salary = (min_salary, max_salary))
    await state.set_state(MenuStates.seeker_vacancy_filters)


@seeker_router.callback_query(F.data == "filter_position", MenuStates.seeker_vacancy_filters)
async def on_vacancy_filters_position(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Enter the desired position (For example \"C++ Developer\" or just \"C++\")")
    await call.message.delete()
    await state.set_state(MenuStates.seeker_vacancy_filters_position)


@seeker_router.message(F.text, MenuStates.seeker_vacancy_filters_position)
async def on_position_filter_message(message: types.Message, state: FSMContext):
    desired_position = message.text;
    await message.answer(
        f"Desired position is set to: {desired_position}",
        reply_markup=SeekerVacacnyFiltersInlineKeyboardMarkup().get_current_markup())
    await message.delete()
    await state.update_data(desired_position=desired_position)
    await state.set_state(MenuStates.seeker_vacancy_filters)


@seeker_router.callback_query(F.data == "done", MenuStates.seeker_vacancy_filters)
async def on_vacancy_filters_back(call: types.CallbackQuery, state: FSMContext):
    seeker_profile = get_seeker_profile(call.from_user.id)
    vsc = seeker_profile.vacancies_search_context
    
    # Filters
    data = await state.get_data()
    desired_salary: (tuple[int, int] | None) = data.get('desired_salary')
    desired_position = data.get('desired_position')

    logging.info(f"Filters are {desired_salary}, {desired_position}")

    # We need to manually check if FIRST vacancy is suitable!
    position_regex = None
    if desired_position is not None:
        position_regex = re.compile(re.escape(desired_position), re.IGNORECASE)

    first_vacancy = None
    if vsc.is_current_vacancy_by_filters(desired_salary, position_regex):
        logging.info("Picked current vacancy as it is filtered already")
        first_vacancy = vsc.get_current_vacancy()
    elif vsc.jump_next_vacancy_with_filters(desired_salary, desired_position):
        logging.info("Jumped from first to filtered")
        first_vacancy = vsc.get_current_vacancy()

    if first_vacancy is None:
        await call.message.answer(
            "There is no vacancies that would match your filters. Returning back to seeker home menu",
            reply_markup=seeker_profile.seeker_markup.get_current_markup())
        await call.message.delete()
        await state.set_state(MenuStates.seeker_home)
        return

    await call.message.answer(
        f"Successfully found vacancies matching specified filters (if any). Here are the vacancies:\n" +
        get_vacancy_message(first_vacancy),
        reply_markup=vsc.inline_markup.get_current_markup())
    await call.message.delete()
    await state.set_state(MenuStates.seeker_vacancy_search)