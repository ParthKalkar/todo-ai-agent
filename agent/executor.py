import time
from typing import Dict, Any
import os
import random
import asyncio
import logging

logger = logging.getLogger(__name__)

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import PromptTemplate
    _HAS_LC = True
except Exception:
    _HAS_LC = False


def _llm_reflection(task: Dict[str, Any], outcome: str, max_retries: int = 3) -> str:
    """Call LLM to generate a short reflection about the task and outcome."""
    if not _HAS_LC:
        logger.warning("LangChain not available, using fallback reflection")
        return f"Task completed with status: {outcome}"

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not set")
        return f"Task completed with status: {outcome} (LLM unavailable)"

    # model selection: prefer explicit OPENAI_MODEL, else choose from OPENAI_MODELS or defaults
    model_name = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    if model_name == "Random model":
        models_env = os.environ.get("OPENAI_MODELS")
        if models_env:
            models = [m.strip() for m in models_env.split(',') if m.strip()]
        else:
            models = ["gpt-3.5-turbo", "gpt-4"]
        model_name = random.choice(models)

    for attempt in range(max_retries):
        try:
            llm = ChatOpenAI(temperature=0, model_name=model_name, max_retries=2)
            prompt = PromptTemplate(
                input_variables=["title", "description", "outcome"],
                template=(
                    "You are an assistant that writes a concise reflection (1-2 sentences) given a task title, description, and outcome. "
                    "Return only the reflection text.\nTitle: {title}\nDescription: {description}\nOutcome: {outcome}"
                ),
            )
            chain = prompt | llm
            result = chain.invoke({"title": task.get('title', ''), "description": task.get('description', ''), "outcome": outcome})
            return result.content
        except Exception as e:
            logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error(f"All LLM attempts failed, using fallback")
                return f"Task completed with status: {outcome} (LLM error: {str(e)})"
            # Wait before retry
            time.sleep(1 * (attempt + 1))  # Exponential backoff


async def execute_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single task (simulated).

    Returns a result dict with keys: status (done/failed/needs-follow-up), reflection.
    """
    print(f"Executing task #{task['id']}: {task['title']}")
    task['status'] = 'in-progress'
    # Simulate work
    await asyncio.sleep(0.4)

    # Simple deterministic success policy: tasks containing "fail" fail
    title = task.get('title', '').lower()
    if 'fail' in title:
        task['status'] = 'failed'
        outcome = 'Simulated failure based on title.'
    else:
        task['status'] = 'done'
        outcome = 'Completed successfully (simulated).'

    # Always use the LLM for reflection per new requirement.
    if not _HAS_LC:
        raise RuntimeError("LangChain is required for LLM-only mode. Install langchain and try again.")
    reflection = _llm_reflection(task, outcome)

    result = {
        'id': task['id'],
        'status': task['status'],
        'reflection': reflection,
    }
    print(f"→ result: {result['status']} — {result['reflection']}")

    # Optionally POST events to a local server for streaming UI if SERVER_URL is set
    try:
        server = os.environ.get('SERVER_URL')
        if server:
            import httpx
            payload = {
                'type': 'task_result',
                'task': {'id': task.get('id'), 'title': task.get('title'), 'description': task.get('description')},
                'result': result,
            }
            # fire-and-forget post
            try:
                httpx.post(f"{server.rstrip('/')}/events", json=payload, timeout=2.0)
            except Exception:
                pass
    except Exception:
        pass
    return result
