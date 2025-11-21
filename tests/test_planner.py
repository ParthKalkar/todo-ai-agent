import os
from agent.planner import generate_todo_list, tasks_to_dicts


def test_generate_todo_list_basic(monkeypatch):
    # Ensure LLM path is disabled
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    tasks = generate_todo_list("Build a small CLI with confirm and auto modes")
    assert tasks
    assert len(tasks) >= 4
    ids = [t.id for t in tasks]
    assert ids == sorted(ids)


def test_generate_with_empty_goal():
    tasks = generate_todo_list("")
    assert tasks == []


def test_tasks_to_dicts(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    tasks = generate_todo_list("Sample goal")
    dicts = tasks_to_dicts(tasks)
    assert isinstance(dicts, list)
    assert all(isinstance(d, dict) for d in dicts)
    for d in dicts:
        assert 'id' in d and 'title' in d and 'description' in d and 'status' in d
