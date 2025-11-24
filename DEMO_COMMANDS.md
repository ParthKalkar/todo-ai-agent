# 🚀 Demo Commands - Copy & Paste Ready

Quick reference with all commands you need to demonstrate the system.

---

## 📋 CLI Demo Commands

### Setup (Run once)
```bash
cd /Users/parthkalkar/Desktop/todo-ai-agent
source .venv/bin/activate
```

### Start CLI Demo
```bash
python -m agent.runner --mode confirm --persist
```

### Example Goals to Enter (Choose one or similar)
```
Create a Python script that fetches weather data for a city and displays it in a formatted table
```

Alternative goals:
```
Build a Python CLI tool that organizes files in a directory by type
```

```
Create a REST API endpoint for a todo management system with CRUD operations
```

```
Write a web scraper that extracts product information from an e-commerce site
```

---

## 🌐 Web Interface Demo Commands

### Terminal 1: Start Server
```bash
cd /Users/parthkalkar/Desktop/todo-ai-agent
./start_server.sh
```

### Terminal 2: Open Browser
```bash
# macOS
open http://127.0.0.1:8000

# Linux
xdg-open http://127.0.0.1:8000

# Windows
start http://127.0.0.1:8000
```

Or manually open browser and visit:
```
http://127.0.0.1:8000
```

### Example Goals to Enter (Choose one or similar)
```
Build a Python CLI tool that organizes files in a directory by type
```

Alternative goals:
```
Create a web scraper that extracts blog posts and saves them to a CSV file
```

```
Develop a Python decorator for API rate limiting with configurable limits
```

```
Build a command-line note-taking application with search functionality
```

---

## 🎬 Interactive Demo Script

### Full Demo Flow
```bash
# Terminal 1: Start everything
cd /Users/parthkalkar/Desktop/todo-ai-agent
source .venv/bin/activate
./start_server.sh

# Terminal 2: While server starts, open browser
open http://127.0.0.1:8000

# Terminal 3: Keep ready for CLI demo
cd /Users/parthkalkar/Desktop/todo-ai-agent
source .venv/bin/activate
```

### Then demonstrate:

#### Step 1: Show Web Interface
- Browser shows http://127.0.0.1:8000
- Click "Launch Agent"
- Show the 4-column layout

#### Step 2: Enter Goal in Web
- Copy goal: `Create a Python script that analyzes CSV data and generates summary statistics`
- Paste into input field
- Select model: `gpt-4o`
- Select mode: `Confirm`
- Click "Execute Agent"
- Watch the real-time plan generation
- Click "Approve"
- Watch execution with streaming output

#### Step 3: Show CLI Demo
- In Terminal 3, run: `python -m agent.runner --mode confirm --persist`
- Enter goal: `Build a CLI tool for todo management with persistence`
- Type: `yes` to approve the plan
- Watch execution

#### Step 4: Show Completion
- Back in browser, watch metrics update
- Explain the real-time streaming
- Show generated code in output panel

---

## 📊 Check System Status Commands

### Verify Setup
```bash
# Check if API key is configured
echo "API Key status: ${OPENAI_API_KEY:0:20}..."

# Check Python version
python --version

# Check dependencies
pip list | grep -E "fastapi|langchain|openai"

# Check if .env exists
cat .env | head -2
```

### Test Server Connectivity
```bash
# Test if server can start
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000 &
sleep 2
curl -s http://127.0.0.1:8000 && echo "✅ Server OK" || echo "❌ Server failed"
pkill -f uvicorn
```

### Check Database
```bash
# Verify database exists
ls -lh agent_runs.db

# Check runs table
sqlite3 agent_runs.db "SELECT COUNT(*) as total_runs FROM runs;"
```

### Check State File
```bash
# View state.json structure
cat state.json | jq '.' | head -30

# Count tasks in state
cat state.json | jq '.tasks | length'
```

---

## 🎯 Quick Demo Scenarios

### Scenario 1: Fast CLI Demo (2 minutes)
```bash
# Command 1
python -m agent.runner --mode confirm --persist

# Enter goal (copy-paste):
Create a Python function that validates email addresses using regex

# Type: yes (to approve)
# Watch execution
# Press Ctrl+C when done
```

### Scenario 2: Web Interface Demo (5 minutes)
```bash
# Terminal 1
./start_server.sh

# Terminal 2
open http://127.0.0.1:8000

# In browser:
# 1. Click "Launch Agent"
# 2. Enter goal: Develop a decorator for timing function execution
# 3. Select mode: Auto (to skip approval)
# 4. Click Execute
# 5. Watch real-time streaming
```

### Scenario 3: Full Feature Demo (10 minutes)
```bash
# Start server
./start_server.sh

# Open browser with 2 different goals:
# Goal 1 (Confirm mode): Create a Python script for batch image resizing
# Goal 2 (Auto mode): Build a decorator for memoization in Python

# Then show CLI:
python -m agent.runner --mode confirm --persist
# Enter: Write a utility to convert between different file formats
```

---

## 🔧 Troubleshooting Quick Commands

### If Server Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process using port
lsof -ti:8000 | xargs kill -9

# Try starting again
./start_server.sh
```

### If API Key Missing
```bash
# Check current API key
echo $OPENAI_API_KEY

# Load from .env file
source .env
echo "API key loaded: ${OPENAI_API_KEY:0:20}..."
```

### If Virtual Environment Missing
```bash
# Create new environment
python -m venv .venv

# Activate it
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Clear Old Data
```bash
# Remove web database
rm agent_runs.db

# Reset state file
rm state.json
echo '{"tasks": [], "trace": []}' > state.json

# Restart server
./start_server.sh
```

---

## 📱 Browser Console Commands (Optional)

If you want to show technical details in browser:

```javascript
// View current run ID
console.log("Current Run ID:", currentRunId);

// View pending confirmation status
console.log("Pending Confirmation:", pendingConfirmation);

// View all events received
console.log("Event Log:", eventLog);
```

---

## 📹 Screen Recording Setup

### Before Recording - Final Checks
```bash
# 1. Clean up old runs (optional)
rm agent_runs.db

# 2. Test the complete flow once
./start_server.sh

# 3. In another terminal, test CLI
python -m agent.runner --mode confirm --persist
# (Enter dummy goal, approve, cancel with Ctrl+C)

# 4. Close everything
pkill -f uvicorn

# 5. Clear terminal
clear
```

### Start Recording - CLI Demo
```bash
# Command 1: Navigate to project
cd /Users/parthkalkar/Desktop/todo-ai-agent

# Command 2: Activate environment
source .venv/bin/activate

# Command 3: Start CLI
python -m agent.runner --mode confirm --persist

# Command 4 (after prompt): Enter goal
Create a Python script that monitors a directory for new files and processes them

# Command 5: Respond to prompt
yes

# (Let it run, watch the output)
```

### Start Recording - Web Demo
```bash
# Terminal 1: Start server
cd /Users/parthkalkar/Desktop/todo-ai-agent
./start_server.sh

# Terminal 2: Open browser (after server starts)
open http://127.0.0.1:8000

# In browser: Navigate and perform these steps:
# 1. Refresh to show landing page
# 2. Click "Launch Agent"
# 3. Enter goal: Develop a Python utility for validating and parsing YAML files
# 4. Keep mode as "Confirm"
# 5. Click "Execute Agent"
# 6. Wait for plan to generate (don't approve yet, let it show in video)
# 7. Click "Approve"
# 8. Watch execution stream in real-time
```

---

## 📊 Demo Goals (Pick Your Favorite)

### Easy (Fast execution - 1-2 minutes)
```
Create a Python function that validates email addresses
```

```
Write a decorator that adds logging to functions
```

```
Build a utility to convert temperature between Celsius and Fahrenheit
```

### Medium (Moderate execution - 2-4 minutes)
```
Create a Python script that organizes files by type in a directory
```

```
Build a CLI tool for managing a simple todo list with persistence
```

```
Develop a decorator for memoization and caching function results
```

### Complex (Longer execution - 4-6 minutes)
```
Create a Python web scraper that extracts data from a website and saves to CSV
```

```
Build a REST API for a todo management system with CRUD operations
```

```
Develop a command-line note-taking application with full search functionality
```

---

## ✅ Demo Checklist

Before you start:
- [ ] Terminal font is 18pt or larger
- [ ] Browser zoomed to 125-150%
- [ ] API key is set: `echo $OPENAI_API_KEY`
- [ ] Virtual environment activated: `source .venv/bin/activate`
- [ ] Project directory correct: `pwd` shows `/Users/parthkalkar/Desktop/todo-ai-agent`
- [ ] Internet connection stable
- [ ] Quiet room (for recording audio)
- [ ] Recording software ready (QuickTime or OBS)
- [ ] Enough disk space: `df -h | head -3`
- [ ] No other applications consuming resources

---

## 🎬 Ready to Record?

### Start with this sequence:

```bash
# Step 1: Prepare terminal
cd /Users/parthkalkar/Desktop/todo-ai-agent
clear

# Step 2: Show help (optional)
python -m agent.runner --help

# Step 3: Start recording (hit record button now)

# Step 4: Run the demo
source .venv/bin/activate
python -m agent.runner --mode confirm --persist
```

Then in browser:
```
1. Open http://127.0.0.1:8000
2. Click "Launch Agent"
3. Enter your chosen goal
4. Watch the demo play out
```

---

**Copy commands from above, paste in terminal, and demonstrate! Good luck! 🎬**
