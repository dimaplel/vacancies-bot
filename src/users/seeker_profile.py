class SeekerProfile:
    _user_id: int
    _portfolio_ref: str
    _seeker_node_ref: str

    def __init__(self, user_id: int, portfolio_ref: str, seeker_node_ref: str):
        self._user_id = user_id
        self._portfolio_ref = portfolio_ref
        self._portfolio_ref = seeker_node_ref


    def set_portfolio_ref(self, portfolio_ref: str):
        self._portfolio_ref = portfolio_ref


    def set_seeker_node_ref(self, seeker_node_ref: str):
        self._seeker_node_ref = seeker_node_ref


    def get_portfolio_ref(self) -> str:
        return self._portfolio_ref


    def get_seeker_node_ref(self) -> str:
        return self._seeker_node_ref