import os
import json
from typing import Optional

from dotenv import load_dotenv
import random

from agent.agent_tools import planner_tool, executor_tool, persistence_tool

_HAS_LC = False
try:
    # LangChain agent imports
    from langchain import OpenAI
    from langchain.agents import initialize_agent, AgentType
    from langchain.tools import Tool
    _HAS_LC = True
except Exception:
    _HAS_LC = False


def _fallback_agent_loop(goal: str, max_steps: int = 6):
    """A deterministic fallback 'agent' that uses the tools in a simple loop."""
    # Call planner to get tasks
    plan_json = planner_tool(goal)
    try:
        tasks = json.loads(plan_json)
    except Exception:
        return {"error": "planner returned invalid json"}

    trace = []
    steps = 0
    for task in tasks:
        if steps >= max_steps:
            break
        # execute task
        res_json = executor_tool(json.dumps(task))
        res = json.loads(res_json)
        trace.append({'task_id': res.get('id'), 'status': res.get('status'), 'reflection': res.get('reflection')})
        steps += 1

    # persist final state (executor already saved)
    state = json.loads(persistence_tool('load') or '{}')
    state['agent_trace'] = trace
    persistence_tool(json.dumps(state))
    return state


def run_agent(goal: str, max_steps: int = 6, use_langchain: Optional[bool] = None):
    load_dotenv()
    # Enforce LangChain/LLM usage per new requirement
    if not _HAS_LC:
        raise RuntimeError("LangChain is required for LLM-only mode. Install langchain and try again.")
    if not os.environ.get('OPENAI_API_KEY'):
        raise RuntimeError("OPENAI_API_KEY must be set for LLM-only mode.")

    # choose a random model for this agent run
    models_env = os.environ.get("OPENAI_MODELS")
    if models_env:
        models = [m.strip() for m in models_env.split(',') if m.strip()]
    else:
        models = ["gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
    model_name = random.choice(models)

    # Build tools for LangChain
    llm = OpenAI(temperature=0, model_name=model_name)

    tools = [
        Tool.from_function(planner_tool, name='planner', description='Produce a JSON TODO list from a goal'),
        Tool.from_function(executor_tool, name='executor', description='Execute a task given as JSON and return result JSON'),
        Tool.from_function(persistence_tool, name='persistence', description='Load or save state; accepts "load" or JSON string'),
    ]

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        max_iterations=max_steps,
        return_intermediate_steps=False,
        verbose=True,
    )

    # Run agent
    result = agent.run(goal)
    # After run, load persisted state and return
    state = json.loads(persistence_tool('load') or '{}')
    state['agent_result_text'] = result
    state['agent_model_used'] = model_name
    return state


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--goal', type=str, required=False, help='High-level goal to give the agent')
    parser.add_argument('--max-steps', type=int, default=6)
    args = parser.parse_args()

    if not args.goal:
        args.goal = input('Enter a high-level goal for the agent: ').strip()
    state = run_agent(args.goal, max_steps=args.max_steps)
    print('\nAgent run complete. Final state:')
    print(json.dumps(state, indent=2))
