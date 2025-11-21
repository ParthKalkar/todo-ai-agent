import json
from agent.persistence import save_state, load_state


def test_persistence_roundtrip(tmp_path):
    path = tmp_path / "state.json"
    state = {"tasks": [{"id": 1, "title": "t", "description": "d", "status": "not-started"}], "trace": []}
    save_state(state, path=str(path))
    loaded = load_state(path=str(path))
    assert isinstance(loaded, dict)
    assert 'tasks' in loaded
    assert loaded['tasks'][0]['id'] == 1
