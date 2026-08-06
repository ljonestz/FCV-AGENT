# WBG FCV Project Screener

A Flask web application that guides World Bank Task Team Leaders (TTLs) through a structured 3-stage workflow to assess and improve FCV (Fragility, Conflict & Violence) integration in project design.

> **Current status & where everything is:** see [`docs/20260618_PROJECT_STATE.md`](docs/20260618_PROJECT_STATE.md) for the live branch map, open PRs, deployment state, and outstanding items. As of 2026-06-18 the phase 0-6 knowledge-base expansion and OPCS policy corrections are staged in PR #29 and not yet merged into `main`.

## What it does

Upload a WBG appraisal or design-stage document (PCN, PID, PAD, Additional Financing, Restructuring Paper, DPF/DPO Program Document, PforR document, MPA, or regional operation) and optionally a Country Partnership Framework or other contextual document. Choose your workflow:

- **Express Analysis** (default) - all 3 stages run automatically in a single SSE connection. Typical IPF/PAD runs are shorter; large PforR operations can run 10-15+ minutes on Render.
- **Step-by-Step** - interactive mode; review and refine at each stage before proceeding. Uses the same backend stage logic and timeout budgets as Express.

Both modes produce identical output across three stages:

1. **Stage 1 — Context Extraction** — Extracts FCV risks from the project document, enriched by automated web research
2. **Stage 2 — FCV Assessment** — Thematic analysis across FCV dimensions, Do No Harm traffic-light, and detailed Under the Hood panels
3. **Stage 3 — Recommendations Note** — Structured memo with strategic priorities, actionable guidance, and ready-to-paste project-document language

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
3. Render reads `Procfile` automatically - no additional build config needed
4. The app runs on gunicorn + gevent with a 600s timeout, required for long-running SSE streams
5. The public Render instance currently deploys from `main`; PforR timeout/payload hardening is live on `main` as of PR #51 (`2877bf9`).

### Long-Running PforR Notes

PforR/P4R project documents generate the largest outputs in the app because Stage 2 and Stage 3 include DLI/PAP/ESSA/ESMS-specific checks and a PforR watch list. The current `main` branch includes:

- backend per-stage stream caps of 8 minutes for Stage 1, 9 minutes for Stage 2, and 9 minutes for Stage 3;
- frontend abort budgets of 9/10/10 minutes, so backend stage errors surface before the browser aborts the stream;
- deterministic PforR/DPO vocabulary scrubbing, replacing a previous blocking model repair call;
- Stage 1 preprocessing/extraction diagnostics in Render logs;
- explicit 413 handling plus frontend preflight warnings for uploads that exceed Render's base64 JSON payload limit.

Recent live checks against `https://fcv-agent.onrender.com/` confirmed that the Morocco Green Generation PforR PAD can complete end-to-end. A later India STARS PforR PAD test hung before response headers, which should be treated as a live Render worker/gateway stall until Render logs show otherwise.

> **Deployment caveat (2026-06-18):** if the Render service has a dashboard **Start Command** of `python app.py`, it overrides the `Procfile` and runs the Flask dev server instead of gunicorn. Clear the Start Command (or set it to the gunicorn line from `Procfile`) so production uses gunicorn + gevent. See `docs/20260618_PROJECT_STATE.md` section 5.

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
| `docs/20260714_ITS_handover_p4r_timeout_patch.md` | Current IPS/ITS handover on PforR timeout and Render-main state |

## Documentation

- `docs/20260618_PROJECT_STATE.md` — current project state: branches, open PRs, deployment, outstanding items
- `CLAUDE.md` — full developer guide: architecture, prompt design, stage pipeline, design decisions
- `docs/reference/` — detailed reference docs for prompts, routes, and frontend functions
- `docs/fcv-agent-knowledge-architecture.html` — visual overview of how knowledge sources flow through the pipeline
