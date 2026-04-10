# WBG FCV Project Screener

A Flask web application that guides World Bank Task Team Leaders (TTLs) through a structured 3-stage workflow to assess and improve FCV (Fragility, Conflict & Violence) integration in project design.

## What it does

Upload a project document (PAD, PCN, PID, or restructuring paper) and optionally a contextual document (RRA, country risk assessment). On the landing page, choose your workflow:

- **Express Analysis** (default) — all 3 stages run automatically in a single connection (~4–5 min). A progress screen shows live status for each stage. No interaction needed until results are ready.
- **Step-by-Step** — interactive mode; review and refine at each stage before proceeding (~8–12 min).

Both modes produce identical output. The tool then:

1. **Stage 1 — Context Extraction** — Extracts FCV risks from the project document, enriched by automated web research
2. **Stage 2 — FCV Assessment** — Thematic analysis across FCV dimensions (sensitivity + responsiveness), Do No Harm traffic-light, Under the Hood panels for FCV Country Coordinators
3. **Stage 3 — Recommendations Note** — Generates a memo-ready note with 4–5 strategic priorities, each containing structured actions with ready-to-paste PAD language, and optional "Go Deeper" panels linking to the FCV Playbook

Output distinguishes **FCV Sensitivity** (do no harm) from **FCV Responsiveness** (actively addressing fragility drivers), anchored to the WBG FCV Strategy and the January 2026 FCV Refresh.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set required environment variable
export ANTHROPIC_API_KEY="your-api-key-here"

# Optional: set admin password for prompt editing (default: fcv-admin-2024)
export ADMIN_PASSWORD="your-password"

# Run locally
python app.py
```

Open `http://localhost:5000` in your browser.

## Concurrency

The app now isolates browser state per assessment tab and injects an `assessment_id` into analysis requests so parallel assessments do not overwrite each other in the same browser profile.

Express Analysis is also executed off the request thread via the app's assessment executor. Combined with multi-worker gunicorn settings in `Procfile`, this allows multiple users and multiple browser sessions to run assessments concurrently with less blocking than the earlier single-session setup.

## Deployment

Deployed on [Render.com](https://render.com). Connect the GitHub repo, set `ANTHROPIC_API_KEY` in the Render dashboard environment variables, and Render will use the `Procfile` automatically.

## Key files

| File | Purpose |
|------|---------|
| `app.py` | Flask backend, all 3 stage prompts + deeper/followon prompts, stage routes, document processing |
| `index.html` | Single-page frontend UI |
| `background_docs.py` | WBG FCV framework reference constants |
| `requirements.txt` | Python dependencies |
| `Procfile` | Render deployment config |
| `claude.md` | Full developer guide (architecture, prompts, design decisions) |

## For developers

See `claude.md` for the full development guide, including prompt architecture, stage pipeline, frontend functions, and how to extend the tool.
