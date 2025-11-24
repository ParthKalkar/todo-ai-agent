from dataclasses import dataclass, asdict
from typing import List
import os
import random
import json
import re

from dotenv import load_dotenv
load_dotenv()

import sys
print(f"[planner.py] Python executable: {sys.executable}")
try:
    import langchain
    print("[planner.py] LangChain import: OK")
except Exception as e:
    print(f"[planner.py] LangChain import: FAILED: {e}")

try:
    # optional LangChain/OpenAI imports
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import PromptTemplate
    _HAS_LC = True
except Exception as e:
    print(f"[planner.py] LangChain detailed import error: {e}")
    _HAS_LC = False


@dataclass
class Task:
    id: int
    title: str
    description: str
    status: str = "not-started"  # not-started | in-progress | done | failed | needs-follow-up


def _generate_with_llm(goal: str) -> List[Task]:
    """Use LangChain+OpenAI to generate a JSON array of tasks.

    Expected JSON format: [{"id":1,"title":"...","description":"..."}, ...]
    """
    if not _HAS_LC:
        raise RuntimeError("LangChain not available")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    # model selection: prefer explicit OPENAI_MODEL, else choose from OPENAI_MODELS or defaults
    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o")
    if model_name.lower() in ["random", "random model"]:
        models_env = os.environ.get("OPENAI_MODELS")
        if models_env:
            models = [m.strip() for m in models_env.split(',') if m.strip()]
        else:
            models = ["gpt-5.1", "gpt-4.1-mini", "gpt-5-mini"]
        model_name = random.choice(models)

    llm = ChatOpenAI(temperature=0, model_name=model_name)
    prompt = PromptTemplate(
        input_variables=["goal"],
        template=(
            "You are an assistant that converts a high-level project goal into a concise, structured "
            "TODO list. Respond with a JSON array of objects with keys: id (int), title (string), description (string). "
            "Do not include any extra text. Goal: {goal}"
        ),
    )
    
    # Check cache first
    cache_key = f"{model_name}:{goal}"
    try:
        from server.app import get_cache_key, get_cached_response, set_cached_response
        cache_key = get_cache_key(goal, model_name)
        cached_result = get_cached_response(cache_key)
        if cached_result:
            print(f"[CACHE] Using cached result for goal: {goal[:50]}...")
            return [Task(int(i.get("id", idx + 1)), i.get("title", ""), i.get("description", "")) for idx, i in enumerate(json.loads(cached_result))]
    except ImportError:
        pass  # Cache not available
    
    chain = prompt | llm
    resp = chain.invoke({"goal": goal}).content

    # Cache the raw response
    try:
        set_cached_response(cache_key, resp)
    except Exception:
        pass  # Cache not available

    # try to extract JSON from response
    m = re.search(r"```json\s*(\[.*\])\s*```", resp, re.DOTALL)
    if not m:
        # fallback: try to find just the array
        m = re.search(r"\[\s*\{.*\}\s*\]", resp, re.DOTALL)
        if not m:
            # fallback: try to parse the whole text
            data_text = resp
        else:
            data_text = m.group(0)
    else:
        data_text = m.group(1)

    try:
        items = json.loads(data_text)
        tasks = [Task(int(i.get("id", idx + 1)), i.get("title", ""), i.get("description", "")) for idx, i in enumerate(items)]
        return tasks
    except Exception:
        raise


def generate_todo_list(goal: str) -> List[Task]:
    """Produce a structured TODO list from a high-level goal.

    If an OpenAI API key and LangChain are available, use the LLM to produce a richer plan. Otherwise fall back to a deterministic generator.
    """
    goal = goal.strip()
    if not goal:
        return []

    # Always use the LLM to generate the plan per new requirement.
    if not _HAS_LC:
        raise RuntimeError("LangChain is required for LLM-only mode. Install langchain and try again.")
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY must be set for LLM-only mode.")

    return _generate_with_llm(goal)


def tasks_to_dicts(tasks: List[Task]):
    return [asdict(t) for t in tasks]


if __name__ == "__main__":
    # quick demo
    for t in generate_todo_list("Build a small CLI with confirm and auto modes"):
        print(f"{t.id}. {t.title} — {t.description} [{t.status}]")
