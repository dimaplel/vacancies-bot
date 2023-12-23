import re
import logging

from dataclasses import dataclass
from typing import Dict, Any, Tuple

from src.connections import MongoDBConnection, PsqlConnection
from src.keyboards.profile_keyboards import SeekerProfileKeyboardMarkup
from src.keyboards.seeker_inline_keyboards import SeekerVacancySearchingInlineKeyboardMarkup
from src.users.vacancy import VacanciesChunk, Vacancy


class VacanciesSearchContext:
        def __init__(self, chunk_limit: int, psql_connection: PsqlConnection, mongodb_connection: MongoDBConnection):
            self._sql_connection = psql_connection
            self._mongodb_connection = mongodb_connection

            self._chunk_limit = chunk_limit
            self._chunk_offset = 0

            self._curr_chunk = VacanciesChunk(chunk_limit, 0)
            self._curr_chunk.query_chunk(psql_connection)
            self._vacancy_idx = 0

            # We can immediately turn off the "prev_button" here, as there will be no vacancies
            self.inline_markup = SeekerVacancySearchingInlineKeyboardMarkup()
            self.inline_markup.toggle_button("prev_vacancy_button", False)

            # We should also check if there are any vacancies next to us
            self.empty_context = False
            if not self.has_next_vacancy():
                self.inline_markup.toggle_button("next_vacancy_button", False)
                self.empty_context = True

            self.inline_markup.update_keyboard()

        
        def is_current_vacancy_by_filters(self, salary: tuple[int, int], position_regex) -> bool:
            vacancy = self.get_current_vacancy()
            assert vacancy is not None
            data = vacancy.get_vacancy_data(self._mongodb_connection)
            # Shouldnt happen
            if data is None:
                logging.error(f"Data is none for vacancy {vacancy.get_id()}")
                return False

            data_salary = data['salary']
            data_position = data['position']

            is_suitable = True
            if salary is not None:
                min_salary, max_salary = salary
                if not (min_salary <= data_salary <= max_salary):
                    is_suitable = False

            if position_regex is not None and position_regex.search(data_position) is None:
                is_suitable = False

            return is_suitable


        def jump_next_vacancy_with_filters(self, salary, position) -> bool:
            return self.jump_vacancy_with_filters(1, salary, position)


        def jump_prev_vacancy_with_filters(self, salary, position) -> bool:
            return self.jump_vacancy_with_filters(-1, salary, position)


        def jump_vacancy_with_filters(self, step: int, salary: tuple[int, int], position: str) -> bool:
            # Escape special characters in the phrase and create a case-insensitive regex
            position_regex = None
            if position is not None:
                position_regex = re.compile(re.escape(position), re.IGNORECASE)
            
            while self.jump_vacancy(step):
                if self.is_current_vacancy_by_filters(salary, position_regex):
                    return True

            return False


        def has_next_vacancy(self) -> bool:
            """
            Returns True if there is any vacancy next to the current. 
            The method won't update any of it's internal state, but it might query the neighboring chunk
            of vacancies if needed

            Returns False otherwise
            """
            able, _ = self._has_neighbor_vacancy(1)
            return able


        def has_prev_vacancy(self) -> bool:
            """
            Same as self.has_next_vacancy
            """
            able, _ = self._has_neighbor_vacancy(-1)
            return able


        def _has_neighbor_vacancy(self, step: int) -> Tuple[bool, (VacanciesChunk | None)]:            
            """
            For internal use only
            Returns True if any vacancies in the specified direction (next if step > 0 or prev is step < 0)
            Returns False if no vacancies in whatever direction
            Also returns a queried chunk of vacancies, if the chunk needs update
            """
            if step == 0:
                return False, None

            if self._curr_chunk is None:
                self._curr_chunk = VacanciesChunk(self._chunk_limit, self._chunk_offset)
                self._curr_chunk.query_chunk(self._sql_connection)

            step = -1 if step < 0 else 1

            vacancy_idx = self._vacancy_idx + step
            # Cannot decrement if vacancy_idx is already 0
            if vacancy_idx < 0:
                return False, None

            idx_upper_bound = self._chunk_limit * (self._chunk_offset + 1)
            idx_lower_bound = self._chunk_limit * self._chunk_offset
            # If we are in the EXPECTED bounds of chunk we should check if there are enough vacancies
            if idx_lower_bound <= vacancy_idx < idx_upper_bound:
                # Perform checks once again to ensure we are not out of boundaries
                # We want to check if length of vacancies is larger than our new vacancy index
                vacancies = self._curr_chunk.get_current_chunk()
                local_idx = vacancy_idx % self._chunk_limit
                if local_idx >= len(vacancies):
                    # Cannot increment
                    return False, None
                
                return True, None
            else: # if ![idx_lower, idx_upper) we need to query a chunk
                chunk_offset = self._chunk_offset + step
                assert chunk_offset >= 0

                chunk = VacanciesChunk(self._chunk_limit, chunk_offset)
                vacancies = chunk.query_chunk(self._sql_connection)

                # We are at beginning of the chunk. Check if there are any vacancies at all.
                # If there are no vacancies - return False, as we cannot increment
                if len(vacancies) == 0:
                    # Cannot increment/decrement
                    # NOTICE: If vacancies were removed during DECREMENT search operation and the chunk
                    # is no longer valid - this will result in undefined state
                    return False, None

                return True, chunk
        

        def jump_next_vacancy(self) -> bool:
            """
            Returns False if cannot increment. No changes if cannot increment
            Otherwise increments the vacancy index and returns True
            """
            return self.jump_vacancy(1)

        
        def jump_prev_vacancy(self) -> bool:
            """
            Returns False if cannot decrement. No changes if cannot.
            Otherwise decrements and returns True.
            """
            return self.jump_vacancy(-1)

        
        def jump_vacancy(self, step: int) -> bool:
            """
            Returns False if cannot increment/decrement. No changes if cannot increment/decrement
            Otherwise increments/decrements (if 1 or -1 respectively) the vacancy index and returns True
            """
            if step == 0:
                return False

            step = -1 if step < 0 else 1
            able, chunk = self._has_neighbor_vacancy(step)
            if not able:
                return False

            self._vacancy_idx = self._vacancy_idx + step
            if chunk is not None:
                self._chunk_offset = self._chunk_offset + step
                self._curr_chunk = chunk

            self.inline_markup.toggle_button("prev_vacancy_button", self.has_prev_vacancy())
            self.inline_markup.toggle_button("next_vacancy_button", self.has_next_vacancy())
            self.inline_markup.update_keyboard()
            return True


        def get_current_vacancy(self) -> Vacancy:
            local_idx = self._vacancy_idx % self._chunk_limit
            vacancies = self._curr_chunk.get_current_chunk()
            # Out of range (somehow?)
            # if local_idx >= len(vacancies):
            #     return None
                
            return vacancies[local_idx]


        def get_current_vacancy_index(self) -> int:
            return self._vacancy_idx


@dataclass
class SeekerProfile:
    _user_id: int
    _portfolio_ref: str
    _seeker_node_ref: str
    seeker_markup = SeekerProfileKeyboardMarkup()
    vacancies_search_context: (VacanciesSearchContext | None) = None


    def get_id(self) -> int:
        return self._user_id


    # Queries mongodb connection for JSON document referenced by self._portfolio_ref
    # Returns the JSON document if any exists
    def get_portfolio(self, mongodb_connection: MongoDBConnection) -> (dict[str, Any] | None):
        doc = mongodb_connection.get_document("portfolios", self._portfolio_ref)
        return doc

    
    # Return True if portfolio was updated successfully, False otherwise. Keep debugging, bozo
    # Remark: update_portfolio will only update those fields that are already reside in document
    # Thus, adding new fields is not possible using this method
    # If there is no portfolio in mongodb's portfolios connection then there is no update as well
    def update_portfolio(self, mongodb_connection: MongoDBConnection, document: Dict[str, Any]) -> bool:
        existing_doc = self.get_portfolio(mongodb_connection)
        if existing_doc is None:
            return False

        # Filter the fields to update only existing fields
        filtered_doc: Dict[str, Any] = {key: value for key, value in document.items() if key in existing_doc}
        if not filtered_doc:
            return False

        # perform update
        return mongodb_connection.update_document("portfolios", self._portfolio_ref, filtered_doc)


    def add_search_context(self, psql_connection: PsqlConnection, mongodb_connection: MongoDBConnection):
        self.vacancies_search_context = VacanciesSearchContext( 
            chunk_limit=5, 
            psql_connection=psql_connection,
            mongodb_connection=mongodb_connection
        )
        return self.vacancies_search_context

