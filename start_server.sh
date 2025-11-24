#!/bin/bash
# Start the todo-ai-agent web server with API key configured

set -a
source .env 2>/dev/null || echo "Note: .env file not found, using OPENAI_API_KEY from environment"
set +a

cd "$(dirname "$0")" || exit
source .venv/bin/activate
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
