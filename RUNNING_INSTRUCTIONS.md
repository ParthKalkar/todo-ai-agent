# Running Instructions - Todo AI Agent

Comprehensive guide to set up, run, and use the Agent-Driven TODO Executor.

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Running the Application](#running-the-application)
4. [Using the Web Interface](#using-the-web-interface)
5. [Understanding the Interface](#understanding-the-interface)
6. [Troubleshooting](#troubleshooting)
7. [Example Workflows](#example-workflows)
8. [Performance Tips](#performance-tips)

---

## Prerequisites

Before you start, ensure you have:
- **Python 3.12 or higher** - Check with `python --version`
- **pip package manager** - Usually comes with Python
- **OpenAI API key** - Get it from https://platform.openai.com/api-keys
- **Internet connection** - Needed for LLM API calls
- **Git** (optional) - For cloning the repository

---

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/ParthKalkar/todo-ai-agent.git
cd todo-ai-agent
```

### Step 2: Create Python Virtual Environment

**On macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**On Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

✅ You'll know it worked when you see `(.venv)` at the start of your terminal prompt.

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `fastapi` - Web framework for the UI
- `uvicorn` - ASGI server to run FastAPI
- `langchain` - LLM orchestration library
- `openai` - OpenAI API client
- `sse-starlette` - Server-Sent Events for real-time updates
- `pytest` - Testing framework

### Step 4: Configure OpenAI API Key

**Option A: Using .env file (Recommended)**
```bash
echo "OPENAI_API_KEY=sk-proj-your-actual-key-here" > .env
```

**Option B: Using Environment Variable**

On macOS/Linux:
```bash
export OPENAI_API_KEY="sk-proj-your-actual-key-here"
```

On Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY = "sk-proj-your-actual-key-here"
```

On Windows (CMD):
```cmd
set OPENAI_API_KEY=sk-proj-your-actual-key-here
```

⚠️ **Security Warning**: Never commit your API key to Git. The `.gitignore` file already excludes `.env` files.

### Step 5: Verify Installation
```bash
# Test Python environment
python -c "import langchain; print('✓ LangChain installed')"

# Test database initialization
python -c "from server.database import init_db; init_db(); print('✓ Database ready')"
```

---

## Running the Application

### Web Application (Recommended)

#### Start the Server
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Start the FastAPI server
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
```

**Expected Output:**
```
[planner.py] Python executable: /path/to/.venv/bin/python
[planner.py] LangChain import: OK
[startup] Agent tools imported successfully
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

If you see this output, the server is ready! ✅

#### Access the Web Interface
Open your browser and visit:
```
http://127.0.0.1:8000
```

You should see a modern interface with 4 panels:
- **Left Panel**: Controls and settings
- **Center Panel**: Live event stream
- **Right Panel**: Execution trace
- **Far Right Panel**: HTML output rendering

#### Stop the Server
Press `Ctrl+C` in the terminal running the server.

### Command Line Interface (Optional)

For CLI users (without the web interface):
```bash
# Confirm mode - requires approval before execution
python -m agent.runner --mode confirm --persist

# Auto mode - executes immediately
python -m agent.runner --mode auto --persist
```

---

## Using the Web Interface

### Basic Workflow

1. **Enter Your Goal**
   ```
   Type: "Create a Python script that sorts a list of numbers"
   ```
   - Be specific and clear
   - Explain the desired outcome
   - Mention any special requirements

2. **Choose Execution Mode**
   - **Confirm Mode** (Recommended)
     - Agent creates a plan
     - You review the plan
     - You approve, edit, regenerate, or cancel before execution
     - Best for: Important tasks, learning, complex workflows
   
   - **Auto Mode**
     - Skips the approval step
     - Executes immediately
     - Best for: Simple tasks, quick iterations

3. **Select AI Model**
   - **gpt-4o** - Best quality, higher cost
   - **gpt-4.1** - Fast and reliable
   - **gpt-4.1-mini** - Balanced (Recommended)
   - **gpt-4.1-nano** - Budget-friendly
   - **Random** - Randomly picks a model

4. **Set Max Steps**
   - Default: 6 steps
   - Simple tasks: 3-4 steps
   - Complex tasks: 7-10 steps
   - Each step may call the LLM once

5. **Click "Start run"**
   - The button will gray out during execution
   - Real-time updates appear in the center panel
   - Progress bar shows completion percentage

### Understanding the Interface Panels

#### Left Panel - Controls
- **Goal textarea** - Where you enter your objective
- **Max steps** - Number input for maximum execution steps
- **Mode selector** - Choose "Confirm" or "Auto"
- **Model selector** - Pick which LLM to use
- **Start run button** - Green button to begin execution
- **Undo Last button** - Revert the last task (if supported)
- **Clear button** - Reset all panels
- **Theme toggle** - Switch between dark/light mode

#### Center Panel - Live Stream
Shows all events in real-time, chronologically:

```
run.start          - Execution started with goal
plan               - Task plan generated
task.start         - Task 1 execution began
task.result        - Task 1 completed, result shown
task.start         - Task 2 execution began
task.result        - Task 2 completed, result shown
...
run.complete       - All tasks finished successfully
```

Each event shows:
- Timestamp (HH:MM:SS)
- Badge (color-coded by type)
- Message content
- Structured data (if applicable)

#### Right Panel - Trace
Shows execution progress in a compact format:

```
📋 Plan Generated
   [plan badge with timestamp]

▶️ Task 1: Design Landing Page Layout
   [task badge - yellow]

✅ Result: Created responsive layout...
   [result badge - green, truncated]

🎉 Run Complete
   [complete badge with timestamp]
```

This panel is scrollable - scroll to see all steps.

#### Far Right Panel - Rendered Output
Displays generated HTML/code output:

- **Landing pages** - Full HTML pages you can interact with
- **Email forms** - Functional email capture forms
- **API code** - Python code snippets for APIs
- **UI mockups** - Interactive interface prototypes

If nothing appears, the task generated text output (shown in the Trace panel instead).

### In Confirm Mode: Plan Review

When the agent generates a plan in Confirm mode, you see:

```
Plan Review
─────────────────────
1. Design Landing Page Layout
   - Create responsive grid layout

2. Develop Email Capture Form
   - Add email input and validation

3. Add Coupon Offer Display
   - Show 20% discount prominent

[approve] [edit] [regenerate] [cancel]
```

**Your options:**
- **[Approve]** - Execute this plan as-is
- **[Edit]** - Modify tasks (coming soon - will pause execution)
- **[Regenerate]** - Request a different plan (re-runs planner with same goal)
- **[Cancel]** - Abort the entire run

### Control Buttons

- **Start run** (Green)
  - Submits your goal and starts execution
  - Button disables during execution
  - Re-enables when finished or in error

- **Undo Last** (Orange)
  - Reverts the last completed task
  - Creates a new run with one fewer completed tasks
  - Useful if a task result was wrong

- **Clear** (Gray)
  - Clears all panels
  - Resets the interface to blank state
  - Does NOT cancel running execution

- **🌙 Theme** (Top right)
  - Toggle between dark and light modes
  - Preference is saved in browser

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'langchain'"

**Cause**: Dependencies not installed or virtual environment not activated.

**Solution**:
```bash
# Make sure virtual environment is activated (you should see (.venv) in prompt)
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: "OPENAI_API_KEY not set"

**Cause**: API key not configured.

**Solution**:
```bash
# Method 1: Set before running
export OPENAI_API_KEY="sk-proj-your-key"  # macOS/Linux
set OPENAI_API_KEY=sk-proj-your-key       # Windows CMD

# Method 2: Create .env file
echo "OPENAI_API_KEY=sk-proj-your-key" > .env

# Then start the server
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
```

### Issue: "Port 8000 already in use"

**Cause**: Another application is using port 8000.

**Solution - Option 1: Use a different port**
```bash
python -m uvicorn server.app:app --host 127.0.0.1 --port 8001
# Then visit http://127.0.0.1:8001
```

**Solution - Option 2: Kill the existing process**

On macOS/Linux:
```bash
lsof -ti:8000 | xargs kill -9
```

On Windows:
```cmd
netstat -ano | findstr :8000
# Find the PID in the output, then:
taskkill /PID <PID> /F
```

### Issue: "Cannot reach http://127.0.0.1:8000"

**Causes & Solutions**:
- ❌ Server not running → Check terminal output shows "Uvicorn running on..."
- ❌ Firewall blocking → Check firewall settings for port 8000
- ❌ Browser issue → Try `http://localhost:8000` instead
- ❌ Wrong address → Make sure you're typing it correctly

**Diagnostic steps**:
```bash
# Check if server is running on port 8000
lsof -i :8000         # macOS/Linux
netstat -ano | findstr :8000  # Windows

# If not running, start it
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
```

### Issue: "Browser shows blank page"

**Cause**: JavaScript error or caching issue.

**Solution**:
1. **Hard refresh**: `Cmd+Shift+R` (macOS) or `Ctrl+Shift+R` (Windows/Linux)
2. **Check console for errors**:
   - Press `F12` to open developer tools
   - Click "Console" tab
   - Look for red error messages
3. **Clear cache**:
   - Ctrl+Shift+Delete (most browsers)
   - Select "Cached images and files"
   - Click "Clear data"
4. **Try incognito mode**: `Ctrl+Shift+N` or `Cmd+Shift+N`

### Issue: "Plans not being generated"

**Causes & Solutions**:
- ❌ Invalid API key → Check OpenAI account and generate a new key
- ❌ No internet connection → Check connection
- ❌ Rate limited → Wait a few seconds and try again
- ❌ Account quota exceeded → Check OpenAI billing/usage

**Diagnostic steps**:
```bash
# Test API key
python -c "import openai; openai.api_key = 'your-key'; print(openai.Model.list())"

# Check server logs for detailed errors
# Look at the terminal running the uvicorn server
```

### Issue: "Confirmation buttons not working"

**Cause**: JavaScript element reference issue.

**Solution**:
1. Hard refresh the page: `Cmd+Shift+R` or `Ctrl+Shift+R`
2. Check browser console for errors: `F12` → Console tab
3. Restart the server:
   ```bash
   # Press Ctrl+C to stop
   # Then restart:
   python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
   ```

### Issue: "Database error" or "Run history not saving"

**Cause**: Database file corrupted or permission issue.

**Solution**:
```bash
# The database is stored in agent_runs.db
# Delete it to reset:
rm agent_runs.db

# Or on Windows:
del agent_runs.db

# Restart the server - it will create a new database
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
```

---

## Example Workflows

### Example 1: Create a Landing Page (Confirm Mode) 🌐

**Scenario**: You want an email capture landing page.

**Steps**:
1. Enter goal:
   ```
   Create a beautiful landing page that captures emails and offers a 20% coupon
   ```
2. Mode: `Confirm`
3. Model: `gpt-4.1-mini`
4. Max steps: `6`
5. Click `Start run`

**What happens**:
- Agent analyzes the goal
- Generates a 6-step plan
- Shows plan in left panel for review
- You click `[approve]`
- Agent generates HTML landing page
- Result appears in "Rendered Output" panel (far right)
- You can copy the HTML code

**Expected output**: Full HTML page with:
- Email input field
- Call-to-action button
- 20% coupon display
- Professional styling
- Mobile responsive

---

### Example 2: Build a Python Script (Auto Mode) 🐍

**Scenario**: You need a quick script without reviewing the plan.

**Steps**:
1. Enter goal:
   ```
   Create a Python script that reads a CSV file and generates a summary report with statistics
   ```
2. Mode: `Auto`
3. Model: `gpt-4.1-nano`
4. Max steps: `5`
5. Click `Start run`

**What happens**:
- Agent skips approval
- Generates plan automatically
- Executes all tasks immediately
- Updates appear in real-time

**Expected output**: Python code that:
- Reads CSV files
- Calculates statistics (mean, median, std dev)
- Generates formatted report
- Includes error handling

---

### Example 3: Complex API Integration (Confirm Mode + gpt-4o) 🔌

**Scenario**: Building a Stripe payment API.

**Steps**:
1. Enter goal:
   ```
   Build a REST API that integrates with Stripe for payment processing, with endpoints for creating customers, processing payments, and refunds
   ```
2. Mode: `Confirm`
3. Model: `gpt-4o` (best quality for complex tasks)
4. Max steps: `8`
5. Click `Start run`

**Workflow**:
1. Review detailed plan
2. Approve for execution
3. Monitor progress in real-time
4. View generated code in output panel
5. Use code in your project

**Expected output**: Complete FastAPI application with:
- Stripe API integration
- Customer creation endpoint
- Payment processing endpoint
- Refund endpoint
- Error handling
- Request validation

---

## Performance Tips

### 1. Choose the Right Model
```
gpt-4.1-mini    → Most tasks (balanced)
gpt-4o          → Complex requirements (slow, expensive)
gpt-4.1-nano    → Quick prototypes (fast, cheap)
Random          → Testing/experimentation
```

### 2. Write Clear Goals
**❌ Bad**: "Build something cool"
**✓ Good**: "Create a Python web scraper that extracts articles from BBC News and stores them in SQLite"

### 3. Use Confirm Mode Strategically
- Confirm mode: Important tasks, new workflows, expensive API calls
- Auto mode: Simple tasks, quick iterations, testing

### 4. Monitor Cost
- Each task execution may call the LLM multiple times
- gpt-4o is more expensive than gpt-4.1-mini
- Check OpenAI usage dashboard regularly

### 5. Adjust Max Steps
- Too few (1-3): Task incomplete
- Just right (5-6): Normal execution
- Too many (15+): Expensive, slow, may not improve quality

### 6. Use Cache Effectively
- Recurring tasks benefit from caching
- Check `/metrics` endpoint for cache hit rate
- Cache saves money and improves speed

### 7. Error Recovery
- Use "Undo Last" to revert a failed task
- Cancel and modify goal for different approach
- Check server logs for detailed error messages

---

## API Endpoints (Advanced)

For programmatic access:

### Start a Run
```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Create a landing page",
    "max_steps": 6,
    "mode": "confirm",
    "model": "gpt-4.1-mini"
  }'
```

Returns:
```json
{
  "ok": true,
  "message": "run started",
  "run_id": "5efec0be-1cde-4d93-afb3-1b8d112ecd69"
}
```

### Get Run Details
```bash
curl http://127.0.0.1:8000/run/5efec0be-1cde-4d93-afb3-1b8d112ecd69
```

### Get All Runs
```bash
curl http://127.0.0.1:8000/runs
```

### View Metrics
```bash
curl http://127.0.0.1:8000/metrics
```

### Stream Events
```bash
curl http://127.0.0.1:8000/stream
```

### Send Confirmation
```bash
curl -X POST http://127.0.0.1:8000/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "run_id": "5efec0be-1cde-4d93-afb3-1b8d112ecd69"
  }'
```

---

## Next Steps

1. ✅ **Setup complete**? Start the server and visit the web interface
2. 🎯 **Try an example**: Use one of the workflow examples above
3. 📚 **Read the docs**: Check ARCHITECTURE.md for technical details
4. 🧪 **Run tests**: `python -m pytest` to verify everything works
5. 🚀 **Deploy**: See ARCHITECTURE.md for production deployment

---

## Getting Help

- **Check the troubleshooting section above** for common issues
- **Look at server logs** - Run the terminal output when things go wrong
- **Check browser console** - Press F12 in browser, click Console tab
- **Review examples** - All example workflows are documented above
- **Check API.md** - For detailed API documentation

---

**Happy automating! 🚀** Start the server and transform your goals into action.
