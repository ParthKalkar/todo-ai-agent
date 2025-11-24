import asyncio
import json
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
import sys
import logging
import hashlib
from typing import Dict, Any
import time
import uuid

# Import database module
from server.database import (
    init_db, create_run, update_run_status, add_task, update_task, 
    add_event, get_run, get_run_tasks, delete_run
)

# Simple in-memory cache for LLM responses
llm_cache: Dict[str, str] = {}
CACHE_TTL = 3600  # 1 hour

# Circuit breaker for LLM calls
circuit_breaker = {
    'failures': 0,
    'last_failure': 0,
    'threshold': 5,  # Open after 5 failures
    'timeout': 300,  # 5 minutes timeout
    'is_open': False
}

def get_cache_key(text: str, model: str) -> str:
    """Generate a cache key for LLM responses."""
    content = f"{model}:{text}"
    return hashlib.md5(content.encode()).hexdigest()

def get_cached_response(cache_key: str) -> str | None:
    """Get cached response if it exists and is not expired."""
    # For simplicity, we'll just check if it exists (no TTL implementation)
    return llm_cache.get(cache_key)

def set_cached_response(cache_key: str, response: str):
    """Cache the LLM response."""
    llm_cache[cache_key] = response

def check_circuit_breaker() -> bool:
    """Check if circuit breaker allows the call."""
    now = time.time()
    if circuit_breaker['is_open']:
        if now - circuit_breaker['last_failure'] > circuit_breaker['timeout']:
            # Try to close the circuit
            circuit_breaker['is_open'] = False
            circuit_breaker['failures'] = 0
            return True
        return False
    return True

def record_failure():
    """Record a failure in the circuit breaker."""
    circuit_breaker['failures'] += 1
    circuit_breaker['last_failure'] = time.time()
    if circuit_breaker['failures'] >= circuit_breaker['threshold']:
        circuit_breaker['is_open'] = True

# startup-time diagnostics to ensure the server is running with the expected environment
logger = logging.getLogger("server.app")

# import agent tools
try:
    from agent.agent_tools import planner_tool, executor_tool
    from agent.persistence import save_state, load_state
    print("[startup] Agent tools imported successfully")
except Exception as e:
    print(f"[startup] ERROR: Failed to import agent tools: {e}")
    import traceback
    traceback.print_exc()
    planner_tool = None
    executor_tool = None
    save_state = None
    load_state = None

app = FastAPI(title="Agent Stream UI")


@app.on_event("startup")
async def _startup_checks():
    """Log environment details and whether LangChain is importable so debugging is easier.

    This helps avoid mismatches where the editor venv differs from the server process venv.
    """
    import os
    
    # Initialize database
    try:
        init_db()
        print("[startup] Database initialized")
    except Exception as e:
        print(f"[startup] ERROR initializing database: {e}")
    
    try:
        logger.info(f"Python executable: {sys.executable}")
        # also print to stdout/stderr so uvicorn logs capture it regardless of logger config
        print(f"[startup] Python executable: {sys.executable}")
    except Exception:
        pass
    
    # Check API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        print(f"[startup] OPENAI_API_KEY is set (length: {len(api_key)})")
    else:
        print(f"[startup] WARNING: OPENAI_API_KEY not set in environment")
    
    # Check LangChain availability
    try:
        import pkgutil
        has_lc = pkgutil.find_loader('langchain') is not None
    except Exception:
        has_lc = False
    logger.info(f"LangChain available: {has_lc}")
    print(f"[startup] LangChain available: {has_lc}")

# mount static directory
app.mount("/static", StaticFiles(directory="server/static"), name="static")
# serve preview folder at /preview if present
try:
    import os
    if os.path.isdir("preview"):
        app.mount("/preview", StaticFiles(directory="preview"), name="preview")
except Exception:
    pass

# simple in-memory broadcast queue
# This is a list of active stream listeners
# Instead of using asyncio.Queue (which has event loop issues), we use simple events
broadcast_listeners = []


async def _get_or_create_queue():
    """Get the current event loop's queue for broadcasting."""
    loop = asyncio.get_event_loop()
    # Create a unique queue per request to avoid cross-loop issues
    queue = asyncio.Queue()
    return queue


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("server/static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


# Metrics collection
metrics = {
    'runs_started': 0,
    'runs_completed': 0,
    'runs_failed': 0,
    'tasks_executed': 0,
    'llm_calls': 0,
    'cache_hits': 0,
    'errors': 0
}

@app.get("/metrics")
async def get_metrics():
    """Get basic metrics for monitoring."""
    return {
        "runs": {
            "started": metrics['runs_started'],
            "completed": metrics['runs_completed'],
            "failed": metrics['runs_failed'],
            "success_rate": (metrics['runs_completed'] / max(metrics['runs_started'], 1)) * 100
        },
        "tasks": {
            "executed": metrics['tasks_executed']
        },
        "llm": {
            "calls": metrics['llm_calls'],
            "cache_hits": metrics['cache_hits'],
            "cache_hit_rate": (metrics['cache_hits'] / max(metrics['llm_calls'], 1)) * 100
        },
        "system": {
            "errors": metrics['errors'],
            "circuit_breaker_open": circuit_breaker['is_open']
        }
    }


@app.get("/runs")
async def get_runs():
    """Get all runs from the database."""
    from server.database import get_all_runs
    try:
        runs = get_all_runs()
        return {"ok": True, "runs": runs}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/confirm")
async def confirm_plan(request: Request):
    """Handle user confirmation for plan in confirm mode.
    
    Body: {"action": "approve|edit|regenerate|cancel", "run_id": "..."}
    """
    try:
        body = await request.json()
        action = body.get('action')
        # Try to find the run_id from confirmation_state (most recent if not provided)
        run_id = body.get('run_id')
        
        if not action:
            return {"ok": False, "error": "No action provided"}
        
        # If no run_id provided, use the most recent confirmation
        if not run_id:
            with confirmation_lock:
                if confirmation_state:
                    run_id = list(confirmation_state.keys())[-1]  # Get last run_id
        
        if not run_id:
            return {"ok": False, "error": "No run_id found"}
        
        # Store the user's action in confirmation state
        with confirmation_lock:
            if run_id in confirmation_state:
                confirmation_state[run_id]["action"] = action
                return {"ok": True, "message": f"Confirmation '{action}' received for run {run_id}"}
            else:
                return {"ok": False, "error": f"No pending confirmation for run {run_id}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/run/{run_id}")
async def get_run_details(run_id: str):
    """Get details for a specific run including tasks."""
    from server.database import get_run, get_run_tasks, get_run_events
    try:
        run = get_run(run_id)
        if not run:
            return {"ok": False, "error": "Run not found"}
        tasks = get_run_tasks(run_id)
        events = get_run_events(run_id)
        return {"ok": True, "run": run, "tasks": tasks, "events": events}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _sync_background_run(run_id: str, goal: str, max_steps: int = 6, mode: str = "auto", model: str | None = None):
    """Synchronous wrapper to run the async background task."""
    print(f"[_sync_background_run] Wrapper called with run_id={run_id}, goal='{goal}'", flush=True, file=sys.stderr)
    try:
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_background_run(run_id, goal, max_steps, mode, model))
        finally:
            loop.close()
    except Exception as e:
        print(f"[_sync_background_run] ERROR: {e}", flush=True, file=sys.stderr)
        import traceback
        traceback.print_exc()
        update_run_status(run_id, 'failed', str(e))

@app.post("/run")
async def run_goal(request: Request, background: BackgroundTasks):
    """Start an agent run in background for the provided goal.

    Body: {"goal": "...", "max_steps": 6, "mode": "auto|confirm"}
    """
    body = await request.json()
    goal = body.get('goal')
    max_steps = int(body.get('max_steps', 6))
    mode = body.get('mode', 'auto')
    model = body.get('model')

    if not goal:
        return {"error": "no goal provided"}

    # Generate run ID
    run_id = str(uuid.uuid4())
    
    # Create run record in database
    create_run(run_id, goal, model, mode)
    
    # Clear old stream events (by clearing the buffer for this session)
    global event_buffer
    event_buffer.clear()
    
    # Schedule background runner using BackgroundTasks with sync wrapper
    background.add_task(_sync_background_run, run_id, goal, max_steps, mode, model)
    return {"ok": True, "message": "run started", "run_id": run_id}


# Global event buffer and lock for thread-safe broadcasting
import threading
event_buffer = []
event_lock = threading.Lock()
event_condition = threading.Condition(event_lock)

# Global confirmation state for confirm mode
confirmation_state: Dict[str, Dict[str, Any]] = {}  # {run_id: {"action": "approve"|"edit"|"regenerate"|"cancel"}}
confirmation_lock = threading.Lock()


async def _broadcast(event: dict):
    """Broadcast an event to all connected stream listeners."""
    print(f"[broadcast] Broadcasting event: {event.get('type')}")
    with event_condition:
        event_buffer.append(event)
        event_condition.notify_all()
    # Give other tasks a chance to run
    await asyncio.sleep(0)


async def _background_run(run_id: str, goal: str, max_steps: int = 6, mode: str = "auto", model: str | None = None):
    """Background run that calls planner_tool and executor_tool and broadcasts events."""
    metrics['runs_started'] += 1
    msg = f"[_background_run] Starting with run_id={run_id}, goal='{goal}', mode={mode}, model={model}"
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)
    try:
        await _broadcast({"type": "run.start", "text": f"Starting run for goal: {goal}", "mode": mode, "model": model})

        # If a specific model was provided, set it for this run so planner/executor pick it
        if model:
            import os
            os.environ['OPENAI_MODEL'] = model
            print(f"[_background_run] Set OPENAI_MODEL to {model}")

        # Initialize plan variable before planner block
        plan = []

        # planner
        print(f"[_background_run] Calling planner_tool...", flush=True, file=sys.stderr)
        print(f"[_background_run] Calling planner_tool...", flush=True)
        if planner_tool:
            try:
                print(f"[_background_run] About to call planner_tool with goal: {goal[:100]}", flush=True, file=sys.stderr)
                # Use to_thread to avoid blocking the event loop
                plan_json = await asyncio.to_thread(planner_tool, goal)
                print(f"[_background_run] Planner returned successfully", flush=True, file=sys.stderr)
                print(f"[_background_run] Planner returned: {plan_json[:200]}...")
                try:
                    plan = json.loads(plan_json)
                except Exception as e:
                    print(f"[_background_run] JSON parse error: {e}", flush=True, file=sys.stderr)
                    plan = plan_json
                print(f"[_background_run] About to broadcast plan", flush=True, file=sys.stderr)
                await _broadcast({"type": "plan", "text": "Planner produced a plan.", "plan": plan})
                print(f"[_background_run] Plan broadcast complete", flush=True, file=sys.stderr)
            except Exception as e:
                print(f"[_background_run] Planner error: {e}", flush=True, file=sys.stderr)
                import traceback
                traceback.print_exc()
                await _broadcast({"type": "plan", "text": f"Planner error: {str(e)}"})
        else:
            print(f"[_background_run] planner_tool is None!", flush=True, file=sys.stderr)
            await _broadcast({"type": "plan", "text": "Planner not available."})

        # In confirm mode, wait for user approval before executing
        if mode == "confirm" and isinstance(plan, list):
            # Initialize confirmation state for this run
            with confirmation_lock:
                confirmation_state[run_id] = {"action": None, "plan": plan}
            
            await _broadcast({"type": "plan.confirm", "text": "Please review the plan and choose: approve, edit, regenerate, or cancel.", "plan": plan})
            
            # Wait for confirmation response with timeout
            confirmed = False
            confirmation_wait = 0
            user_action = None
            while not confirmed and confirmation_wait < 300:  # 5 minute timeout
                # Check if user has submitted a confirmation
                with confirmation_lock:
                    if run_id in confirmation_state and confirmation_state[run_id]["action"]:
                        user_action = confirmation_state[run_id]["action"]
                        confirmed = True
                        break
                
                # Wait before checking again
                await asyncio.sleep(0.5)
                confirmation_wait += 1
            
            # Handle user action
            if user_action == "approve":
                await _broadcast({"type": "plan.approved", "text": "Plan approved. Starting execution."})
            elif user_action == "cancel":
                await _broadcast({"type": "run.complete", "text": "Run cancelled by user.", "status": "cancelled"})
                update_run_status(run_id, 'cancelled', 'User cancelled')
                with confirmation_lock:
                    del confirmation_state[run_id]
                return
            elif user_action == "regenerate":
                await _broadcast({"type": "plan.regenerating", "text": "Regenerating plan..."})
                # TODO: Implement plan regeneration
                await _broadcast({"type": "run.complete", "text": "Plan regeneration not yet implemented.", "status": "pending"})
                with confirmation_lock:
                    del confirmation_state[run_id]
                return
            elif user_action == "edit":
                await _broadcast({"type": "plan.edit_pending", "text": "Plan editing not yet implemented."})
                # TODO: Implement plan editing
                await _broadcast({"type": "run.complete", "text": "Plan editing not yet implemented.", "status": "pending"})
                with confirmation_lock:
                    del confirmation_state[run_id]
                return
            elif confirmation_wait >= 300:
                await _broadcast({"type": "run.complete", "text": "Confirmation timeout.", "status": "timeout"})
                update_run_status(run_id, 'timeout', 'User confirmation timeout')
                with confirmation_lock:
                    del confirmation_state[run_id]
                return
            
            # Clean up confirmation state
            with confirmation_lock:
                if run_id in confirmation_state:
                    del confirmation_state[run_id]

        steps = 0
        total_tasks = len(plan) if isinstance(plan, list) else 0
        if isinstance(plan, list):
            for i, task in enumerate(plan):
                if steps >= max_steps:
                    break
                
                # Send progress update
                progress = int((i / total_tasks) * 100) if total_tasks > 0 else 0
                await _broadcast({
                    "type": "progress", 
                    "text": f"Processing task {i+1} of {total_tasks}", 
                    "progress": progress,
                    "current_task": task.get('title')
                })
                
                # Store task in database
                add_task(run_id, task.get('id'), task.get('title'), task.get('description'))
                add_event(run_id, 'task.start', {"task_id": task.get('id'), "title": task.get('title')})
                
                await _broadcast({"type": "task.start", "text": f"Selected task #{task.get('id')}: {task.get('title')}", "task": task, "trace": {
                    "task_id": task.get('id'),
                    "title": task.get('title'),
                    "status": "in-progress",
                    "description": task.get('description', '')
                }})
                # call executor_tool (asynchronous)
                if executor_tool:
                    try:
                        res_json = await executor_tool(json.dumps(task))
                        try:
                            res = json.loads(res_json)
                        except Exception:
                            res = res_json
                        metrics['tasks_executed'] += 1
                        # Update task in database
                        update_task(run_id, task.get('id'), 'completed', 
                                   json.dumps(res), res.get('reflection', ''))
                        add_event(run_id, 'task.result', {"task_id": task.get('id'), "result": res})
                    except Exception as e:
                        res = {"error": str(e)}
                        metrics['errors'] += 1
                        update_task(run_id, task.get('id'), 'failed', json.dumps(res), str(e))
                        add_event(run_id, 'task.error', {"task_id": task.get('id'), "error": str(e)})
                else:
                    res = {"error": "executor not available"}
                    update_task(run_id, task.get('id'), 'failed', json.dumps(res), 'executor not available')

                await _broadcast({"type": "task.result", "text": f"Task {task.get('id')} result", "result": res, "trace": {
                    "task_id": task.get('id'),
                    "title": task.get('title'),
                    "status": res.get('status', 'done'),
                    "description": task.get('description', '')
                }})

                # Generate preview event - show results for any task
                title = task.get('title', 'Task Result')
                result_content = res.get('result', res.get('reflection', 'Task completed'))
                
                # Check if result looks like HTML
                result_str = str(result_content) if result_content else ''
                is_html = '<html' in result_str.lower() or '<body' in result_str.lower() or '<!doctype' in result_str.lower()
                is_python_code = result_str.strip().startswith(('def ', 'class ', 'import ', 'from ', '@app', '@router', 'async def'))
                
                if is_html:
                    # If it's HTML, render it directly with proper document structure
                    preview_html = result_str
                else:
                    # Check if it's Python code
                    if is_python_code:
                        # Format Python code nicely with syntax highlighting
                        preview_html = f"""<div style="padding: 20px; font-family: 'Courier New', monospace; line-height: 1.4; max-width: 800px; background: #f5f5f5;">
    <h2 style="margin-top: 0; color: #333; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">{title}</h2>
    <div style="background: #1e1e1e; color: #d4d4d4; padding: 20px; border-radius: 8px; overflow-x: auto; border: 1px solid #333;">
        <pre style="margin: 0; font-size: 13px; white-space: pre-wrap; word-wrap: break-word;">{result_str}</pre>
    </div>
    <div style="background: #e8f4f8; padding: 12px; border-radius: 6px; margin-top: 15px; font-size: 12px; color: #555; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <strong>Task ID:</strong> {task.get('id')} | <strong>Status:</strong> Code Generated | <strong>Lines:</strong> {len(result_str.split(chr(10)))}
    </div>
</div>"""
                    else:
                        # Otherwise, wrap the result in a simple HTML container (not a full document)
                        # This way the frontend will show it in the Preview column
                        preview_html = f"""<div style="padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 600px;">
    <h2 style="margin-top: 0; color: #333;">{title}</h2>
    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; margin: 15px 0;">
        <h4 style="margin-top: 0; color: #666;">Task Result:</h4>
        <p style="white-space: pre-wrap; word-wrap: break-word; color: #333; margin: 0;">{result_str[:500]}{'...' if len(result_str) > 500 else ''}</p>
    </div>
    <div style="background: #e8f4f8; padding: 12px; border-radius: 6px; margin-top: 15px; font-size: 13px; color: #555;">
        <strong>Task ID:</strong> {task.get('id')} | <strong>Status:</strong> Completed
    </div>
</div>"""
                
                await _broadcast({"type": "preview", "text": f"Preview for: {title}", "preview": "html", "html": preview_html})

                steps += 1

        await _broadcast({"type": "run.complete", "text": "Run complete."})
        update_run_status(run_id, 'completed')
        metrics['runs_completed'] += 1
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"[error] Background run failed: {error_msg}")
        await _broadcast({"type": "run.error", "text": str(e), "error_detail": error_msg})
        metrics['runs_failed'] += 1
        metrics['errors'] += 1


@app.get("/stream")
async def stream():
    """Stream events to client via Server-Sent Events."""
    print("[stream] New client connected")
    
    async def event_generator():
        last_index = 0
        empty_count = 0
        
        while True:
            # Check if there are new events
            with event_condition:
                current_buffer_len = len(event_buffer)
                if last_index < current_buffer_len:
                    empty_count = 0  # Reset counter when we get events
                    # Send all new events
                    for i in range(last_index, current_buffer_len):
                        payload = event_buffer[i]
                        last_index += 1
                        event_type = payload.get('type')
                        print(f"[stream] Sending event {i}: {event_type}")
                        yield {
                            "event": "message",
                            "id": None,
                            "retry": None,
                            "data": json.dumps(payload),
                        }
                else:
                    empty_count += 1
                    # Wait for notification with timeout, but don't close the connection
                    event_condition.wait(timeout=2.0)
            
            # Yield control to avoid blocking
            await asyncio.sleep(0.05)

    return EventSourceResponse(event_generator())
