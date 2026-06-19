# AI Customer Support Assistant

FastAPI service for support chat with structured ticket responses and optional CRM webhook delivery.

## Setup

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

Set at least one provider key (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`).

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/chat` | Return structured support reply |
| POST | `/tickets` | Create ticket + optional CRM sync |
| GET | `/health` | Health check |

### Chat example

```bash
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "C-1042",
    "message": "My order 8821 never arrived",
    "provider": "openai"
  }'
```

Response fields include `category`, `priority`, `reply`, `suggested_actions`, and `needs_human`.

## CRM integration

If `CRM_WEBHOOK_URL` is set, `/tickets` posts a JSON payload with the ticket summary.
`CRM_WEBHOOK_TOKEN` is sent as `Authorization: Bearer <token>` when present.
