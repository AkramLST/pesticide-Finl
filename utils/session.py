class Session:
    """Singleton holding the currently logged-in user's data."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._user = None
        return cls._instance

    def login(self, user_row: dict):
        self._user = user_row

    def logout(self):
        self._user = None

    @property
    def is_logged_in(self) -> bool:
        return self._user is not None

    @property
    def user(self) -> dict:
        return self._user or {}

    @property
    def user_id(self):
        return self._user.get("id") if self._user else None

    @property
    def username(self) -> str:
        return self._user.get("username", "") if self._user else ""

    @property
    def name(self) -> str:
        return self._user.get("name", "") if self._user else ""

    @property
    def role(self) -> str:
        return self._user.get("role", "") if self._user else ""

    def is_admin(self) -> bool:
        return self.role == "Admin"


session = Session()
