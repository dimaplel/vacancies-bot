import logging

from aiogram import Router, F, types
from aiogram.methods.get_chat_member import GetChatMember
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Italic, Bold

from src.states.menu_states import MenuStates, RecruiterMenuStates
from src.users.company import Company
from src.users.user_profile import UserProfile
from src.users.recruiter_profile import RecruiterProfile
from src.sweet_home import sweet_home
from src.bot import bot
from src.keyboards.recruiter_inline_keyboards import (ConfirmOrChangeDescriptionInlineKeyboardMarkup,
                                                      KeepThePreviousDescriptionInlineKeyboardMarkup,
                                                      VacancyDisplayInlineKeyboardMarkup,
                                                      DeleteVacancyOrGoBackInlineKeyboardMarkup,
                                                      ApplicantsListDisplayInlineKeyboard,
                                                      GoBackInlineKeyboardMarkup)


recruiter_router = Router(name="Recruiter Router")


@recruiter_router.message(F.text, MenuStates.recruiter_home)
async def recruiter_home(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    
    recruiter_profile: RecruiterProfile = user_profile.recruiter_ref
    assert recruiter_profile is not None

    recruiter_markup = recruiter_profile.recruiter_markup
    if message.text == recruiter_markup.get_button_text("add_vacancy_button"):
        company: Company = sweet_home.recruiter_home.get_company(recruiter_profile)
        await message.answer(f"We will now create a vacancy for your company ({Italic(company.name).as_html()}).\n\n"
                             f"First of all, enter vacancy position name.", parse_mode='HTML')

        await state.set_data({"vacancy_ref": {"company": company,
                                              "position": None, "description": None, "salary": None}})
        await state.set_state(RecruiterMenuStates.vacancy_position)

    elif message.text == recruiter_markup.get_button_text("your_vacancies_button"):
        vacancies = sweet_home.recruiter_home.get_vacancies_data(recruiter_profile)
        if len(vacancies) == 0:
            await message.answer("You have no vacancies yet. You can create one in the recruiter menu.",
                                 reply_markup=recruiter_markup.get_current_markup())
            return

        await state.set_data({"vacancies": vacancies})

        vacancies_text = ""
        for i, vacancy in enumerate(vacancies, start=1):
            vacancies_text += f"{i}) {Italic(vacancy[1]['position']).as_html()}\n"

        await message.answer(f"{Bold('Your vacancies:').as_html()}\n\n"
                             f"{vacancies_text}\n"
                             f"Choose vacancy to display by typing its index.\n", parse_mode='HTML', 
                             reply_markup=GoBackInlineKeyboardMarkup().get_current_markup())
        await state.set_state(RecruiterMenuStates.choose_vacancy)

    elif message.text == recruiter_markup.get_button_text("back_button"):
        await message.answer("Returning back to user profile menu.",
                             reply_markup=user_profile.user_markup.get_current_markup())
        await state.set_state(MenuStates.profile_home)


@recruiter_router.callback_query(F.data == "back", RecruiterMenuStates.choose_vacancy)
async def back_to_menu(call: types.CallbackQuery, state: FSMContext):
    await state.set_data({})
    user_id = call.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    recruiter_profile: RecruiterProfile = user_profile.recruiter_ref

    await call.message.answer("You went back to recruiter menu.",
                              reply_markup=recruiter_profile.recruiter_markup.get_current_markup())
    await call.message.delete()

    await state.set_state(MenuStates.recruiter_home)


@recruiter_router.message(F.text.regexp(r'^([1-9]\d*)$'), RecruiterMenuStates.choose_vacancy)
async def vacancy_display(message: types.Message, state: FSMContext):
    data = await state.get_data()
    vacancies = data["vacancies"]

    chosen_vacancy = vacancies[int(message.text) - 1]
    chosen_vacancy_data = chosen_vacancy[1]
    await state.update_data(chosen_vacancy=chosen_vacancy)

    await message.answer(f"{Bold('Vacancy ' + chosen_vacancy_data['position']).as_html()}\n\n"
                         f"{chosen_vacancy_data['description']}\n\n"
                         f"{Italic('Salary: ').as_html() + str(chosen_vacancy_data['salary'])}\n\n"
                         f"Choose an action.", parse_mode='HTML',
                         reply_markup=VacancyDisplayInlineKeyboardMarkup().get_current_markup())
    await state.set_state(RecruiterMenuStates.manage_vacancy)


@recruiter_router.callback_query(F.data == "back", RecruiterMenuStates.manage_vacancy)
async def back_to_vacancies(call:types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    vacancies = data["vacancies"]
    try:
        data.pop("chosen_vacancy")
    except KeyError:
        pass

    vacancies_text = ""
    for i, vacancy in enumerate(vacancies, start=1):
        vacancies_text += f"{i}) {Italic(vacancy[1]['position']).as_html()}\n"

    await call.message.answer(f"{Bold('Your vacancies:').as_html()}\n\n"
                         f"{vacancies_text}\n"
                         f"Choose vacancy to display by typing its index.", parse_mode='HTML')
    await call.message.delete()

    await state.set_state(RecruiterMenuStates.choose_vacancy)


@recruiter_router.callback_query(F.data == "delete", RecruiterMenuStates.manage_vacancy)
async def vacancy_removal_confirmation(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("This action will forever remove this vacancy, are you sure about it?",
                              reply_markup=DeleteVacancyOrGoBackInlineKeyboardMarkup().get_current_markup())
    await state.set_state(RecruiterMenuStates.confirm_vacancy_removal)


@recruiter_router.callback_query(F.data == "back", RecruiterMenuStates.confirm_vacancy_removal)
async def back_to_vacancy_action(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chosen_vacancy = data["chosen_vacancy"]
    chosen_vacancy_data = chosen_vacancy[1]

    await call.message.answer(f"{Bold('Vacancy ' + chosen_vacancy_data['position']).as_html()}\n\n"
                         f"{chosen_vacancy_data['description']}\n\n"
                         f"{Italic('Salary: ').as_html() + str(chosen_vacancy_data['salary'])}\n\n"
                         f"Choose an action.", parse_mode='HTML',
                         reply_markup=VacancyDisplayInlineKeyboardMarkup().get_current_markup())
    await call.message.delete()
    await state.set_state(RecruiterMenuStates.manage_vacancy)


@recruiter_router.callback_query(F.data == "confirm", RecruiterMenuStates.confirm_vacancy_removal)
async def delete_vacancy(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    recruiter_profile: RecruiterProfile = user_profile.recruiter_ref

    data = await state.get_data()
    chosen_vacancy = data["chosen_vacancy"]
    sweet_home.recruiter_home.delete_vacancy(recruiter_profile, chosen_vacancy)

    await call.message.answer(f"Your vacancy for '{chosen_vacancy[1]['position']}' was permanently deleted!",
                              reply_markup=recruiter_profile.recruiter_markup.get_current_markup())

    await call.message.delete()
    await state.set_data({})
    await state.set_state(MenuStates.recruiter_home)


@recruiter_router.callback_query(F.data == "applicants", RecruiterMenuStates.manage_vacancy)
async def display_applicants(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    recruiter_profile = user_profile.recruiter_ref

    data = await state.get_data()
    chosen_vacancy = data["chosen_vacancy"]

    applicants_id_list = sweet_home.recruiter_home.get_vacancy_applicants(recruiter_profile, chosen_vacancy[0])
    user_profiles_list = [sweet_home.request_user_profile(uid) for uid in applicants_id_list
                          if sweet_home.request_user_profile(uid) is not None]
    if len(applicants_id_list) == 0:
        await call.message.answer("This vacancy has no applicants, you were returned to recruiter menu.",
                                  reply_markup=recruiter_profile.recruiter_markup.get_current_markup())
        await call.message.delete()
        await state.set_data({})
        await state.set_state(MenuStates.recruiter_home)
        return

    logging.info(f"Retrieved applicants with ids: {applicants_id_list}")

    if len(user_profiles_list) == 0:
        await call.message.answer("Applicants don't have a valid seeker profile and cannot be viewed properly, "
                                  "you were returned to recruiter menu.",
                                  reply_markup=recruiter_profile.recruiter_markup.get_current_markup())
        await call.message.delete()
        await state.set_data({})
        await state.set_state(MenuStates.recruiter_home)
        return

    current_applicant_profile = user_profiles_list[0]
    current_portfolio = sweet_home.seeker_home.request_seeker_portfolio(current_applicant_profile.seeker_ref)
    logging.info(f"Retrieved portfolio for user with id {current_applicant_profile.get_id()}: {current_portfolio}")

    telegram_profile = await GetChatMember(chat_id=current_applicant_profile.get_id(),
                                     user_id=current_applicant_profile.get_id()).as_(bot)
    keyboard = ApplicantsListDisplayInlineKeyboard(len(user_profiles_list))
    await state.update_data(applicant_profiles=user_profiles_list, keyboard=keyboard)

    portfolio_text = ""
    for exp in current_portfolio.get("experiences"):
        portfolio_text += (f"{Bold('— Title: ').as_html()} {exp['title']}\n"
                           f"{Bold('— Description: ').as_html()} {exp['desc']}\n"
                           f"{Bold('— Duration').as_html()} {exp['timeline']}\n\n")

    await call.message.answer(f"{telegram_profile.user.mention_html(current_applicant_profile.get_full_name())}\n\n"
                              f"Main position: {current_portfolio.get('position')}\n"
                              f"Past experiences:\n\n"
                              f"{portfolio_text}", parse_mode='HTML',
                              reply_markup=keyboard.get_current_markup())
    await call.message.delete()
    await state.set_state(RecruiterMenuStates.applicants_displaying)


@recruiter_router.callback_query(F.data.in_({'next', 'back'}), RecruiterMenuStates.applicants_displaying)
async def previous_applicant(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard: ApplicantsListDisplayInlineKeyboard = data.get("keyboard")
    prev_keyboard = keyboard.get_current_markup()

    is_next = True if call.data == "next" else False
    keyboard.flip_page(is_next=is_next)
    current_applicant_index = keyboard.get_current_applicant()

    current_applicant_profile = data.get("applicant_profiles")[current_applicant_index]
    current_portfolio = sweet_home.seeker_home.request_seeker_portfolio(current_applicant_profile.seeker_ref)
    telegram_profile = await GetChatMember(chat_id=current_applicant_profile.get_id(),
                                           user_id=current_applicant_profile.get_id()).as_(bot)

    experiences = current_portfolio.get("experiences")
    if len(experiences) == 0:
        portfolio_text = "Has no prior experience."
    else:
        portfolio_text = "Past experiences:\n\n"
        for exp in experiences:
            portfolio_text += (f"{Bold('— Title: ').as_html()} {exp['title']}\n"
                               f"{Bold('— Description: ').as_html()} {exp['desc']}\n"
                               f"{Bold('— Duration').as_html()} {exp['timeline']}\n\n")

    if prev_keyboard == keyboard.get_current_markup():
        await call.message.edit_text(f"{telegram_profile.user.mention_html(current_applicant_profile.get_full_name())}\n\n"
                                  f"Main position: {current_portfolio.get('position')}\n"
                                  f"{portfolio_text}", parse_mode='HTML')
    else:
        await call.message.edit_text(
            f"{telegram_profile.user.mention_html(current_applicant_profile.get_full_name())}\n\n"
            f"Main position: {current_portfolio.get('position')}\n"
            f"{portfolio_text}", parse_mode='HTML',
            reply_markup=(keyboard.get_current_markup()))
    # await call.message.delete()


@recruiter_router.callback_query(F.data == "exit", RecruiterMenuStates.applicants_displaying)
async def exit_applicants_display(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)

    recruiter_profile: RecruiterProfile = user_profile.recruiter_ref

    await call.message.answer(f"You returned back to your recruiter menu.",
                              reply_markup=recruiter_profile.recruiter_markup.get_current_markup())
    await call.message.delete()

    await state.set_data({})
    await state.set_state(MenuStates.recruiter_home)


@recruiter_router.message(F.text, RecruiterMenuStates.vacancy_position)
async def handle_vacancy_position(message: types.Message, state: FSMContext):
    data = await state.get_data()
    vacancy: dict = data["vacancy_ref"]
    vacancy.update(position=message.text)

    await message.answer(f"Great, now enter a description for your '{message.text}' position.\n\n"
                         f"Note: it should include everything you want to mention, like responsibilities, "
                         f"requirements, benefits etc. except for the salary")

    await state.set_state(RecruiterMenuStates.vacancy_description)


@recruiter_router.message(F.text, RecruiterMenuStates.vacancy_description)
async def handle_vacancy_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    vacancy: dict = data["vacancy_ref"]
    vacancy.update(description=message.text)

    await message.answer(f"Your vacancy would look like this so far:\n\n"
                         f"{Bold(vacancy['position']).as_html()} at {vacancy['company'].name}\n\n"
                         f"{message.text}\n\n Are you satisfied with it or would you like to change the description?",
                         reply_markup=ConfirmOrChangeDescriptionInlineKeyboardMarkup().get_current_markup(),
                         parse_mode='HTML')
    await state.set_state(RecruiterMenuStates.confirm_or_retry_description)


@recruiter_router.callback_query(F.data == "retry", RecruiterMenuStates.confirm_or_retry_description)
async def retry_description(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    position = data["vacancy_ref"]["position"]
    await call.message.answer(f"OK, let's do this again. Enter a description for your '{position}' position.",
                              reply_markup=KeepThePreviousDescriptionInlineKeyboardMarkup().get_current_markup())

    await call.message.delete()
    await state.set_state(RecruiterMenuStates.vacancy_description)


@recruiter_router.callback_query(F.data == "back", RecruiterMenuStates.vacancy_description)
async def keep_previous_description(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    vacancy: dict = data["vacancy_ref"]

    await call.message.answer(f"Your vacancy would look like this so far:\n\n"
                         f"{Bold(vacancy['position']).as_html()} at {vacancy['company'].name}\n\n"
                         f"{vacancy['description']}\n\n"
                              f"Are you satisfied with it or would you like to change the description?",
                         reply_markup=ConfirmOrChangeDescriptionInlineKeyboardMarkup().get_current_markup(),
                         parse_mode='HTML')
    await call.message.delete()
    await state.set_state(RecruiterMenuStates.confirm_or_retry_description)


@recruiter_router.callback_query(F.data == "confirm", RecruiterMenuStates.confirm_or_retry_description)
async def confirm_description(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Perfect! Finally, write a salary for your vacancy.")
    await call.message.delete()
    await state.set_state(RecruiterMenuStates.vacancy_salary)


@recruiter_router.message(F.text.regexp(r'^\d+(\.\d+)?$'), RecruiterMenuStates.vacancy_salary)
async def handle_salary(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_profile: UserProfile = sweet_home.request_user_profile(user_id)
    recruiter_profile = user_profile.recruiter_ref

    data = await state.get_data()
    vacancy: dict = data['vacancy_ref']
    vacancy.update(salary=float(message.text), company=vacancy["company"].get_id())

    sweet_home.recruiter_home.add_vacancy(recruiter_profile, vacancy)

    await message.answer("Your vacancy has been added and can be searched by anyone now! "
                         "You can manage it in your vacancies menu.",
                         reply_markup=recruiter_profile.recruiter_markup.get_current_markup())
    await state.set_data({})
    await state.set_state(MenuStates.recruiter_home)