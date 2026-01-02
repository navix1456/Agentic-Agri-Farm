class SessionStore:
    def __init__(self) -> None:
        self.state: dict = {
            "crop": None,
            "location": None,
            "season": None,
            "last_agent": None,
            "history": [],
        }

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            self.state[key] = value

    def get(self, key: str, default=None):
        return self.state.get(key, default)

    def append_history(self, entry: dict) -> None:
        self.state.setdefault("history", []).append(entry)

    def to_dict(self) -> dict:
        return dict(self.state)
