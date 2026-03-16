# WBG FCV Project Screener

A Flask web application that guides World Bank Task Team Leaders (TTLs) through a structured 4-stage workflow to assess and improve FCV (Fragility, Conflict & Violence) integration in project design.

## What it does

Upload a project document (PAD, PCN, PID, or restructuring paper) and optionally a contextual document (RRA, country risk assessment). The tool then:

1. **Stage 1** — Extracts FCV risks from the project document, enriched by automated web research
2. **Stage 2** — Scores the project across 6 FCV dimensions (sensitivity) and probes responsiveness potential
3. **Stage 3** — Identifies specific design gaps and proposes location-grounded mitigations
4. **Stage 4** — Generates a memo-ready Recommendations Note with strategic priorities and an on-demand Explorer for deep dives

Output distinguishes **FCV Sensitivity** (do no harm) from **FCV Responsiveness** (actively addressing fragility drivers), anchored to the WBG FCV Strategy 2020–2025.

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

## Deployment

Deployed on [Render.com](https://render.com). Connect the GitHub repo, set `ANTHROPIC_API_KEY` in the Render dashboard environment variables, and Render will use the `Procfile` automatically.

## Key files

| File | Purpose |
|------|---------|
| `app.py` | Flask backend, all 4 prompts, stage routes, document processing |
| `index.html` | Single-page frontend UI |
| `background_docs.py` | WBG FCV framework reference constants |
| `requirements.txt` | Python dependencies |
| `Procfile` | Render deployment config |
| `claude.md` | Full developer guide (architecture, prompts, design decisions) |

## For developers

See `claude.md` for the full development guide, including prompt architecture, stage pipeline, frontend functions, and how to extend the tool.
