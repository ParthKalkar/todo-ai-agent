# Project Plan — Agent-Driven TODO Executor (Track 2)

Overview
--------
Build a minimal prototype that: accepts a high-level user goal, proposes a structured TODO list, optionally waits for confirmation (or runs in auto mode), executes tasks in a loop, and logs steps/results in the chat. This repo will contain a simple Python-based CLI prototype with optional persistence and a short example transcript.

Assumptions
-----------
- We'll implement a minimal, well-structured Python CLI prototype (single-file runner + small module) to meet the 3-4 hour objective.
- The provided OpenAI API key is stored locally in `.env` (not committed). The key is required only if the agent uses the OpenAI API; otherwise the prototype can run in a mocked/local mode.

Tech stack
----------
- Python 3.10+ (3.11 recommended)
- Minimal dependencies: `python-dotenv` for env loading, `openai` if using the API (optional)
- State persistence: small JSON file (optional bonus)

Deliverables
------------
- Source code: prototype agent (CLI)
- `PROJECT_PLAN.MD` (this file)
- `.env` (contains the API key locally; added to `.gitignore`)
- `README.md` explaining how to run and the execution loop
- Example transcript (in README) showing from goal → plan → execution

High-level milestones
---------------------
1. Chat planning: parse user goal -> produce structured TODO list (titles + descriptions).
2. Confirmation / Auto-mode toggle: support confirm vs auto execution.
3. Execution loop: select next task (first unfinished), run (simulated or real action), mark status and log reflection.
4. Trace/logging: print step-by-step logs to stdout and optionally persist to `state.json`.
5. README + example transcript.

File structure (planned)
------------------------
- `agent/` (source)
  - `__init__.py`
  - `runner.py`        -- CLI entrypoint, handles chat, confirmation, and runs loop
  - `planner.py`       -- produces structured TODO lists from a goal
  - `executor.py`      -- simple executor that simulates/runs tasks and updates state
  - `persistence.py`   -- optional: read/write JSON state
- `.env`               -- local env (gitignored)
- `PROJECT_PLAN.MD`
- `README.md`

Acceptance criteria
-------------------
- Given a user goal, the program outputs a clear TODO list (title + short description for each task).
- In confirm mode, the program waits for user input to approve/edit/cancel before executing.
- In auto mode, the program proceeds immediately and logs each step: selected task, result (done/failed/needs-follow-up), and a short reflection.
- The loop runs until all tasks are terminal and prints a final summary.

Execution details
-----------------
- Task structure: {id, title, description, status}
- Simple execution policy: pick first task with status `not-started`.
- Execution will be simulated (print messages and mark success) for safe deterministic behavior; where appropriate we can wire real actions (file writes, HTTP calls).

Persistence (bonus)
-------------------
- Save state to `state.json` after each task: tasks list and current index. Allows resume.

Extensions (if more time)
-------------------------
- Add a minimal TUI (text UI) showing task statuses live (e.g., using `rich` or `textual`).
- Integrate with OpenAI/LLM to generate plans and reflections dynamically.
- Add unit tests for planner and executor components.

Notes about secrets & environment
--------------------------------
- `.env` has been added to the repo root and contains the provided `OPENAI_API_KEY`. `.gitignore` was updated to avoid accidental commits.

Next steps (short-term)
-----------------------
1. Scaffold the Python project files and `requirements.txt`.
2. Implement a minimal planner + executor and a `runner.py` CLI.
3. Demonstrate an example session and create `README.md`.
