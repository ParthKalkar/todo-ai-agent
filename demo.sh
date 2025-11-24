#!/bin/bash

# 🚀 Agent-Driven TODO Executor - Interactive Demo
# This script demonstrates the full capabilities of the production-ready agent system

set -e

echo "🤖 Agent-Driven TODO Executor - Production Demo"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}$(printf '%.0s=' {1..50})${NC}"
}

# Check if virtual environment exists
check_environment() {
    print_header "🔍 Environment Check"

    if [ ! -d ".venv" ]; then
        print_error "Virtual environment not found. Please run setup first."
        exit 1
    fi

    if [ ! -f ".env" ]; then
        print_error ".env file not found. Please create it with your OPENAI_API_KEY."
        exit 1
    fi

    print_success "Environment check passed"
}

# Start the server
start_server() {
    print_header "🚀 Starting Server"

    # Activate virtual environment and start server in background
    source .venv/bin/activate
    python -m uvicorn server.app:app --host 127.0.0.1 --port 8000 --log-level info &
    SERVER_PID=$!

    # Wait for server to start
    print_status "Waiting for server to start..."
    sleep 3

    # Check if server is running
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "Server started successfully on http://localhost:8000"
    else
        print_error "Server failed to start"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
}

# Run demo scenarios
run_demo_scenarios() {
    print_header "🎯 Running Demo Scenarios"

    # Demo 1: Simple goal with auto mode
    print_status "Demo 1: Simple goal with auto execution"
    echo "Goal: Create a Python script to calculate factorial"

    curl -s -X POST "http://localhost:8000/run" \
        -H "Content-Type: application/json" \
        -d '{
            "goal": "Create a Python script that calculates factorial of a number",
            "max_steps": 3,
            "mode": "auto",
            "model": "gpt-4.1-mini"
        }' > /dev/null

    print_success "Demo 1 completed"

    # Demo 2: Complex goal with confirmation mode
    print_status "Demo 2: Complex goal with confirmation mode"
    echo "Goal: Build a simple REST API for task management"

    # Start the run
    curl -s -X POST "http://localhost:8000/run" \
        -H "Content-Type: application/json" \
        -d '{
            "goal": "Build a simple REST API for task management with FastAPI",
            "max_steps": 5,
            "mode": "confirm",
            "model": "gpt-4.1-mini"
        }' > /dev/null &

    RUN_PID=$!
    sleep 2

    # Simulate user confirmation
    print_status "Simulating user confirmation for first task..."
    sleep 1

    curl -s -X POST "http://localhost:8000/confirm" \
        -H "Content-Type: application/json" \
        -d '{
            "action": "approve",
            "task_id": "task-1",
            "feedback": "Approved - proceed with API setup"
        }' > /dev/null

    wait $RUN_PID
    print_success "Demo 2 completed"

    # Demo 3: Error handling and circuit breaker
    print_status "Demo 3: Testing error handling and recovery"
    echo "Goal: Test system resilience with invalid goal"

    curl -s -X POST "http://localhost:8000/run" \
        -H "Content-Type: application/json" \
        -d '{
            "goal": "",
            "max_steps": 1,
            "mode": "auto",
            "model": "gpt-4.1-mini"
        }' > /dev/null

    print_success "Error handling test completed"
}

# Show metrics
show_metrics() {
    print_header "📊 System Metrics"

    METRICS=$(curl -s http://localhost:8000/metrics)

    echo "Current System Metrics:"
    echo "$METRICS" | python3 -m json.tool
}

# Show web UI
show_web_ui() {
    print_header "🌐 Web Interface"

    print_status "Opening web interface in browser..."
    print_status "Features to test:"
    echo "  • Goal input with model selection"
    echo "  • Real-time progress streaming"
    echo "  • Confirmation mode interactions"
    echo "  • Progress bars and status updates"
    echo "  • Undo functionality"
    echo "  • Dark/Light theme toggle"
    echo "  • Circuit breaker status"

    # Try to open browser (works on macOS)
    if command -v open &> /dev/null; then
        open http://localhost:8000
    else
        print_warning "Please open http://localhost:8000 in your browser"
    fi

    print_status "Press Enter when done exploring the web UI..."
    read
}

# Test CLI interface
test_cli() {
    print_header "💻 CLI Interface Test"

    print_status "Testing CLI with simple goal..."

    python -m agent.runner "Create a hello world script" --mode auto --max-steps 2

    print_success "CLI test completed"
}

# Cleanup
cleanup() {
    print_header "🧹 Cleanup"

    # Kill server
    if [ ! -z "$SERVER_PID" ]; then
        print_status "Stopping server..."
        kill $SERVER_PID 2>/dev/null || true
        print_success "Server stopped"
    fi

    print_success "Demo completed successfully!"
}

# Main demo flow
main() {
    trap cleanup EXIT

    check_environment
    start_server
    run_demo_scenarios
    show_metrics
    show_web_ui
    test_cli

    print_header "🎉 Demo Complete!"

    echo ""
    print_success "What you've seen:"
    echo "  ✅ Intelligent goal planning with LLM"
    echo "  ✅ Real-time streaming progress updates"
    echo "  ✅ Interactive confirmation mode"
    echo "  ✅ Circuit breaker for fault tolerance"
    echo "  ✅ Undo functionality with state rollback"
    echo "  ✅ Modern web UI with theme toggle"
    echo "  ✅ Comprehensive metrics and monitoring"
    echo "  ✅ CLI and API interfaces"
    echo "  ✅ Error handling and recovery"
    echo "  ✅ Production-grade reliability features"

    echo ""
    print_status "Next steps:"
    echo "  • Check out the README.md for detailed documentation"
    echo "  • Explore ARCHITECTURE.md for scalability roadmap"
    echo "  • Review FEATURES.md for advanced capabilities"
    echo "  • See API.md for programmatic access"
    echo "  • Run individual components for deeper testing"
}

# Run main demo
main "$@"