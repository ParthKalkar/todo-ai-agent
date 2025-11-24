import argparse
import asyncio
import os
import sys
import json
from typing import List, Dict

from dotenv import load_dotenv

from agent.planner import generate_todo_list
from agent.executor import execute_task
from agent.persistence import save_state, load_state


def print_plan(tasks: List[Dict]):
    print("\nProposed TODO list:")
    for t in tasks:
        print(f"[{t['id']}] {t['title']} — {t['description']} (status: {t['status']})")


def prompt_confirmation() -> str:
    print("\nOptions: [approve] [edit] [regenerate] [cancel]")
    choice = input("Choose: ").strip().lower()
    return choice


def prompt_resume() -> bool:
    print("A saved state was found. Do you want to resume? [y/N]")
    choice = input("Resume: ").strip().lower()
    return choice in ("y", "yes")


def do_edit(tasks: List[Dict]):
    print('\nEdit tasks — current tasks:')
    for t in tasks:
        print(f"[{t['id']}] {t['title']} — {t['description']} (status: {t.get('status')})")
    try:
        tid = int(input('Enter task id to edit (or 0 to cancel): ').strip())
    except Exception:
        print('Invalid id.')
        return
    if tid == 0:
        return
    matching = [t for t in tasks if t['id'] == tid]
    if not matching:
        print('Task not found.')
        return
    t = matching[0]
    new_title = input(f"New title (enter to keep) [{t['title']}]: ").strip()
    new_desc = input(f"New description (enter to keep) [{t['description']}]: ").strip()
    if new_title:
        t['title'] = new_title
    if new_desc:
        t['description'] = new_desc
    print('Task updated.')


async def run_execution_loop(tasks: List[Dict], persist: bool = True):
    trace = []
    # Ensure tasks are dicts
    for t in tasks:
        if 'status' not in t:
            t['status'] = 'not-started'

    while True:
        # find first not-started
        next_task = None
        for t in tasks:
            if t.get('status') == 'not-started':
                next_task = t
                break

        if not next_task:
            print('\nAll tasks are terminal. Exiting loop.')
            break

        print(f"\nSelected task #{next_task['id']}: {next_task['title']}")
        result = await execute_task(next_task)
        trace_entry = {
            'task_id': next_task['id'],
            'title': next_task['title'],
            'result': result['status'],
            'reflection': result['reflection'],
        }
        trace.append(trace_entry)
        if persist:
            save_state({'tasks': tasks, 'trace': trace}, path='state.json')
        # If UI present and this was a landing/landing page task, generate HTML preview
        try:
            if next_task.get('title', '').lower().find('landing') != -1:
                from agent.ui import generate_landing_preview
                out = generate_landing_preview('preview/landing.html', site_title='Coupon Bazaar')
                print(f"Landing page preview generated: {out}")
        except Exception:
            # ignore preview failures
            pass

    # summary
    print('\nExecution summary:')
    for e in trace:
        print(f"- Task {e['task_id']}: {e['result']} — {e['reflection']}")


def main(argv=None):
    load_dotenv()  # load .env if present

    parser = argparse.ArgumentParser(description='Agent-driven TODO executor (prototype)')
    parser.add_argument('--mode', choices=['confirm', 'auto'], default='confirm', help='Operation mode')
    parser.add_argument('--persist', action='store_true', help='Persist state to state.json')
    parser.add_argument('--ui', action='store_true', help='Show a simple TUI (requires rich)')
    parser.add_argument('--agent', action='store_true', help='Run in agentic mode (LangChain agent when available)')
    args = parser.parse_args(argv)

    print('Agent-driven TODO executor (prototype)')

    # If there is a saved state, offer resume
    saved = load_state(path='state.json')
    if saved and saved.get('tasks'):
        if prompt_resume():
            tasks = saved.get('tasks')
            print('Resuming from saved state.')
        else:
            print('Not resuming; continuing to new planning.')
            goal = input('\nEnter a high-level goal: ').strip()
            if not goal:
                print('No goal provided. Exiting.')
                sys.exit(1)
            tasks_objs = generate_todo_list(goal)
            tasks = [t.__dict__ for t in tasks_objs]
    else:
        goal = input('\nEnter a high-level goal: ').strip()
        if not goal:
            print('No goal provided. Exiting.')
            sys.exit(1)
        # If UI mode requested, show a generating indicator first
        if args.ui:
            try:
                from agent.ui import show_tasks_ui
                show_tasks_ui([], generating=True)
            except Exception:
                pass
        tasks_objs = generate_todo_list(goal)
        tasks = [t.__dict__ for t in tasks_objs]

    while True:
        # show plan (with optional UI)
        if args.ui:
            try:
                from agent.ui import show_tasks_ui
                c = show_tasks_ui(tasks)
                if c == 'e':
                    do_edit(tasks)
                    if args.persist:
                        save_state({'tasks': tasks}, path='state.json')
                    continue
                elif c == 'q':
                    print('Quitting per UI request.')
                    break
            except Exception:
                # fall back to text plan if UI not available
                print('(UI not available; showing text plan)')
                print_plan(tasks)
        else:
            print_plan(tasks)

        if args.agent:
            # Run agentic mode
            try:
                from agent.agent_runner import run_agent
                goal_text = goal
                print('Starting agentic run...')
                state = run_agent(goal_text, max_steps=6)
                print('Agent run finished. State summary:')
                print(state)
                break
            except Exception as e:
                print(f'Agent run failed: {e} — falling back to interactive mode')
        if args.mode == 'confirm':
            choice = prompt_confirmation()
            if choice in ('approve', 'a'):
                print('Approved — starting execution.')
                asyncio.run(run_execution_loop(tasks, persist=args.persist))
                break
            elif choice == 'edit':
                do_edit(tasks)
                if args.persist:
                    save_state({'tasks': tasks}, path='state.json')
                # loop back to show updated plan
            elif choice == 'regenerate':
                if args.ui:
                    try:
                        from agent.ui import show_tasks_ui
                        show_tasks_ui([], generating=True)
                    except Exception:
                        pass
                tasks_objs = generate_todo_list(goal + ' (regenerated)')
                tasks = [t.__dict__ for t in tasks_objs]
                print('Regenerated plan.')
            elif choice == 'cancel':
                print('Cancelled by user.')
                break
            else:
                print('Unknown choice. Please enter approve, edit, regenerate, or cancel.')
        else:
            # auto
            print('Auto mode — starting execution immediately.')
            asyncio.run(run_execution_loop(tasks, persist=args.persist))
            break


if __name__ == '__main__':
    main()
