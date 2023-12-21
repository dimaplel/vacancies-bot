import logging

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Italic, Bold

from src.states.menu_states import MenuStates, RecruiterMenuStates
from src.users.company import Company
from src.users.user_profile import UserProfile
from src.users.recruiter_profile import RecruiterProfile
from src.sweet_home import sweet_home
from src.keyboards.recruiter_inline_keyboards import (ConfirmOrChangeDescriptionInlineKeyboardMarkup,
                                                      KeepThePreviousDescriptionInlineKeyboardMarkup)


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
        for i, vacancy in enumerate(vacancies):
            vacancies_text += f"{i}) {vacancy['position']}"

        await message.answer(f"Your vacancies:\n\n"
                             f"{vacancies_text}\n\n"
                             f"Choose vacancy to display by typing its index.")
        await state.set_state(RecruiterMenuStates.choose_vacancy)

    elif message.text == recruiter_markup.get_button_text("back_button"):
        await message.answer("Returning back to user profile menu", reply_markup=user_profile.user_markup.get_current_markup())
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


@recruiter_router.message(F.text.regexp(r'^[1-9]\d*$'), RecruiterMenuStates.choose_vacancy)
async def vacancy_display(message: types.Message, state: FSMContext):
    data = await state.get_data()
    vacancies = data["vacancies"]

    chosen_vacancy = vacancies[int(message.text)]
    await message.answer(f"{Bold('Vacancy ' + chosen_vacancy['position']).as_html()}\n\n"
                         f"{chosen_vacancy['description']}\n\n"
                         f"{Italic('Salary: ').as_html() + chosen_vacancy['salary']}\n\n"
                         f"Choose an action.", )


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