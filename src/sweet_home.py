import logging

from aiogram.types import Message
from aiogram.utils.formatting import Italic, Text, Bold
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router

from states.profile_states import ProfileStates
from config import cfg
from databases.psql_connection import PsqlConnection
from databases.redis_connection import RedisConnection
from databases.mongodb_connection import MongoDBConnection
from databases.neo4j_connection import Neo4jConnection
from keyboards.function_choice_keyboard import function_choice_keyboard

from users.user_profile import UserProfile


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
        self._user_cache = {}

        try:
            logging.info("Opening databases connections")
            self._sql_connection.open()
            self._mongodb_connection.open()
            self._redis_connection.open()
            self._neo4j_connection.open()
            self._sql_db_init()
        except Exception as e:
            return


    def request_user_profile(self, user_id: int) -> (UserProfile | None):
        # Avoid querying sql connection everytime using cached values
        # cached values must ensure they are always up-to-date with sql connection and vice versa
        userProfile: (UserProfile | None) = self._user_cache.get(user_id)
        if userProfile is not None:
            return userProfile

        queryResult = self._sql_connection.execute_query(f"SELECT * FROM user_profiles WHERE user_id = {user_id}")
        if queryResult is None:
            return None

        # We should always assume there is only 1 result for any user_id we provided
        assert len(queryResult) == 1
        row = queryResult[0]
        first_name = row['first_name']
        last_name = row['last_name']
        # We do not specify seeker_profile and recruiter_profile here. Those will be set explicitly
        userProfile = UserProfile(user_id, first_name, last_name) 
        
        if not userProfile.request_seeker_profile(self._sql_connection):
            logging.info("Could not set a seeker profile for user with id %d", user_id)
            logging.info("Registration of the seeker profile will be required")


        if not userProfile.request_recruiter_profile(self._sql_connection):
            logging.info("Could not set a recruiter profile for user with id %d", user_id)
            logging.info("Registration of the recruiter profile will be required")


        # Cache user profile value in map
        self._user_cache[user_id] = userProfile
        return userProfile


    def add_user_profile(self, userProfile: UserProfile):
        assert self.request_user_profile(userProfile.get_id()) is None
        user_id = userProfile.get_id()
        self._user_cache[user_id] = userProfile
        self._sql_connection.execute_query(f"INSERT INTO user_profiles (user_id, first_name, last_name) "
                                           f"VALUES (%s, %s, %s)",
                                           user_id, userProfile.first_name, userProfile.last_name)


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
    user_id = message.from_user.id
    if menu.request_user_profile(user_id) is not None:
        # TODO: implement menu for existing user
        return
        # kb: ReplyKeyboardBuilder = CreationMenuKeyboard()
        # await message.answer("Welcome back! Choose from one of the options below.", reply_markup=kb)
    
    await message.answer(f"Welcome to the Vacancies Bot 👨‍💻\n\n"
                         f"For registration purposes, enter your {Italic('first name').as_html()}.", parse_mode="HTML")
    await state.set_state(ProfileStates.first_name)



@entry_router.message(ProfileStates.first_name)
async def enter_first_name(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text)
    await message.answer(f"Nice to meet you, {message.text}! You have a lovely first name!\n\n"
                       f"Now, please provide me with your {Italic('last name').as_html()}.", parse_mode="HTML")
    await state.set_state(ProfileStates.last_name)


@entry_router.message(ProfileStates.last_name)
async def enter_last_name(message: Message, state: FSMContext) -> None:
    await state.update_data(last_name=message.text)
    data = await state.get_data()
    userProfile = UserProfile(message.from_user.id, data["first_name"], data["last_name"])
    menu.add_user_profile(userProfile=userProfile)
    await message.answer("Your profile has been successfully registered! Choose from one of the options below.",
                         reply_markup=function_choice_keyboard())
    # TODO: make buttons for searching and publishing
