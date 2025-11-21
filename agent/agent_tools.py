import json
from typing import Any
import asyncio

from agent.planner import generate_todo_list, tasks_to_dicts
from agent.executor import execute_task
from agent.persistence import save_state, load_state


def planner_tool(goal: str) -> str:
    """Planner tool: accepts a goal string and returns a JSON array of tasks."""
    tasks = generate_todo_list(goal)
    dicts = tasks_to_dicts(tasks)
    return json.dumps(dicts)


async def executor_tool(task_json: str) -> str:
    """Executor tool: accepts a JSON object representing a task, executes it, updates state, and returns result JSON."""
    try:
        task = json.loads(task_json) if isinstance(task_json, str) else task_json
    except Exception:
        return json.dumps({"error": "invalid task json"})

    # Ensure minimal fields
    if isinstance(task, dict) and 'id' in task:
        res = await execute_task(task)

        # update persisted state if present
        state = load_state() or {}
        tasks = state.get('tasks', [])
        # replace or append
        found = False
        for i, t in enumerate(tasks):
            if t.get('id') == task.get('id'):
                tasks[i] = task
                found = True
                break
        if not found:
            tasks.append(task)
        state['tasks'] = tasks
        trace = state.get('trace', [])
        trace.append({'task_id': res['id'], 'title': task.get('title'), 'result': res['status'], 'reflection': res['reflection']})
        state['trace'] = trace
        save_state(state)

        return json.dumps(res)
    else:
        return json.dumps({"error": "task must be an object with an id"})


def persistence_tool(command: str) -> str:
    """Persistence tool: simple commands:
    - 'load' => returns current state JSON
    - any JSON string => saves that JSON as the state and returns success
    """
    cmd = command.strip()
    if cmd.lower() == 'load':
        state = load_state() or {}
        return json.dumps(state)

    # try to parse JSON and save
    try:
        data = json.loads(command)
        save_state(data)
        return json.dumps({"ok": True})
    except Exception:
        return json.dumps({"error": "invalid command or json"})
