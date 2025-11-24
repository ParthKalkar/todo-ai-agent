# 📁 Project Files & Configuration Guide

Complete reference for all files, scripts, and configuration in the Agent-Driven TODO Executor project.

## Table of Contents
1. [Shell Scripts](#shell-scripts)
2. [Configuration Files](#configuration-files)
3. [Data Files](#data-files)
4. [Project Structure](#project-structure)
5. [Usage Guide](#usage-guide)

---

## 🔧 Shell Scripts

### start_server.sh
**Purpose**: Quick startup script for the web application

**Location**: `/start_server.sh`

**Contents**:
```bash
#!/bin/bash
# Start the todo-ai-agent web server with API key configured

set -a
source .env 2>/dev/null || echo "Note: .env file not found, using OPENAI_API_KEY from environment"
set +a

cd "$(dirname "$0")" || exit
source .venv/bin/activate
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
```

**What it does**:
- Loads environment variables from `.env` file if it exists
- Activates Python virtual environment
- Starts FastAPI server on localhost:8000

**How to use**:
```bash
# Make it executable (first time only)
chmod +x start_server.sh

# Run the script
./start_server.sh
```

**Expected output**:
```
[planner.py] Python executable: /path/to/.venv/bin/python
[startup] Database initialized
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Requirements**:
- Python virtual environment (`.venv/`) must exist
- OpenAI API key set in `.env` or environment
- All dependencies installed via `pip install -r requirements.txt`

---

### demo.sh
**Purpose**: Interactive demonstration of all system features

**Location**: `/demo.sh`

**Size**: 246 lines of comprehensive demo code

**Features**:
- 🎨 Colored terminal output for readability
- 🔍 Environment validation (checks for .venv, dependencies)
- 🚀 Automatic server startup and shutdown
- 📊 Multiple demo scenarios testing different workflows
- 📈 System metrics display
- 🌐 Opens web UI in browser
- ⌨️ Tests CLI interface
- 🛡️ Automatic cleanup on exit with trap handler

**Key Functions**:
- `check_environment()` - Validates setup
- `start_server()` - Starts FastAPI server
- `run_demo_scenarios()` - Executes example workflows
- `show_metrics()` - Displays system stats
- `show_web_ui()` - Opens browser to web interface
- `test_cli()` - Tests command-line interface
- `cleanup()` - Stops server on exit

**How to use**:
```bash
# Make it executable (first time only)
chmod +x demo.sh

# Run the demo
./demo.sh
```

**What it demonstrates**:
```
✅ Intelligent goal planning with LLM
✅ Real-time streaming progress updates
✅ Interactive confirmation mode
✅ Circuit breaker for fault tolerance
✅ Undo functionality with state rollback
✅ Modern web UI with theme toggle
✅ Comprehensive metrics and monitoring
✅ CLI and API interfaces
✅ Error handling and recovery
✅ Production-grade reliability features
```

**Requirements**:
- Same as start_server.sh
- Browser installed (for showing web UI)

---

## ⚙️ Configuration Files

### .env (Environment Configuration)
**Purpose**: Store sensitive configuration like API keys

**Location**: `/.env`

**Template Location**: `/.env.example`

**Contents**:
```dotenv
# OpenAI API Configuration
# Get your API key from: https://platform.openai.com/account/api-keys
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Optional: Set default model (defaults to gpt-4o if not specified)
# OPENAI_MODEL=gpt-4o
```

**How to create it**:
```bash
# Method 1: Copy from template
cp .env.example .env
nano .env  # Edit with your API key

# Method 2: Create manually
echo "OPENAI_API_KEY=sk-proj-your-key-here" > .env
```

**What each variable does**:
- `OPENAI_API_KEY` (required)
  - Your OpenAI API key
  - Get from https://platform.openai.com/api-keys
  - Never commit to Git (it's in .gitignore)
  - Used by planner and executor tools

- `OPENAI_MODEL` (optional)
  - Default LLM model to use
  - Defaults to gpt-4o if not set
  - Can be overridden per run in web UI

**⚠️ Security Notes**:
- **Never share your .env file** - contains API credentials
- **Never commit to Git** - already in .gitignore
- **Never hard-code API keys** - always use .env
- **Rotate keys regularly** - best practice for security

**Alternative: Set via environment**:
```bash
# Instead of .env file, you can set environment variable
export OPENAI_API_KEY="sk-proj-your-key"
./start_server.sh
```

---

### .env.example (Configuration Template)
**Purpose**: Template showing all possible environment variables

**Location**: `/.env.example`

**Contents**:
```dotenv
# OpenAI API Configuration
# Get your API key from: https://platform.openai.com/account/api-keys
OPENAI_API_KEY=sk-proj-your-api-key-here

# Optional: Set default model (defaults to gpt-4o if not specified)
# OPENAI_MODEL=gpt-4o
```

**How to use**:
- Reference this file to see all available configuration options
- Copy it to `.env` and fill in your actual values
- Never modify this file for your credentials
- This file is safe to commit (doesn't have real credentials)

---

### .gitignore (Git Ignore Configuration)
**Purpose**: Tell Git which files NOT to commit

**Typically ignores**:
- `.env` - Contains API credentials
- `.venv/` - Virtual environment (can be recreated)
- `__pycache__/` - Python bytecode
- `*.pyc` - Compiled Python
- `.DS_Store` - macOS metadata
- `node_modules/` - JavaScript dependencies (if used)
- IDE files (`.vscode/`, `.idea/`)

**Why it matters**:
- Prevents accidental credential leaks
- Keeps repository clean
- Prevents conflicts from environment-specific files

---

## 💾 Data Files

### state.json (CLI Execution History)
**Purpose**: Persistent storage of agent execution state for CLI interface

**Location**: `/state.json`

**Created by**: `python -m agent.runner --mode confirm --persist`

**Structure**:
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Design Landing Page Layout",
      "description": "Create a visually appealing and user-friendly layout for the landing page.",
      "status": "done"
    },
    {
      "id": 2,
      "title": "Develop Email Capture Form",
      "description": "Implement a form to collect visitor email addresses securely.",
      "status": "done"
    }
  ],
  "trace": [
    {
      "task_id": 1,
      "title": "Define Landing Page Structure",
      "result": "done",
      "reflection": "The landing page structure was effectively defined, ensuring a clear organization of essential sections..."
    },
    {
      "task_id": 2,
      "title": "Design Visual Elements",
      "result": "done",
      "reflection": "The design for the landing page was successfully completed, effectively incorporating a cohesive color scheme..."
    }
  ]
}
```

**Field Descriptions**:

**tasks array**:
- `id` (number) - Unique task identifier
- `title` (string) - Task name/title
- `description` (string) - What the task does
- `status` (string) - Current state:
  - `done` - Task completed successfully
  - `in-progress` - Task currently executing
  - `failed` - Task execution failed
  - `not-started` - Task hasn't started

**trace array**:
- `task_id` (number) - Which task this trace belongs to
- `title` (string) - Task being executed
- `result` (string) - Outcome (done, failed, etc.)
- `reflection` (string) - AI-generated summary of task execution (1-2 sentences)
  - Generated by LLM after each task
  - Explains what was accomplished or what went wrong
  - Useful for understanding task results

**When it's created**:
```bash
# CLI with persist flag - saves to state.json
python -m agent.runner --mode confirm --persist

# Web interface - saves to SQLite database instead
./start_server.sh
```

**How it's used**:
1. **State persistence**: Resume interrupted runs
2. **Audit trail**: Complete history of executions
3. **Debugging**: LLM reflections help understand task outcomes
4. **Recovery**: Restore previous state if needed

**Example workflow**:
```bash
# Start with persist
$ python -m agent.runner --persist
Goal: Create a landing page
Mode: Confirm
[Task 1 completes, saves to state.json]
[Task 2 completes, saves to state.json]
[User interrupts with Ctrl+C]

# Later, run again - state.json is loaded
$ python -m agent.runner --persist
[Previous tasks are already in state.json]
[Can resume from where it left off]
```

**Editing state.json**:
- You can manually edit if needed (it's just JSON)
- Useful for resetting failed tasks or testing
- Changes take effect on next run with `--persist`

---

### agent_runs.db (Web Run History Database)
**Purpose**: SQLite database storing web interface run history

**Location**: `/agent_runs.db`

**Created by**: First run of `./start_server.sh`

**Auto-created schema**:
```sql
-- Stores run information
CREATE TABLE runs (
  id TEXT PRIMARY KEY,
  goal TEXT,
  model TEXT,
  mode TEXT,
  status TEXT,
  created_at TIMESTAMP,
  completed_at TIMESTAMP
)

-- Stores tasks for each run
CREATE TABLE tasks (
  id TEXT,
  run_id TEXT,
  task_id TEXT,
  title TEXT,
  description TEXT,
  status TEXT,
  FOREIGN KEY (run_id) REFERENCES runs(id)
)

-- Stores event stream for real-time updates
CREATE TABLE events (
  id INTEGER PRIMARY KEY,
  run_id TEXT,
  event_type TEXT,
  data TEXT,
  timestamp TIMESTAMP,
  FOREIGN KEY (run_id) REFERENCES runs(id)
)
```

**What it stores**:
- **runs**: Run metadata (ID, goal, model, status)
- **tasks**: Task details for each run
- **events**: Event stream for real-time updates

**How to access**:
```bash
# View all runs
curl http://127.0.0.1:8000/runs

# View specific run details
curl http://127.0.0.1:8000/run/{run_id}
```

**To reset/delete**:
```bash
# Remove the database file
rm agent_runs.db

# Restart server - it creates a new empty database
./start_server.sh
```

---

## 📂 Project Structure

### Complete Directory Layout
```
todo-ai-agent/
├── 📄 README.md                    # Main project documentation ⭐
├── 📄 RUNNING_INSTRUCTIONS.md      # Complete setup guide ⭐
├── 📄 ARCHITECTURE.md              # System design and deployment
├── 📄 FEATURES.md                  # Feature showcase
├── 📄 API.md                       # API reference
├── 📄 PROJECT_FILES.md             # This file
│
├── 🔧 Configuration & Scripts
│   ├── .env                        # Environment variables (create from .env.example)
│   ├── .env.example                # API key template
│   ├── start_server.sh             # Quick server startup
│   ├── demo.sh                     # Interactive demo
│   ├── .gitignore                  # Git ignore rules
│   └── requirements.txt            # Python dependencies
│
├── 💾 Data Files
│   ├── state.json                  # CLI execution history
│   └── agent_runs.db               # Web run history (SQLite)
│
├── 🐍 Python Packages
│   ├── agent/                      # Core agent logic
│   │   ├── __init__.py
│   │   ├── agent_runner.py         # Main agent orchestrator
│   │   ├── agent_tools.py          # LangChain tool wrappers
│   │   ├── executor.py             # Task execution engine
│   │   ├── persistence.py          # JSON state management
│   │   ├── planner.py              # LLM-powered planning
│   │   ├── runner.py               # CLI interface
│   │   ├── ui.py                   # Rich TUI components
│   │   └── __pycache__/            # Compiled Python bytecode
│   │
│   └── server/                     # Web application
│       ├── __init__.py
│       ├── app.py                  # FastAPI application
│       ├── database.py             # SQLite operations
│       ├── __pycache__/            # Compiled bytecode
│       └── static/
│           ├── index.html          # Web UI (modern interface)
│           └── empty.html          # Placeholder
│
├── 🧪 Testing
│   ├── tests/
│   │   ├── conftest.py             # Pytest configuration
│   │   ├── test_executor.py        # Executor tests
│   │   ├── test_persistence.py     # Persistence tests
│   │   ├── test_planner.py         # Planner tests
│   │   └── test_runner.py          # Runner tests
│   └── pytest.ini                  # Test configuration
│
├── 📂 Environment
│   ├── .venv/                      # Python virtual environment (created by you)
│   └── .git/                       # Git repository
│
└── 📂 Preview (Unused)
    └── preview/
        └── landing.html            # Legacy preview file
```

---

## 🚀 Usage Guide

### Scenario 1: Start Web Server
```bash
# Setup (first time only)
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
nano .env

# Start server
./start_server.sh

# Visit http://127.0.0.1:8000 in browser
```

---

### Scenario 2: Run Interactive Demo
```bash
# Make sure .venv and .env are set up (from Scenario 1)

# Run full demo
./demo.sh

# Demo will:
# ✅ Check environment
# ✅ Start server
# ✅ Run example workflows
# ✅ Show metrics
# ✅ Open web UI in browser
# ✅ Test CLI
# ✅ Cleanup automatically
```

---

### Scenario 3: CLI with State Persistence
```bash
# Start with persist flag
python -m agent.runner --mode confirm --persist

# You'll be prompted:
# Enter your goal: "Create a landing page"
# [Tasks execute and save to state.json]

# If interrupted:
# Press Ctrl+C to stop

# Run again - state.json is reloaded:
python -m agent.runner --mode confirm --persist
# [Previous tasks shown, can resume or start over]
```

---

### Scenario 4: Programmatic API Access
```bash
# Start server (from Scenario 1)
./start_server.sh

# In another terminal, execute a run
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Create a Python script",
    "max_steps": 5,
    "mode": "auto",
    "model": "gpt-4.1-mini"
  }'

# Get run history
curl http://127.0.0.1:8000/runs

# Get specific run details
curl http://127.0.0.1:8000/run/{run_id}
```

---

### Scenario 5: Configuration & Secrets
```bash
# Option 1: Use .env file (Recommended)
cp .env.example .env
echo "OPENAI_API_KEY=sk-proj-your-actual-key" >> .env
./start_server.sh

# Option 2: Set environment variable (CI/CD)
export OPENAI_API_KEY="sk-proj-your-actual-key"
./start_server.sh

# Option 3: Pass via command (Not recommended for secrets)
OPENAI_API_KEY="sk-proj-your-key" python -m uvicorn server.app:app
```

---

## 📋 Quick Reference

| File | Type | Purpose | Created By | Status |
|------|------|---------|------------|--------|
| `.env` | Config | API key storage | You (from .env.example) | Required |
| `.env.example` | Template | Config template | Project | Reference only |
| `start_server.sh` | Shell script | Quick server start | Project | Ready to use |
| `demo.sh` | Shell script | Interactive demo | Project | Ready to use |
| `state.json` | JSON | CLI execution history | CLI with --persist | Auto-created |
| `agent_runs.db` | SQLite DB | Web run history | Web server | Auto-created |
| `.gitignore` | Config | Git ignore rules | Project | Built-in |

---

## 🔐 Security Best Practices

### API Keys
- ✅ Store in `.env` (never in code)
- ✅ Use `.env.example` as template
- ✅ Rotate keys periodically
- ❌ Never commit `.env` to Git
- ❌ Never hard-code keys in scripts
- ❌ Never share API keys

### Data Files
- ✅ Review `.gitignore` to prevent leaks
- ✅ Back up `state.json` if important
- ✅ Keep `agent_runs.db` secure
- ❌ Don't share database with credentials

### Scripts
- ✅ Make scripts executable: `chmod +x script.sh`
- ✅ Review script contents before running
- ✅ Don't run scripts from untrusted sources
- ❌ Don't modify production scripts without testing

---

## 🆘 Troubleshooting

### ".env file not found"
**Solution**:
```bash
cp .env.example .env
nano .env  # Add your API key
```

### "Virtual environment not found"
**Solution**:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### "Port 8000 already in use"
**Solution**:
```bash
# Use different port
python -m uvicorn server.app:app --host 127.0.0.1 --port 8001

# Or kill process using 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
```

### "state.json keeps growing"
**Solution**:
```bash
# Backup old state
cp state.json state.json.backup

# Reset state
rm state.json

# Next run creates fresh state.json
python -m agent.runner --persist
```

### Database error
**Solution**:
```bash
# Reset database
rm agent_runs.db

# Restart server - creates new database
./start_server.sh
```

---

## 📖 See Also

- **[README.md](README.md)** - Project overview and quick start
- **[RUNNING_INSTRUCTIONS.md](RUNNING_INSTRUCTIONS.md)** - Complete setup guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and scalability
- **[API.md](API.md)** - API reference and examples
- **[FEATURES.md](FEATURES.md)** - Feature showcase

---

## Next Steps

1. ✅ Review this guide
2. 📝 Set up `.env` with your API key
3. 🚀 Run `./start_server.sh` or `./demo.sh`
4. 🌐 Visit `http://127.0.0.1:8000` in browser
5. 📚 Check other documentation files for detailed info

**Happy automating!** 🤖
