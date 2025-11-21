import json
from typing import Any, Dict


def save_state(state: Dict[str, Any], path: str = "state.json") -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def load_state(path: str = "state.json") -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
