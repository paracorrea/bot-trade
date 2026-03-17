import json
import os


class StateManager:
    def __init__(self, filename="state.json"):
        self.filename = filename
        self.default_state = {
            "symbol": "",
            "cycle_id": "",
            "has_open_position": False,
            "buy_order_id": "",
            "sell_order_id": "",
            "last_status": "",
            "notes": ""
        }
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            self.save_state(self.default_state)

    def load_state(self):
        with open(self.filename, mode="r", encoding="utf-8") as file:
            return json.load(file)

    def save_state(self, state):
        with open(self.filename, mode="w", encoding="utf-8") as file:
            json.dump(state, file, indent=2, ensure_ascii=False)

    def reset_state(self, symbol=""):
        state = self.default_state.copy()
        state["symbol"] = symbol
        self.save_state(state)