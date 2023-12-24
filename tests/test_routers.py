import unittest
import unittest.mock as mock
from unittest.mock import AsyncMock, Mock
from typing import Any, Dict

from aiogram.types import Message, User

from src.routers.entry_router import entry_handler, enter_first_name, enter_last_name
from src.states.menu_states import MenuStates
from src.states.registration_states import EntryRegistrationStates
from src.users.user_profile import UserProfile


def create_mock_message(text, user_id=1234, chat_type='private'):
    # Create a mock data
    user = mock.AsyncMock(spec=User)
    user.id = user_id
    user.username = 'testuser'

    message = mock.AsyncMock(spec=Message)
    message.answer = AsyncMock()
    message.from_user = user
    message.text = text
    return message


class FSMContextMock:
    def __init__(self):
        self.mock = AsyncMock()
        self.state = None
        self.data = {}

        # Set up mock methods
        self.mock.set_state = AsyncMock(side_effect=self.set_state)
        self.mock.get_state= AsyncMock(side_effect=self.get_state)
        self.mock.set_data = AsyncMock(side_effect=self.set_data)
        self.mock.get_data = AsyncMock(side_effect=self.get_data)
        self.mock.update_data = AsyncMock(side_effect=self.update_data)


    async def set_state(self, state):
        self.state = state


    async def get_state(self):
        return self.state


    async def set_data(self, data):
        self.data = data


    async def update_data(self, data: Dict[str, Any] | None = None, **kwargs: Any):
        if data:
            self.data.update(data)
        if kwargs:
            self.data.update(kwargs)
        return self.data


    async def get_data(self):
        return self.data


class SweetBotTest(unittest.IsolatedAsyncioTestCase):
    
    @mock.patch('src.sweet_home.sweet_home.request_user_profile', Mock(return_value=None))
    async def test_start_bot_new_user(self):
        # Create a mock message with CommandStart
        mock_message = create_mock_message("/start", user_id=1234)
        mock_state = FSMContextMock()

        # Run the entry handler
        await entry_handler(mock_message, mock_state.mock)
        
        mock_state.mock.set_state.assert_awaited_once_with(EntryRegistrationStates.first_name)
        self.assertEqual(await mock_state.get_state(), EntryRegistrationStates.first_name)


    @mock.patch('src.sweet_home.sweet_home.request_user_profile', Mock(return_value=UserProfile(1234, "John", "Doe")))
    async def test_start_bot_existing_user(self):
        # Create a mock message with CommandStart
        mock_message = create_mock_message("/start")
        mock_state = FSMContextMock()

        # Run the entry handler
        await entry_handler(mock_message, mock_state.mock)
        
        # Assert we skipped registration successfully
        mock_state.mock.set_state.assert_awaited_once_with(MenuStates.profile_home)
        self.assertEqual(await mock_state.get_state(), MenuStates.profile_home)


    async def test_enter_first_name(self):
        # Create a mock message containing the first name
        mock_message = create_mock_message("John")
        mock_state = FSMContextMock()
        await enter_first_name(mock_message, mock_state.mock)

        mock_state.mock.update_data.assert_awaited_once_with(first_name="John")
        mock_state.mock.set_state.assert_awaited_once_with(EntryRegistrationStates.last_name)


    @mock.patch('src.sweet_home.sweet_home.add_user_profile')
    async def test_enter_last_name(self, mock_add_user_profile):
        mock_message = create_mock_message("Doe", user_id=1234)
        
        mock_state = FSMContextMock()
        await mock_state.set_data({"first_name": "John"})
        await enter_last_name(mock_message, mock_state.mock)

        # Assert that add_user_profile was called
        mock_add_user_profile.assert_called_once()
        mock_state.mock.set_state.assert_awaited_once_with(MenuStates.profile_home)

        data = await mock_state.get_data()
        expected = UserProfile(1234, "John", "Doe")
        self.assertEqual(data['profile'], expected)