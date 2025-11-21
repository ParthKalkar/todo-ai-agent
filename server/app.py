import asyncio
import json
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
from fastapi import BackgroundTasks
import asyncio
import json
import sys
import logging
import hashlib
from typing import Dict, Any
import time

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
except Exception:
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
    try:
        logger.info(f"Python executable: {sys.executable}")
        # also print to stdout/stderr so uvicorn logs capture it regardless of logger config
        print(f"[startup] Python executable: {sys.executable}")
    except Exception:
        pass
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
broadcast_queue: asyncio.Queue = asyncio.Queue()


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

    # schedule background runner (pass mode if provided)
    background.add_task(_background_run, goal, max_steps, mode, model)
    return {"ok": True, "message": "run started"}


async def _broadcast(event: dict):
    await broadcast_queue.put(event)


async def _background_run(goal: str, max_steps: int = 6, mode: str = "auto", model: str | None = None):
    """Background run that calls planner_tool and executor_tool and broadcasts events."""
    metrics['runs_started'] += 1
    try:
        await _broadcast({"type": "run.start", "text": f"Starting run for goal: {goal}", "mode": mode, "model": model})

        # If a specific model was provided, set it for this run so planner/executor pick it
        if model:
            import os
            os.environ['OPENAI_MODEL'] = model

        # planner
        if planner_tool:
            plan_json = planner_tool(goal)
            try:
                plan = json.loads(plan_json)
            except Exception:
                plan = plan_json
            await _broadcast({"type": "plan", "text": "Planner produced a plan.", "plan": plan})
        else:
            await _broadcast({"type": "plan", "text": "Planner not available."})

        # In confirm mode, wait for user approval before executing
        if mode == "confirm" and isinstance(plan, list):
            await _broadcast({"type": "plan.confirm", "text": "Please review the plan and choose: approve, edit, regenerate, or cancel.", "plan": plan})
            
            # Wait for confirmation response
            confirmed = False
            while not confirmed:
                # Wait for confirmation event
                event = await broadcast_queue.get()
                if event.get("type") == "confirmation":
                    action = event.get("action")
                    if action == "approve":
                        await _broadcast({"type": "plan.approved", "text": "Plan approved. Starting execution."})
                        confirmed = True
                    elif action == "edit":
                        await _broadcast({"type": "plan.edit", "text": "Edit functionality not implemented in web UI yet."})
                        # For now, just continue - could implement edit logic
                        confirmed = True
                    elif action == "regenerate":
                        await _broadcast({"type": "plan.regenerate", "text": "Regenerating plan..."})
                        # Regenerate plan
                        if planner_tool:
                            plan_json = planner_tool(goal + " (regenerated)")
                            try:
                                plan = json.loads(plan_json)
                            except Exception:
                                plan = plan_json
                            await _broadcast({"type": "plan", "text": "New plan generated.", "plan": plan})
                            await _broadcast({"type": "plan.confirm", "text": "Please review the new plan.", "plan": plan})
                        else:
                            confirmed = True
                    elif action == "cancel":
                        await _broadcast({"type": "run.cancelled", "text": "Run cancelled by user."})
                        return
                # Put back other events
                elif event.get("type") != "confirmation":
                    await broadcast_queue.put(event)

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
                
                await _broadcast({"type": "task.start", "text": f"Selected task #{task.get('id')}: {task.get('title')}", "task": task})
                # call executor_tool (asynchronous)
                if executor_tool:
                    try:
                        res_json = await executor_tool(json.dumps(task))
                        try:
                            res = json.loads(res_json)
                        except Exception:
                            res = res_json
                        metrics['tasks_executed'] += 1
                    except Exception as e:
                        res = {"error": str(e)}
                        metrics['errors'] += 1
                else:
                    res = {"error": "executor not available"}

                await _broadcast({"type": "task.result", "text": f"Task {task.get('id')} result", "result": res})

                # if task title mentions landing, generate preview event
                title = (task.get('title') or '').lower()
                if 'landing' in title:
                    await _broadcast({"type": "preview", "text": "Landing preview generated", "preview": "landing"})

                steps += 1

        await _broadcast({"type": "run.complete", "text": "Run complete."})
        metrics['runs_completed'] += 1
    except Exception as e:
        await _broadcast({"type": "run.error", "text": str(e)})
        metrics['runs_failed'] += 1
        metrics['errors'] += 1


@app.get("/stream")
async def stream():
    async def event_generator():
        while True:
            payload = await broadcast_queue.get()
            yield {
                "event": "message",
                "id": None,
                "retry": None,
                "data": json.dumps(payload),
            }

    return EventSourceResponse(event_generator())
