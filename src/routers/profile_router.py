import logging

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Italic, Bold

from src.sweet_home import sweet_home
from src.users.user_profile import UserProfile
from src.users.seeker_profile import SeekerProfile
from src.users.recruiter_profile import RecruiterProfile
from src.users.company import Company
from src.keyboards.recruiter_inline_keyboards import (NoExperienceInlineKeyboardMarkup,
                                                      PortfolioAdditionInlineKeyboardMarkup,
                                                      SearchOrRegisterInlineKeyboardMarkup,
                                                      CompaniesChoiceInlineKeyboardMarkup)
from src.states.registration_states import SeekerRegistrationStates, RecruiterRegistrationStates
from src.states.menu_states import MenuStates


profile_router = Router(name="Profile Router")


# Handle options from profile menu
@profile_router.message(F.text, MenuStates.profile_home)
async def profile_home(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    assert user_profile is not None
    
    user_markup = user_profile.user_markup
    if message.text == user_markup.get_button_text("seeker_button"):
        if not sweet_home.profile_home.request_seeker_profile(user_profile):
            # Do seeker profile registration
            await message.answer("To become a seeker, you will need to make a portfolio.\n\n"
                                "Enter the position you would like to apply for.",
                                reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
            await state.set_state(SeekerRegistrationStates.position)
        else: # We have seeker profile - proceed to seeker home menu
            seeker_profile: SeekerProfile = user_profile.seeker_ref
            assert seeker_profile is not None
            
            await state.set_state(MenuStates.seeker_home)
            await message.answer(f"Successfully entered your seeker profile, {user_profile.first_name}\n"
                "Select an action from the menu below", 
                reply_markup=seeker_profile.seeker_markup.get_current_markup())

    elif message.text == user_markup.get_button_text("recruiter_button"):
        if not sweet_home.profile_home.request_recruiter_profile(user_profile):
            # Do recruiter profile registration
            await message.answer("To become a recruiter, you should choose/create a company you're hiring for.\n\n"
                                "Enter the name of your company and we will search for it.",
                                reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
            await state.set_state(RecruiterRegistrationStates.enter_company)

        else: # We have recruiter profile - proceed to recruiter home menu
            recruiter_profile: RecruiterProfile = user_profile.recruiter_ref
            assert recruiter_profile is not None
            
            await state.set_state(MenuStates.recruiter_home)
            await message.answer(f"Successfully entered your recruiter profile, {user_profile.first_name}\n" 
                "Select an action from the menu below", 
                reply_markup=recruiter_profile.recruiter_markup.get_current_markup())

    elif message.text == user_markup.get_button_text("edit_profile_button"):
        # TODO: do profile editing logic
        await message.answer("NOIMPL", reply_markup=user_markup.get_current_markup())


@profile_router.message(F.text, SeekerRegistrationStates.position)
async def ask_experience_title(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer(f"OK, now we proceed with your working experience.\n\n"
                         f"Enter your experience title {Italic('For instance: Developer at ABC Inc.').as_html()} "
                         f"if you have one or press the button below.",
                         parse_mode="HTML", reply_markup=NoExperienceInlineKeyboardMarkup().get_current_markup())
    await state.set_state(SeekerRegistrationStates.experience_title)



@profile_router.callback_query(F.data == "no-exp", SeekerRegistrationStates.experience_title)
async def no_prior_experience(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    portfolio = {"position": data["position"], "experiences": []}

    user_profile: UserProfile = sweet_home.request_user_profile(call.from_user.id)
    sweet_home.profile_home.add_seeker_profile(user_profile, portfolio)

    await call.message.answer(f"{Bold('You have successfully registered a seeker profile.').as_html()}\n\n"
                              f"{Bold('— Name:').as_html()} {user_profile.get_full_name()}\n"
                              f"{Bold('— Desired position:').as_html()} {data['position']}\n\n" +
                              Italic("You may now access seeker menu!").as_html(),
                              parse_mode="HTML",
                              reply_markup=user_profile.user_markup.get_current_markup())
    await call.message.delete()
    await state.set_state(state=None)


@profile_router.message(F.text, SeekerRegistrationStates.experience_title)
async def add_experience_title(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get("experiences") is None:
        await state.update_data(experiences=[{"title": message.text}])
    else:
        data["experiences"].append({"title": message.text})
        # await state.update_data(experiences=data["experiences"])
    logging.info(f"Current portfolio: {data.get('experiences')}")
    await message.answer("Noted! Now, enter the description of your previous experience.")
    await state.set_state(SeekerRegistrationStates.experience_desc)


@profile_router.message(F.text, SeekerRegistrationStates.experience_desc)
async def add_experience_desc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    logging.info(f"Current portfolio: {data.get('experiences')}")
    experiences = data.get("experiences")
    exp_idx = len(experiences) - 1
    experiences[exp_idx].update({"desc": message.text})
    await state.update_data(experiences=experiences)
    await message.answer("Good one! Now enter a time frame you have had this experience at.")
    await state.set_state(SeekerRegistrationStates.experience_timeline)


@profile_router.message(F.text, SeekerRegistrationStates.experience_timeline)
async def add_experience_timeline(message: types.Message, state: FSMContext):
    data = await state.get_data()
    experiences = data.get("experiences")
    exp_idx = len(experiences) - 1
    experiences[exp_idx].update({"timeline": message.text})
    await state.update_data(experiences=experiences)
    experiences_text = ""
    for exp in experiences:
        experiences_text += (f"{Bold('— Title: ').as_html()} {exp['title']}\n"
                             f"{Bold('— Description: ').as_html()} {exp['desc']}\n"
                             f"{Bold('— Duration: ').as_html()} {exp['timeline']}\n\n")
    await message.answer(f"{Bold('Your current experiences: ').as_html()}\n\n{experiences_text}"
                         f"Please choose an option and press a button below.",
                         parse_mode='HTML', reply_markup=PortfolioAdditionInlineKeyboardMarkup().get_current_markup())
    await state.set_state(SeekerRegistrationStates.confirm_or_add_portfolio)


@profile_router.callback_query(F.data == "conf-exp", SeekerRegistrationStates.confirm_or_add_portfolio)
async def confirm_portfolio(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_profile: UserProfile = sweet_home.request_user_profile(call.from_user.id)
    portfolio = {"position": data.get("position"), "experiences": data.get("experiences")}
    sweet_home.profile_home.add_seeker_profile(user_profile, portfolio)
    experiences_text = ""
    for exp in data.get("experiences"):
        experiences_text += (f"{Bold('— Title: ').as_html()} {exp['title']}\n"
                             f"{Bold('— Description: ').as_html()} {exp['desc']}\n"
                             f"{Bold('— Duration').as_html()} {exp['timeline']}\n\n")
    await call.message.answer(f"{Bold('You have successfully registered a seeker profile.').as_html()}\n\n"
                              f"{Bold('— Name:').as_html()} {user_profile.get_full_name()}\n"
                              f"{Bold('— Desired position:').as_html()} {data['position']}\n\n" 
                              f"{Bold('— Portfolio: ').as_html()}\n\n{experiences_text}" +
                              Italic("You may now access seeker menu!").as_html(),
                              parse_mode="HTML",
                              reply_markup=user_profile.user_markup.get_current_markup())
    await call.message.delete()
    await state.set_data({})
    await state.set_state(state=MenuStates.profile_home)


@profile_router.callback_query(F.data == "add-exp", SeekerRegistrationStates.confirm_or_add_portfolio)
async def add_more_experience(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(f"Let's add another experience!\n\n"
                         f"Enter your experience title {Italic('For instance: Developer at ABC Inc.').as_html()}",
                         parse_mode="HTML")
    logging.info(f"Current portfolio: {(await state.get_data()).get('experiences')}")
    await state.set_state(SeekerRegistrationStates.experience_title)


@profile_router.message(F.text, RecruiterRegistrationStates.enter_company)
async def search_for_company(message: types.Message, state: FSMContext):
    result = sweet_home.profile_home.search_company_by_name(message.text)
    await state.update_data(company_name=message.text.strip())
    if result is None:
        await message.answer(f"Hmmm, we didn't find your company in registered ones. "
                             f"Would you like to register company with name {message.text.strip()} or try another name?",
                             reply_markup=SearchOrRegisterInlineKeyboardMarkup().get_current_markup())
        await state.set_state(RecruiterRegistrationStates.register_or_retry)
        return

    keyboard = CompaniesChoiceInlineKeyboardMarkup(result)
    await state.update_data(keyboard=keyboard)
    await message.answer("Select the company from the list below or register a new one.",
                         reply_markup=keyboard.get_current_markup())
    await state.set_state(RecruiterRegistrationStates.choose_company)


@profile_router.callback_query(F.data == SearchOrRegisterInlineKeyboardMarkup().get_button_data("retry_button"),
                               RecruiterRegistrationStates.register_or_retry)
async def retry_search(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("OK, let's try again: Enter the name of your company and we will search for it.")
    await state.set_state(RecruiterRegistrationStates.enter_company)


@profile_router.callback_query(F.data == SearchOrRegisterInlineKeyboardMarkup().get_button_data("register_button"),
                               RecruiterRegistrationStates.register_or_retry)
async def register_company(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        data.pop("keyboard")
    except KeyError:
        pass

    await call.message.edit_text(f"Awesome, let's register company '{data.get('company_name')}'.\n"
                                 f"Enter how many employees it currently has.")
    await state.set_state(RecruiterRegistrationStates.register_company)


@profile_router.message(F.text.regexp(r'^[1-9]\d*$'), RecruiterRegistrationStates.register_company)
async def finalize_seeker_registration(message: types.Message, state: FSMContext):
    data = await state.get_data()
    employees_count = int(message.text)
    user_profile = sweet_home.request_user_profile(message.from_user.id)
    company_ref = sweet_home.profile_home.add_company(data["company_name"], employees_count)
    sweet_home.profile_home.add_recruiter_profile(user_profile, company_ref.get_id())
    await message.answer("Your recruiter profile was successfully registered, with the following company association:\n\n"
                         f"{Bold('— Company name:').as_html()} {company_ref.name}\n"
                         f"{Bold('— Employees count:').as_html()} {company_ref.metrics.num_employees}\n\n"
                         f"{Italic('You may now access the recruiter profile!').as_html()}",
                         parse_mode='HTML', reply_markup=user_profile.user_markup.get_current_markup())
    await state.set_data({})
    await state.set_state(MenuStates.profile_home)


@profile_router.callback_query(RecruiterRegistrationStates.choose_company)
async def handle_company_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard: CompaniesChoiceInlineKeyboardMarkup = data.get("keyboard")
    if call.data == keyboard.get_button_data("previous_button"):
        keyboard.flip_page(is_next=False)
    elif call.data == keyboard.get_button_data("next_button"):
        keyboard.flip_page(is_next=True)
    elif call.data == SearchOrRegisterInlineKeyboardMarkup().get_button_data("register_button"):
        await register_company(call, state)
        return
    elif call.data.isdigit():
        chosen_company: Company = keyboard.get_companies()[int(call.data)]
        company_metrics = sweet_home.profile_home.get_company_metrics(chosen_company.get_id())
        user_profile: UserProfile = sweet_home.request_user_profile(call.from_user.id)
        sweet_home.profile_home.add_recruiter_profile(user_profile, chosen_company.get_id())
        await call.message.answer(f"You chose company {chosen_company.name} with following stats:\n\n"
                                     f"{Bold('— Employees count:').as_html()} {company_metrics.get('employees')}\n"
                                     f"{Bold('— Open vacancies:').as_html()} {company_metrics.get('open_vacancies')}\n\n"
                                     f"{Italic('You may now access recruiter menu!').as_html()}",
                                     parse_mode='HTML', reply_markup=user_profile.user_markup.get_current_markup())
        await call.message.delete()
        await state.set_state(MenuStates.profile_home)
        return

    await call.message.edit_reply_markup(call.inline_message_id, reply_markup=keyboard.get_current_markup())