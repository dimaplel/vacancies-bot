import logging

from typing import Optional
from aiogram.types import Message
from aiogram.utils.formatting import Italic, Bold
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router

from states.profile_states import ProfileStates
from config import cfg
from databases.psql_connection import PsqlConnection
from databases.redis_connection import RedisConnection
from databases.mongodb_connection import MongoDBConnection
from databases.neo4j_connection import Neo4jConnection
from keyboards.creation_menu_keyboard import CreationMenuKeyboard

from users.user_profile import UserProfile
from users.seeker_profile import SeekerProfile
from users.recruiter_profile import RecruiterProfile


class SweetHome:
    def __init__(self) -> None:
        self._cfg = cfg
        self._sql_connection = PsqlConnection(
            cfg.postgres_host,
            cfg.postgres_db,
            cfg.postgres_user,
            cfg.postgres_password.get_secret_value()
        )
        self._redis_connection = RedisConnection(
            cfg.redis_host,
            cfg.redis_username,
            cfg.redis_password.get_secret_value()
        )
        self._mongodb_connection = MongoDBConnection(
            cfg.mongo_host,
            cfg.mongo_initdb_root_username,
            cfg.mongo_initdb_root_password.get_secret_value(),
            cfg.mongo_dbname
        )
        self._neo4j_connection = Neo4jConnection(
            cfg.neo4j_host,
            cfg.neo4j_user,
            cfg.neo4j_password.get_secret_value()
        )

        try:
            logging.info("Opening databases connections")
            self._sql_connection.open()
            self._mongodb_connection.open()
            self._redis_connection.open()
            self._neo4j_connection.open()
            self._sql_db_init()
        except Exception as e:
            return


    def request_user_profile(self, user_id: int) -> Optional[UserProfile]:
        queryResult = self._sql_connection.execute_query(f"SELECT * FROM user_profiles WHERE user_id = {user_id}")
        if queryResult is None:
            return None

        first_name = queryResult['first_name']
        last_name = queryResult['last_name']
        seeker_profile = self.request_seeker_profile(user_id)
        recruiter_profile = self.request_recruiter_profile(user_id)
        userProfile = UserProfile(user_id, first_name, last_name, seeker_profile, recruiter_profile)
        return userProfile


    def request_seeker_profile(self, user_id: int) -> Optional[SeekerProfile]:
        queryResult = self._sql_connection.execute_query(f"SELECT * FROM seeker_profiles WHERE user_id = {user_id}")
        if queryResult is None:
            return None

        portfolio_ref = queryResult['portfolio_ref']
        seeker_node_ref = queryResult['seeker_node_ref']
        seeker_profile = SeekerProfile(user_id, portfolio_ref, seeker_node_ref)
        return seeker_profile


    def request_recruiter_profile(self, user_id: int) -> Optional[RecruiterProfile]:
        queryResult = self._sql_connection.execute_query(f"SELECT * FROM recruiter_profiles WHERE user_id = {user_id}")
        if queryResult is None:
            return None

        company_id: int = int(queryResult['company_id'])
        recruiter_node_ref = queryResult['recruiter_node_ref']
        recruiter_profile = RecruiterProfile(user_id, recruiter_node_ref, company_id)
        return recruiter_profile
        
        
    def _sql_db_init(self):
        self._sql_connection.execute_query(f"""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id BIGINT PRIMARY KEY, 
                first_name VARCHAR(255), 
                last_name VARCHAR(255))""")

        self._sql_connection.execute_query(f"""
            CREATE TABLE IF NOT EXISTS seeker_profiles (
                user_id BIGINT PRIMARY KEY, 
                portfolio_ref VARCHAR(255) NOT NULL, 
                seeker_node_ref BIGINT NOT NULL)""")
            
        self._sql_connection.execute_query(f"""
            CREATE TABLE IF NOT EXISTS recruiter_profiles (
                user_id BIGINT PRIMARY KEY, 
                recruiter_node_ref BIGINT, 
                company_id INT,
                FOREIGN KEY (company_id) REFERENCES companies(company_id))""")

        self._sql_connection.execute_query(f"""
            CREATE TABLE IF NOT EXISTS vacancies (
                recruiter_id BIGINT, 
                vacancy_doc_ref VARCHAR(255))""")

        self._sql_connection.execute_query(f"""
            CREATE TABLE IF NOT EXISTS companies (
                company_id SERIAL PRIMARY KEY, 
                name VARCHAR(255), 
                website VARCHAR(255))""")


entry_router = Router()
menu = SweetHome()


@entry_router.message(CommandStart())
async def entry_handler(message: Message, state: FSMContext) -> None:
    if menu.request_user_profile(message.from_user.id) is not None:
        # TODO: implement menu for existing user
        return
        # kb: ReplyKeyboardBuilder = CreationMenuKeyboard()
        # await message.answer("Welcome back! Choose from one of the options below.", reply_markup=kb)
    await message.answer("Welcome to the Vacancies Bot 👨‍💻\n\n"
                         f"For registration purposes, enter your {Italic("first name")}.")
    await state.set_state(ProfileStates.first_name)



@entry_router.message(ProfileStates.first_name)
async def enter_first_name(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text)
    await message.answer(f"Nice to meet you, {message.text}! You have a lovely first name!\n\n"
                         f"Now, please provide me with your {Italic("last name")}.")
    await state.set_state(ProfileStates.last_name)


@entry_router.message(ProfileStates.last_name)
async def enter_last_name(message: Message, state: FSMContext) -> None:
    await state.update_data(last_name=message.text)
    data = await state.get_data()
    up = UserProfile(message.from_user.id, data["first_name"], data["last_name"])
    # TODO: add up to the hash map and to the sql db
    await message.answer("Your profile has been successfully registered! Choose from one of the options below.")
    # TODO: make buttons for searching and publishing
