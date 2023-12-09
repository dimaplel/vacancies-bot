from dataclasses import dataclass


@dataclass
class SeekerProfile:
    _user_id: int
    _portfolio_ref: str
    _seeker_node_ref: str


    def get_id(self) -> int:
        return self._user_id