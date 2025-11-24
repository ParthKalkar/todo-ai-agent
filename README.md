# 🤖 Agent-Driven TODO Executor

A production-ready AI agent system that transforms high-level goals into structured TODO lists, executes tasks with real-time progress tracking, and provides enterprise-grade reliability features.

![Python](https://img.shields.io/badge/python-3.12+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green) ![LangChain](https://img.shields.io/badge/LangChain-0.1+-orange)

## ✨ Key Features

### 🎯 Core Functionality
- **Intelligent Planning**: LLM-powered TODO list generation from natural language goals
- **Dual Execution Modes**: Confirm mode (user approval required) and Auto mode (immediate execution)
- **Real-time Execution**: Sequential task processing with live status updates
- **Complete Traceability**: Full logging of decisions, actions, and reflections

### 🚀 Production-Grade Enhancements
- **Circuit Breaker Pattern**: Automatic fault tolerance for LLM service failures
- **Smart Progress Tracking**: Visual progress bars with real-time completion percentages
- **Undo System**: One-click task reversion for error recovery
- **Intelligent Caching**: Response caching to reduce API costs and improve performance
- **Theme Toggle**: Professional dark/light mode with persistence
- **Metrics Dashboard**: Real-time system monitoring and analytics
- **Enhanced Error Handling**: Exponential backoff, graceful degradation, and retry logic

### 🎨 Modern User Experience
- **Streaming Web UI**: Real-time event streaming with Server-Sent Events
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Rich Status Indicators**: Visual feedback with contextual icons and messages
- **Interactive Controls**: Plan review, approval, editing, and cancellation

## 📖 Documentation

### Getting Started
- **[RUNNING_INSTRUCTIONS.md](RUNNING_INSTRUCTIONS.md)** ⭐ **START HERE** - Complete setup and usage guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture and system design
- **[FEATURES.md](FEATURES.md)** - Comprehensive feature showcase
- **[API.md](API.md)** - API reference and examples

## 🏃 Quick Start

### Prerequisites
- Python 3.12+
- OpenAI API key (get from https://platform.openai.com/api-keys)

### Installation

1. **Clone and setup environment:**
```bash
git clone https://github.com/ParthKalkar/todo-ai-agent.git
cd todo-ai-agent
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure API key:**
```bash
# Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

4. **Start the web application:**
```bash
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
```

5. **Open your browser:**
```
http://127.0.0.1:8000
```

## 🎬 Demo Videos

Click on any demo below to download and watch:

| Mode | Web UI | CLI |
|------|--------|-----|
| **Confirm Mode** <br/> (user approval) | [📹 Download Demo](https://github.com/ParthKalkar/todo-ai-agent/raw/main/demo_webUI_confirm_mode_fast.mp4) | [📹 Download Demo](https://github.com/ParthKalkar/todo-ai-agent/raw/main/demo_cli_confirm_mode_fast.mp4) |
| **Auto Mode** <br/> (instant execution) | [📹 Download Demo](https://github.com/ParthKalkar/todo-ai-agent/raw/main/demo_webUI_auto_mode_fast.mp4) | [📹 Download Demo](https://github.com/ParthKalkar/todo-ai-agent/raw/main/demo_cli_auto_mode_fast.mp4) |

**Video Details:**
- Web UI Confirm Mode: 1.7 MB
- Web UI Auto Mode: 640 KB
- CLI Confirm Mode: 1.4 MB
- CLI Auto Mode: 1.7 MB

*All videos are optimized and lightweight for quick download*

## 🎮 Usage

### Web Interface (Recommended)

1. **Enter a Goal**: Type your high-level objective in the text area
2. **Choose Mode**: Select Confirm mode for approval workflow or Auto mode for immediate execution
3. **Pick Model**: Choose from available OpenAI models (gpt-4o, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-5-mini, gpt-5-nano-2025-08-07)
4. **Start Execution**: Click "Start run" to begin
5. **Monitor Progress**: Watch real-time progress bars and status updates
6. **Review Results**: Use Undo button if needed, view generated previews

### Command Line Interface

```bash
# Confirm mode (default)
python -m agent.runner --mode confirm --persist

# Auto mode
python -m agent.runner --mode auto --persist

# With UI
python -m agent.runner --mode confirm --persist --ui
```

## 📚 Documentation

For detailed information about the system:

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture and system design
- **[FEATURES.md](FEATURES.md)** - Comprehensive feature showcase and capabilities
- **[API.md](API.md)** - Complete API reference and usage examples

## 🔧 Advanced Features

### Circuit Breaker Protection
The system automatically protects against LLM service failures:
- Opens after 5 consecutive failures
- Stays open for 5 minutes to allow service recovery
- Provides fallback responses during outages

### Intelligent Caching
- Caches LLM responses to reduce API costs
- Smart cache keys based on content and model
- Automatic cache invalidation for fresh results

### Real-Time Metrics
Access system metrics at: `http://127.0.0.1:8000/metrics`

```json
{
  "runs": {
    "started": 15,
    "completed": 12,
    "failed": 3,
    "success_rate": 80.0
  },
  "tasks": {
    "executed": 45
  },
  "llm": {
    "calls": 67,
    "cache_hits": 23,
    "cache_hit_rate": 34.3
  },
  "system": {
    "errors": 2,
    "circuit_breaker_open": false
  }
}
```

### Theme System
- **Dark Mode**: Professional dark theme (default)
- **Light Mode**: Clean light theme
- **Persistence**: Remembers your preference
- **Smooth Transitions**: CSS transitions between themes

## 🏗️ Architecture

```
todo-ai-agent/
├── agent/                    # Core agent logic
│   ├── planner.py           # LLM-powered task planning
│   ├── executor.py          # Task execution with resilience
│   ├── agent_tools.py       # LangChain tool wrappers
│   ├── persistence.py       # JSON state management
│   ├── runner.py            # CLI interface
│   └── ui.py                # Rich TUI components
├── server/                  # Web application
│   ├── app.py              # FastAPI application with SSE
│   └── static/
│       └── index.html       # Modern web interface
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
├── .env                     # Environment configuration
└── README.md               # This file
```

### Key Components

- **Planner**: Uses GPT models to generate structured TODO lists
- **Executor**: Executes tasks with reflection and error handling
- **Web Server**: FastAPI with Server-Sent Events for real-time updates
- **Circuit Breaker**: Fault tolerance for external service dependencies
- **Cache System**: In-memory response caching for performance
- **Metrics Collector**: Real-time system monitoring

## 🎯 How the Agent Loop Works

### System Design: Chat → Plan → Confirm → Execute → Reflect

The agent system follows a structured loop that transforms user goals into executed tasks:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Provides Goal                        │
│              "Build a web scraper for news"                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           PLANNING PHASE: Goal Analysis → TODO List          │
│                                                              │
│  Agent uses GPT model to break down goal into structured   │
│  tasks with titles and descriptions. Output: JSON array.   │
│                                                              │
│  Example:                                                   │
│  [                                                          │
│    {"id": 1, "title": "Research Libraries",                │
│     "description": "Compare BeautifulSoup vs Scrapy"},     │
│    {"id": 2, "title": "Design Schema",                     │
│     "description": "Plan data structure for articles"}     │
│  ]                                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│      CONFIRMATION PHASE: User Review & Approval              │
│                                                              │
│  Confirm Mode: Shows plan, awaits user action               │
│    ▶ [approve]    - Proceed with execution                 │
│    ▶ [edit]       - Modify tasks                           │
│    ▶ [regenerate] - Create new plan                        │
│    ▶ [cancel]     - Abort                                  │
│                                                              │
│  Auto Mode: Skips this phase, proceeds immediately         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│       EXECUTION PHASE: Sequential Task Processing            │
│                                                              │
│  Loop: While unfinished tasks remain:                       │
│    1. Select first "not-started" task                      │
│    2. Execute task (simulated with deterministic logic)    │
│    3. Mark status: done | failed | needs-follow-up        │
│    4. Generate LLM reflection (1-2 sentences)             │
│    5. Save trace entry to state.json                       │
│    6. Display update in real-time UI                       │
│                                                              │
│  Status Markers:                                            │
│    ○ not-started  │  ◔ in-progress  │  ● done             │
│    ✖ failed       │  ◐ needs-follow-up                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│    REFLECTION PHASE: Summary & Persistence                   │
│                                                              │
│  For each completed task:                                   │
│    - Generate LLM-powered reflection                       │
│    - Collect in execution trace                            │
│    - Persist state to JSON for recovery                    │
│    - Display trace entry in chat/UI                        │
│                                                              │
│  Final Output: Execution Summary                            │
│    Task #1: done - Research identified BeautifulSoup...   │
│    Task #2: done - Defined JSON schema with...            │
│    Task #3: failed - Implementation needs retry...         │
└─────────────────────────────────────────────────────────────┘
```

### Example Session Transcript

```
=== Agent-Driven TODO Executor ===

User Input:
  Goal: "Build a Python web scraper that extracts news articles 
         and stores them in a database"
  Mode: Confirm
  Model: gpt-4o

[Planning Phase]
Agent: "I've created a 5-step execution plan for your goal:"

Proposed TODO List:
  [1] Research web scraping libraries (BeautifulSoup, Selenium)
      Description: Compare popular Python libraries and pick the best

  [2] Design the article data schema (title, content, URL, date)
      Description: Plan the structure for storing articles

  [3] Implement basic scraper with BeautifulSoup
      Description: Create scraper logic and parsing rules

  [4] Set up SQLite database for persistence
      Description: Initialize database and define tables

  [5] Test scraper with sample news website
      Description: Verify extraction accuracy and error handling

Options: [approve] [edit] [regenerate] [cancel]
User: approve

[Execution Phase - Real-time Updates]

Step 1/5: Research web scraping libraries
  Status: in-progress →
  ✓ Completed: done
  Reflection: "Evaluated BeautifulSoup (simpler) vs Selenium (JS support).
               BeautifulSoup chosen for initial implementation."

Step 2/5: Design the article data schema
  Status: in-progress →
  ✓ Completed: done
  Reflection: "Designed schema with fields: id, title, content, URL,
               published_date, source. Includes indexes for quick lookup."

Step 3/5: Implement basic scraper with BeautifulSoup
  Status: in-progress →
  ✓ Completed: done
  Reflection: "Implemented scraper with error handling. Supports CSS
               selectors and regex patterns for flexible article extraction."

Step 4/5: Set up SQLite database for persistence
  Status: in-progress →
  ✓ Completed: done
  Reflection: "Database initialized with proper schema. Added connection
               pooling and transaction management for reliability."

Step 5/5: Test scraper with sample news website
  Status: in-progress →
  ✓ Completed: done
  Reflection: "Tested against BBC News. Successfully extracted 47 articles
               with 100% accuracy. Ready for production deployment."

[Summary]

Execution Completed Successfully!
  Total Tasks: 5
  Completed: 5
  Failed: 0
  Success Rate: 100%

Execution Trace:
  Task #1: done - Evaluated BeautifulSoup...
  Task #2: done - Designed schema with fields...
  Task #3: done - Implemented scraper with error...
  Task #4: done - Database initialized with...
  Task #5: done - Tested against BBC News...

State saved to: state.json
Session duration: 2.3 seconds

User: Thank you! The tasks were well-planned and executed.
```

## 🎯 Example Workflows

### Landing Page Creation
```
Goal: "Create a beautiful landing page that captures emails and offers a 20% coupon"

1. Define Landing Page Structure
2. Design Visual Elements
3. Develop Email Capture Form
4. Add Coupon Offer Display
5. Implement Mobile Responsiveness
6. Test Conversion Funnel
```

### CLI Tool Development
```
Goal: "Build a CLI tool with confirm and auto modes"

1. Define Project Scope
2. Choose Programming Language
3. Set Up Development Environment
4. Implement Confirm Mode
5. Implement Auto Mode
6. Create User Interface
7. Add Help Command
8. Testing
9. Documentation
10. Deployment
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=agent --cov=server

# Run specific test file
python -m pytest tests/test_planner.py -v
```

## 🔮 Future Enhancements

### Immediate Roadmap
- [ ] **Task Dependencies**: Support for parallel execution and prerequisite chains
- [ ] **Pause/Resume**: Workflow interruption and continuation
- [ ] **Task Graph Visualization**: Interactive dependency graphs
- [ ] **Real-time Collaboration**: Multi-user editing and review

### Enterprise Features
- [ ] **OAuth Integration**: Secure user authentication
- [ ] **Audit Logging**: Complete action traceability
- [ ] **Database Integration**: PostgreSQL for persistence
- [ ] **Redis Caching**: External cache for scalability
- [ ] **Load Balancing**: Multi-instance deployment
- [ ] **Monitoring Stack**: Grafana/Prometheus dashboards

### Extensibility
- [ ] **Plugin Architecture**: Third-party tool integrations
- [ ] **Custom Workflows**: User-defined task templates
- [ ] **API Integrations**: GitHub, Slack, Jira connectors
- [ ] **Custom LLM Providers**: Support for Claude, Gemini, etc.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) for LLM orchestration
- Web UI powered by [FastAPI](https://fastapi.tiangolo.com/) and Server-Sent Events
- Styled with modern CSS and responsive design principles
- Inspired by production agent systems and DevOps best practices

---

**Ready to transform your goals into action?** 🚀

Start the server and visit `http://127.0.0.1:8000` to experience the future of AI-assisted task management.
