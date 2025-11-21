import os
from agent.executor import execute_task


def test_execute_task_success(monkeypatch):
    # Ensure LLM isn't called
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    task = {'id': 1, 'title': 'Do something', 'description': 'A task', 'status': 'not-started'}
    res = execute_task(task)
    assert res['status'] == 'done'
    assert res['id'] == 1
    assert isinstance(res['reflection'], str) and res['reflection']


def test_execute_task_failure(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    task = {'id': 2, 'title': 'This will fail', 'description': 'A failing task', 'status': 'not-started'}
    res = execute_task(task)
    assert res['status'] == 'failed'
    assert res['id'] == 2
    assert isinstance(res['reflection'], str) and res['reflection']


def test_execute_task_reflection_fallback(monkeypatch):
    # When OPENAI_API_KEY is not present, reflection should equal deterministic outcome
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    task = {'id': 3, 'title': 'Do something else', 'description': 'A task', 'status': 'not-started'}
    res = execute_task(task)
    assert res['reflection'] == 'Completed successfully (simulated).'
