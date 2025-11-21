# 🔌 API Reference

## Overview

The Agent-Driven TODO Executor provides a comprehensive REST API for programmatic access to all agent capabilities. The API is built with FastAPI and supports both synchronous and asynchronous operations with real-time streaming via Server-Sent Events.

**Base URL**: `http://localhost:8000`
**Authentication**: None (development) - OAuth 2.0 planned for production
**Content-Type**: `application/json`

## Core Endpoints

### POST `/run`

Execute an agent run with goal planning and task execution.

**Request Body**:
```json
{
  "goal": "Build a REST API for user management",
  "max_steps": 10,
  "mode": "confirm",
  "model": "gpt-4o-mini",
  "auto_confirm": false
}
```

**Parameters**:
- `goal` (string, required): The goal to achieve
- `max_steps` (integer, optional): Maximum tasks to execute (default: 10)
- `mode` (string, optional): Execution mode - "auto" or "confirm" (default: "confirm")
- `model` (string, optional): OpenAI model to use (default: from env)
- `auto_confirm` (boolean, optional): Skip confirmation prompts (default: false)

**Response**: Server-Sent Events stream

**Example Request**:
```bash
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Create a Python script to analyze CSV data",
    "max_steps": 5,
    "mode": "auto",
    "model": "gpt-4o-mini"
  }'
```

### POST `/confirm`

Confirm or reject pending task execution in confirmation mode.

**Request Body**:
```json
{
  "action": "approve",
  "task_id": "task-123",
  "feedback": "Looks good, proceed"
}
```

**Parameters**:
- `action` (string, required): "approve" or "reject"
- `task_id` (string, required): ID of the task to confirm
- `feedback` (string, optional): Additional feedback or rejection reason

**Response**:
```json
{
  "status": "confirmed",
  "task_id": "task-123",
  "message": "Task execution approved"
}
```

### POST `/undo`

Undo the last completed task and rollback state.

**Request Body**:
```json
{
  "task_id": "task-123",
  "reason": "Made an error in implementation"
}
```

**Parameters**:
- `task_id` (string, required): ID of task to undo
- `reason` (string, optional): Reason for undo operation

**Response**:
```json
{
  "status": "undone",
  "task_id": "task-123",
  "previous_state": {
    "status": "pending",
    "completed_at": null
  }
}
```

### GET `/status`

Get current execution status and circuit breaker state.

**Response**:
```json
{
  "status": "idle",
  "current_task": null,
  "circuit_breaker": {
    "state": "closed",
    "failure_count": 0,
    "last_failure_time": null
  },
  "active_runs": 0
}
```

### GET `/metrics`

Get comprehensive system metrics and performance data.

**Response**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime_seconds": 3600,
  "total_runs": 25,
  "successful_runs": 23,
  "failed_runs": 2,
  "average_execution_time": 45.2,
  "cache_stats": {
    "hits": 150,
    "misses": 75,
    "hit_rate": 0.667
  },
  "model_usage": {
    "gpt-4o": 15,
    "gpt-4o-mini": 10
  },
  "error_breakdown": {
    "api_timeout": 1,
    "json_parse_error": 1
  },
  "circuit_breaker": {
    "state": "closed",
    "total_failures": 2,
    "total_recoveries": 2
  }
}
```

### GET `/health`

Basic health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Streaming Events

The `/run` endpoint returns a stream of Server-Sent Events. Each event contains JSON data with the following structure:

```javascript
// Event format
event: event_type
data: {"key": "value", ...}

// Example events
event: planning_start
data: {"message": "Starting goal analysis..."}

event: todo_generated
data: {"todos": [...]}

event: task_start
data: {"task_id": "task-1", "title": "Set up project structure"}

event: progress
data: {"task_id": "task-1", "progress": 50, "message": "Installing dependencies..."}

event: task_complete
data: {"task_id": "task-1", "status": "completed", "reflection": "..."}

event: confirmation_required
data: {"task_id": "task-2", "title": "Implement authentication", "description": "..."}

event: run_complete
data: {"status": "success", "total_tasks": 5, "completed_tasks": 5}

event: error
data: {"error": "API rate limit exceeded", "retry_after": 60}
```

## Event Types

### Planning Events
- `planning_start`: Goal analysis begins
- `todo_generated`: TODO list created
- `planning_complete`: Planning phase finished

### Execution Events
- `task_start`: Task execution begins
- `progress`: Progress update (0-100%)
- `task_complete`: Task finished successfully
- `task_failed`: Task execution failed
- `reflection_generated`: LLM reflection completed

### Interaction Events
- `confirmation_required`: User confirmation needed
- `confirmation_received`: User response processed

### System Events
- `run_complete`: Entire run finished
- `error`: Error occurred
- `circuit_breaker_open`: Circuit breaker activated
- `circuit_breaker_closed`: Circuit breaker recovered

## Error Handling

All endpoints return appropriate HTTP status codes and error responses:

```json
{
  "error": "validation_error",
  "message": "Invalid goal parameter",
  "details": {
    "goal": "Goal cannot be empty"
  }
}
```

**Common Error Codes**:
- `400`: Bad Request - Invalid parameters
- `422`: Unprocessable Entity - Validation errors
- `429`: Too Many Requests - Rate limited
- `500`: Internal Server Error - Server issues
- `503`: Service Unavailable - Circuit breaker open

## Rate Limiting

- **Global Limit**: 100 requests per minute
- **Per IP**: 50 requests per minute
- **Run Endpoint**: 5 concurrent runs maximum

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## SDK Examples

### Python Client

```python
import httpx
import json

class AgentClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def run_agent(self, goal, mode="confirm", model="gpt-4o-mini"):
        """Run agent with streaming response"""
        payload = {
            "goal": goal,
            "mode": mode,
            "model": model
        }

        async with self.client.stream(
            "POST",
            f"{self.base_url}/run",
            json=payload,
            headers={"Accept": "text/event-stream"}
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    yield data

    async def confirm_task(self, task_id, action="approve"):
        """Confirm pending task"""
        payload = {"action": action, "task_id": task_id}
        response = await self.client.post(f"{self.base_url}/confirm", json=payload)
        return response.json()

    async def get_metrics(self):
        """Get system metrics"""
        response = await self.client.get(f"{self.base_url}/metrics")
        return response.json()

# Usage example
async def main():
    client = AgentClient()

    # Run agent
    async for event in client.run_agent("Build a weather app"):
        print(f"Event: {event.get('event')}")
        if event.get('event') == 'confirmation_required':
            await client.confirm_task(event['task_id'])
```

### JavaScript Client

```javascript
class AgentAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    async *runAgent(goal, options = {}) {
        const payload = {
            goal,
            mode: options.mode || 'confirm',
            model: options.model || 'gpt-4o-mini',
            max_steps: options.maxSteps || 10
        };

        const response = await fetch(`${this.baseURL}/run`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream'
            },
            body: JSON.stringify(payload)
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    yield data;
                }
            }
        }
    }

    async confirmTask(taskId, action = 'approve', feedback = '') {
        const response = await fetch(`${this.baseURL}/confirm`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, task_id: taskId, feedback })
        });
        return response.json();
    }

    async getMetrics() {
        const response = await fetch(`${this.baseURL}/metrics`);
        return response.json();
    }
}

// Usage example
async function runAgent() {
    const api = new AgentAPI();

    for await (const event of api.runAgent('Create a blog website')) {
        console.log('Event:', event.event, event);

        if (event.event === 'confirmation_required') {
            await api.confirmTask(event.task_id, 'approve');
        }
    }
}
```

## Webhook Integration

Set up webhooks for asynchronous notifications:

```json
{
  "url": "https://your-app.com/webhook",
  "events": ["run_complete", "error"],
  "secret": "your-webhook-secret"
}
```

Webhook payload example:
```json
{
  "event": "run_complete",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "run_id": "run-123",
    "status": "success",
    "goal": "Build a REST API",
    "total_tasks": 5,
    "completed_tasks": 5,
    "execution_time": 42.3
  }
}
```

## Production Considerations

### Scaling
- Use load balancer for multiple instances
- Implement Redis for session storage
- Add database for persistent state
- Use message queues for background processing

### Security
- Enable HTTPS/TLS
- Implement authentication
- Add request signing
- Rate limiting and throttling
- Input validation and sanitization

### Monitoring
- Log all API requests
- Monitor response times
- Track error rates
- Set up alerts for failures
- Use distributed tracing

This API provides complete programmatic access to all agent capabilities with real-time streaming, comprehensive error handling, and production-ready features.