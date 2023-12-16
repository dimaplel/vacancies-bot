import logging

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Italic, Bold

from sweet_home import sweet_home
from users.user_profile import UserProfile
from keyboards.inline_keyboards import (no_experience_keyboard,
                                        portfolio_addition_keyboard,
                                        search_or_register_keyboard,
                                        companies_choice_keyboard)
from states.registration_states import EntryRegistrationStates, SeekerRegistrationStates, RecruiterRegistrationStates


# profile_markup = UserProfileKeyboardMarkup()
# register_profiles_keyboard = profile_markup.get_current_markup()
# register_profile_buttons = [button.text for row in register_profiles_keyboard.keyboard for button in row]
# profile_markup.set_type(UserProfileKeyboardTypes.SEEKER)
# seeker_access_keyboard = profile_markup.get_current_markup()
# profile_markup.set_type(UserProfileKeyboardTypes.RECRUITER)
# recruiter_access_keyboard = profile_markup.get_current_markup()
# profile_markup.set_type(UserProfileKeyboardTypes.FULL)
# full_access_keyboard = profile_markup.get_current_markup()


profile_router = Router(name="Profile Router")


# Handle options from profile menu
@profile_router.message(EntryRegistrationStates.options_handle)
async def register_seeker(message: types.Message, state: FSMContext):
    user_profile: UserProfile = sweet_home.request_user_profile(message.from_user.id)
    user_markup = user_profile.user_markup
    if message.text == user_markup.get_button_text("seeker_button"):
        if not user_profile.has_seeker_profile() and not sweet_home.profile_home.request_seeker_profile(user_profile):
            # Do seeker profile registration
            await message.answer("To become a seeker, you will need to make a portfolio.\n\n"
                                "Enter the position you would like to apply for.",
                                reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
            await state.set_state(SeekerRegistrationStates.position)
        else:
            # TODO: Implement logic for existing seeker profile
            pass

    elif message.text == user_markup.get_button_text("recruiter_button"):
        if not user_profile.has_recruiter_profile() and not sweet_home.profile_home.request_recruiter_profile(user_profile): 
            # Do recruiter profile registration
            await message.answer("To become a recruiter, you should choose/create a company you're hiring for.\n\n"
                                "Enter the name of your company and we will search for it.",
                                reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
            await state.set_state(RecruiterRegistrationStates.enter_company)

        else:
            # TODO: Implement logic for existing recruiter profile
            pass

    elif message.text == user_markup.get_button_text("edit_profile_button"):
        # Do profile editing logic
        pass


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
                         parse_mode='HTML', reply_markup=portfolio_addition_keyboard())
    await state.set_state(SeekerRegistrationStates.confirm_or_add_portfolio)


@profile_router.callback_query(F.data == "conf-exp", SeekerRegistrationStates.confirm_or_add_portfolio)
async def confirm_portfolio(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_profile: UserProfile = data["profile"]
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
    await state.set_state(state=EntryRegistrationStates.options_handle)


@profile_router.callback_query(F.data == "add-exp", SeekerRegistrationStates.confirm_or_add_portfolio)
async def add_more_experience(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(f"Let's add another experience!\n\n"
                         f"Enter your experience title {Italic('For instance: Developer at ABC Inc.').as_html()}",
                         parse_mode="HTML")
    logging.info(f"Current portfolio: {(await state.get_data()).get('experiences')}")
    await state.set_state(SeekerRegistrationStates.experience_title)


@profile_router.message(F.text, RecruiterRegistrationStates.enter_company)
async def search_for_company(message: types.Message, state: FSMContext):
    result = sweet_home.search_company_by_name(message.text)
    await state.update_data(company_name=message.text)
    if result is None:
        await message.answer("Hmmm, we didn't find your company in registered ones. "
                             "Would you like to register your company or try another name?",
                             reply_markup=search_or_register_keyboard())
        await state.set_state(RecruiterRegistrationStates.register_or_retry)
        return

    if len(result) > 5:
        await state.update_data(page=0)

    await state.update_data(companies=result)
    await message.answer("Select the company from the list below or register a new one.",
                         reply_markup=companies_choice_keyboard(result, page=0))
    await state.set_state(RecruiterRegistrationStates.enter_company)


@profile_router.callback_query(F.data == "search-again", RecruiterRegistrationStates.register_or_retry)
async def retry_search(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("OK, let's try again: Enter the name of your company and we will search for it.")
    await state.set_state(RecruiterRegistrationStates.enter_company)
