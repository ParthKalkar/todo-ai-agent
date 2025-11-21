import builtins
from agent.runner import prompt_confirmation, prompt_resume, do_edit


def test_prompt_confirmation(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'approve')
    assert prompt_confirmation() == 'approve'


def test_prompt_resume_yes(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    assert prompt_resume() is True


def test_prompt_resume_no(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'n')
    assert prompt_resume() is False


def test_do_edit(monkeypatch, tmp_path):
    # Prepare a task list and simulate editing title and description
    tasks = [{'id': 1, 'title': 'Old', 'description': 'Old desc', 'status': 'not-started'}]
    inputs = iter(['1', 'New title', 'New desc'])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    do_edit(tasks)
    assert tasks[0]['title'] == 'New title'
    assert tasks[0]['description'] == 'New desc'
