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
    """Call LLM to generate a reflection or code output about the task and outcome."""
    if not _HAS_LC:
        logger.warning("LangChain not available, using fallback reflection")
        return f"Task completed with status: {outcome}"

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not set")
        return f"Task completed with status: {outcome} (LLM unavailable)"

    # model selection: prefer explicit OPENAI_MODEL, else choose from OPENAI_MODELS or defaults
    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o")
    if model_name.lower() in ["random", "random model"]:
        models_env = os.environ.get("OPENAI_MODELS")
        if models_env:
            models = [m.strip() for m in models_env.split(',') if m.strip()]
        else:
            models = ["gpt-5.1", "gpt-5-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini"]
        model_name = random.choice(models)

    for attempt in range(max_retries):
        try:
            llm = ChatOpenAI(temperature=0, model_name=model_name, max_retries=2)
            
            # Detect if this task should generate code/HTML/UI
            title_lower = task.get('title', '').lower()
            desc_lower = task.get('description', '').lower()
            combined_text = title_lower + ' ' + desc_lower
            
            # Determine what type of output to generate
            should_generate_email_form = any(keyword in combined_text 
                                            for keyword in ['email capture', 'email form', 'email'])
            should_generate_landing_page = any(keyword in combined_text 
                                              for keyword in ['landing', 'page', 'website'])
            should_generate_ui = any(keyword in combined_text 
                                    for keyword in ['mockup', 'ui', 'interface', 'wireframe', 'prototype'])
            should_generate_api = any(keyword in combined_text 
                                     for keyword in ['api', 'endpoint', 'rest', 'fastapi', 'flask', 'backend', 'code', 'python'])
            
            if should_generate_email_form:
                # Generate actual HTML email form
                prompt = PromptTemplate(
                    input_variables=["title", "description"],
                    template=(
                        "Generate a complete, standalone HTML email capture form for a landing page. "
                        "Include HTML, CSS (in <style> tags), and JavaScript all in one file. "
                        "Make it beautiful and modern. "
                        "Title: {title}\nDescription: {description}\n\n"
                        "Return ONLY the complete HTML code, nothing else."
                    ),
                )
            elif should_generate_landing_page:
                # Generate actual HTML landing page
                prompt = PromptTemplate(
                    input_variables=["title", "description"],
                    template=(
                        "Generate a complete, standalone HTML landing page with embedded CSS and JavaScript. "
                        "Make it beautiful, modern, and professional. "
                        "Title: {title}\nDescription: {description}\n\n"
                        "Return ONLY the complete HTML code, nothing else."
                    ),
                )
            elif should_generate_ui:
                # Generate UI mockup in HTML
                prompt = PromptTemplate(
                    input_variables=["title", "description"],
                    template=(
                        "Generate a complete HTML UI mockup/prototype with modern styling. "
                        "Include HTML, CSS (in <style> tags), and any necessary JavaScript all in one file. "
                        "Make it visually appealing and professional. "
                        "Title: {title}\nDescription: {description}\n\n"
                        "Return ONLY the complete HTML code, nothing else."
                    ),
                )
            elif should_generate_api:
                # Generate Python API code example
                prompt = PromptTemplate(
                    input_variables=["title", "description"],
                    template=(
                        "Generate a complete, production-ready Python code example. "
                        "If it's FastAPI, use FastAPI. If it's Flask, use Flask. "
                        "Include all necessary imports, models, routes, and error handling. "
                        "Make it well-structured and documented. "
                        "Title: {title}\nDescription: {description}\n\n"
                        "Return ONLY the complete Python code, nothing else."
                    ),
                )
            else:
                # Standard reflection for other tasks
                prompt = PromptTemplate(
                    input_variables=["title", "description", "outcome"],
                    template=(
                        "You are an assistant that writes a concise reflection (1-2 sentences) given a task title, description, and outcome. "
                        "Return only the reflection text.\nTitle: {title}\nDescription: {description}\nOutcome: {outcome}"
                    ),
                )
            
            chain = prompt | llm
            # Determine whether to use code generation prompts or standard reflection
            if should_generate_email_form or should_generate_landing_page or should_generate_ui or should_generate_api:
                result = chain.invoke({"title": task.get('title', ''), "description": task.get('description', '')})
            else:
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
        'result': reflection,  # Also include as 'result' for preview rendering
    }
    print(f"→ result: {result['status']} — {result['reflection'][:100]}...")

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
