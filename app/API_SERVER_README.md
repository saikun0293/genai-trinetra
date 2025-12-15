# Custom API Server with ADK Agent

This document explains how to expose both the ADK agent and custom REST API endpoints together in a single server.

## Overview

The `api_server.py` module demonstrates how to:

1. **Get the base FastAPI app from ADK** - This includes all standard agent endpoints
2. **Add custom REST API endpoints** - Your own business logic endpoints
3. **Run everything together** - Single server, single port

## Architecture

```
┌─────────────────────────────────────────────┐
│         FastAPI Server (Port 8000)          │
├─────────────────────────────────────────────┤
│                                             │
│  ADK Agent Endpoints:                       │
│  ├── /run_sse (Agent streaming)             │
│  ├── /run (Agent query)                     │
│  ├── /list-apps                             │
│  ├── /apps/{app}/users/{user}/sessions      │
│  └── /docs (OpenAPI docs)                   │
│                                             │
│  Custom API Endpoints:                      │
│  ├── /health                                │
│  ├── /api/info                              │
│  ├── /api/transactions/validate             │
│  ├── /api/transactions/batch                │
│  ├── /api/transactions/{id}                 │
│  └── /api/agent/analyze                     │
│                                             │
└─────────────────────────────────────────────┘
```

## Running the Server

### Option 1: Direct Python Execution

```bash
# From project root
python -m app.api_server
```

### Option 2: Using uvicorn

```bash
# From project root
uvicorn app.api_server:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Using Makefile (add to your Makefile)

```makefile
# Run custom API server with agent
api-server:
	uv run python -m app.api_server
```

## Available Endpoints

### Agent Endpoints (from ADK)

These are automatically provided by `get_fast_api_app()`:

| Endpoint                                      | Method | Description                                 |
| --------------------------------------------- | ------ | ------------------------------------------- |
| `/run_sse`                                    | POST   | Stream agent responses (Server-Sent Events) |
| `/run`                                        | POST   | Query agent (non-streaming)                 |
| `/list-apps`                                  | GET    | List available apps                         |
| `/apps/{app}/users/{user}/sessions`           | POST   | Create session                              |
| `/apps/{app}/users/{user}/sessions/{session}` | GET    | Get session                                 |
| `/docs`                                       | GET    | Interactive API documentation               |

### Custom Endpoints (your business logic)

| Endpoint                     | Method | Description                              |
| ---------------------------- | ------ | ---------------------------------------- |
| `/health`                    | GET    | Health check for monitoring              |
| `/api/info`                  | GET    | Service information and endpoint listing |
| `/api/transactions/validate` | POST   | Validate a single transaction            |
| `/api/transactions/batch`    | POST   | Process multiple transactions            |
| `/api/transactions/{id}`     | GET    | Get transaction details                  |
| `/api/agent/analyze`         | POST   | Custom wrapper for agent analysis        |

## Usage Examples

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "healthy",
  "service": "adk-agent-api"
}
```

### 2. Get Service Info

```bash
curl http://localhost:8000/api/info
```

### 3. Validate Transaction

```bash
curl -X POST http://localhost:8000/api/transactions/validate \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_123",
    "amount": 1000.50,
    "currency": "USD",
    "payee_country": "Canada",
    "vendor_country": "USA",
    "payment_method": "Bank Transfer",
    "payment_purpose": "Payroll"
  }'
```

### 4. Agent Interaction (ADK standard endpoint)

```bash
# Create a session first
curl -X POST http://localhost:8000/apps/app/users/user_123/sessions \
  -H "Content-Type: application/json" \
  -d '{"state": {}}'

# Stream agent response
curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "app",
    "user_id": "user_123",
    "session_id": "session_abc",
    "new_message": {
      "role": "user",
      "parts": [{"text": "Analyze this transaction"}]
    },
    "streaming": true
  }'
```

### 5. Batch Processing

```bash
curl -X POST http://localhost:8000/api/transactions/batch \
  -H "Content-Type: application/json" \
  -d '[
    {
      "transaction_id": "txn_1",
      "amount": 100,
      "currency": "USD",
      "payee_country": "USA",
      "vendor_country": "Canada",
      "payment_method": "Credit Card",
      "payment_purpose": "Purchase"
    },
    {
      "transaction_id": "txn_2",
      "amount": 200,
      "currency": "EUR",
      "payee_country": "France",
      "vendor_country": "Germany",
      "payment_method": "Bank Transfer",
      "payment_purpose": "Invoice"
    }
  ]'
```

## Frontend Integration

Update your frontend to use both agent and custom endpoints:

```typescript
// Agent interaction (existing)
const agentResponse = await fetch("/api/run_sse", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    app_name: "app",
    user_id: "user_123",
    session_id: sessionId,
    new_message: { role: "user", parts: [{ text: query }] },
    streaming: true
  })
})

// Custom endpoint (new)
const validationResponse = await fetch("/api/transactions/validate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    transaction_id: "txn_123",
    amount: 1000,
    currency: "USD"
    // ... other fields
  })
})
```

## Adding Your Own Endpoints

To add custom endpoints, edit `app/api_server.py`:

```python
@app.post("/api/your-endpoint")
async def your_custom_endpoint(data: YourModel) -> dict[str, Any]:
    """
    Your custom business logic here.
    """
    # Process data
    result = process_your_data(data)

    return {"result": result}
```

## Deployment

### Local Development

```bash
# Already configured in vite.config.ts
# Frontend proxies /api/* to http://127.0.0.1:8000
cd frontend && npm run dev

# In another terminal
python -m app.api_server
```

### Cloud Run Deployment

Create a `Dockerfile` or use `adk deploy cloud_run`:

```bash
# Using ADK CLI (update to use api_server.py)
# Note: You'll need to modify deployment to use api_server.py instead of agent.py
adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --service_name=hackathon-api \
  .
```

Or create a custom `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["python", "-m", "app.api_server"]
```

### Vertex AI Agent Engine

When using Agent Engine, you'll deploy with `agent_engine_app.py` (which doesn't support custom endpoints). For custom endpoints + agent, use Cloud Run deployment instead.

## Comparison: When to Use What

| Deployment Method           | Agent Endpoints | Custom Endpoints | Session Management | Use Case                  |
| --------------------------- | --------------- | ---------------- | ------------------ | ------------------------- |
| `adk api_server`            | ✅ Yes          | ❌ No            | In-memory/SQLite   | Local dev only            |
| `api_server.py` (this file) | ✅ Yes          | ✅ Yes           | In-memory/SQLite   | Local dev + Cloud Run     |
| `agent_engine_app.py`       | ✅ Yes          | ⚠️ Limited\*     | Vertex AI managed  | Production (agent-only)   |
| Cloud Run + `api_server.py` | ✅ Yes          | ✅ Yes           | Your DB/Vertex AI  | Production (agent + APIs) |

\*Agent Engine allows `register_operations()` for custom methods, but these are agent-specific, not REST endpoints.

## Best Practices

1. **Development**: Use `api_server.py` locally with SQLite sessions
2. **Production with custom APIs**: Deploy to Cloud Run with proper session storage
3. **Production agent-only**: Use Vertex AI Agent Engine
4. **Monitoring**: Use `/health` endpoint for liveness/readiness probes
5. **Documentation**: FastAPI auto-generates docs at `/docs`
6. **CORS**: Configure `ALLOWED_ORIGINS` appropriately for production

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use a different port
PORT=8001 python -m app.api_server
```

### Agent Not Found

Ensure your agent is in the correct location:

```
app/
├── __init__.py
├── agent.py        # Must export 'app'
├── api_server.py   # This file
└── sub_agents/
```

### Session Errors

For production, use a persistent session store:

```python
SESSION_SERVICE_URI = "postgresql://user:pass@host/db"
# Or
SESSION_SERVICE_URI = "vertex://projects/PROJECT/locations/LOCATION"
```

## Next Steps

1. Customize the example endpoints in `api_server.py`
2. Add your business logic models using Pydantic
3. Integrate with your databases or services
4. Test with the frontend
5. Deploy to Cloud Run for production

## Related Files

- `app/agent.py` - Main agent definition
- `app/agent_engine_app.py` - Vertex AI Agent Engine wrapper
- `frontend/vite.config.ts` - Frontend proxy configuration
- `Makefile` - Build and deployment commands
