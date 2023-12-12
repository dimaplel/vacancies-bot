from dataclasses import dataclass
from typing import Dict, Any

from src.connections import MongoDBConnection
from src.keyboards.profile_keyboards import SeekerProfileKeyboardMarkup


@dataclass
class SeekerProfile:
    _user_id: int
    _portfolio_ref: str
    _seeker_node_ref: str
    seeker_markup = SeekerProfileKeyboardMarkup()


    def get_id(self) -> int:
        return self._user_id


    # Queries mongodb connection for JSON document referenced by self._portfolio_ref
    # Returns the JSON document if any exists
    def get_portfolio(self, mongodb_connection: MongoDBConnection) -> (Dict[str, Any] | None):
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
