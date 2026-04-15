# WBG FCV Project Screener

A Flask web application that guides World Bank Task Team Leaders (TTLs) through a structured 3-stage workflow to assess and improve FCV (Fragility, Conflict & Violence) integration in project design.

## What it does

Upload a project document (PAD, PCN, PID, or restructuring paper) and optionally a Country Partnership Framework or other contextual document. Choose your workflow:

- **Express Analysis** (default) — all 3 stages run automatically in a single connection (~4–5 min)
- **Step-by-Step** — interactive mode; review and refine at each stage before proceeding (~8–12 min)

Both modes produce identical output across three stages:

1. **Stage 1 — Context Extraction** — Extracts FCV risks from the project document, enriched by automated web research
2. **Stage 2 — FCV Assessment** — Thematic analysis across FCV dimensions, Do No Harm traffic-light, and detailed Under the Hood panels
3. **Stage 3 — Recommendations Note** — Structured memo with strategic priorities, actionable guidance, and ready-to-paste PAD language

## Prerequisites

- Python 3.10+
- An Anthropic API key ([console.anthropic.com](https://console.anthropic.com))

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | **Yes** | Anthropic API key for Claude access |

## Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set required environment variable
export ANTHROPIC_API_KEY="your-api-key-here"

# Run locally
python app.py
# Open http://localhost:5000
```

## Render Deployment

1. Connect this GitHub repo to a new Render **Web Service**
2. Set `ANTHROPIC_API_KEY` as an environment variable in the Render dashboard
3. Render reads `Procfile` automatically — no additional build config needed
4. The app runs on gunicorn + gevent with a 600s timeout, required for long-running SSE streams

## Concurrency

The app isolates state per browser tab via a per-assessment ID. Express Analysis runs off the request thread via a background executor. Combined with multi-worker gunicorn settings in `Procfile`, multiple users and sessions can run assessments concurrently.

## Key Files

| File | Purpose |
|---|---|
| `app.py` | Flask backend — all stage prompts, routes, document processing |
| `index.html` | Single-page frontend UI |
| `background_docs.py` | WBG FCV framework reference constants (knowledge base) |
| `requirements.txt` | Python dependencies |
| `Procfile` | Render deployment config |

## Documentation

- `CLAUDE.md` — full developer guide: architecture, prompt design, stage pipeline, design decisions
- `docs/reference/` — detailed reference docs for prompts, routes, and frontend functions
- `docs/fcv-agent-knowledge-architecture.html` — visual overview of how knowledge sources flow through the pipeline
