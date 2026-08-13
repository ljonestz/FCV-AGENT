# WBG FCV Project Screener

A Flask web application that guides World Bank Task Team Leaders (TTLs) through a structured 3-stage workflow to assess and improve FCV (Fragility, Conflict & Violence) integration in project design.

## What it does

Upload a WBG appraisal or design-stage document (PCN, PID, PAD, Additional Financing, Restructuring Paper, DPF/DPO Program Document, PforR document, MPA, or regional operation) and optionally a Country Partnership Framework or other contextual document. Choose your workflow:

- **Express Analysis** (default) - all 3 stages run automatically in a single SSE connection. Typical IPF/PAD runs are shorter; large PforR operations can run 10-15+ minutes on Render.
- **Step-by-Step** - interactive mode; review and refine at each stage before proceeding. Uses the same backend stage logic and timeout budgets as Express.

Both modes produce identical output across three stages:

1. **Stage 1 — Context Extraction** — Extracts FCV risks from the project document, enriched by automated web research
2. **Stage 2 — FCV Assessment** — Thematic analysis across FCV dimensions, Do No Harm traffic-light, and detailed Under the Hood panels
3. **Stage 3 — Recommendations Note** — Structured memo with strategic priorities, actionable guidance, and ready-to-paste project-document language

## Optional sector lenses

Users may select up to two specialist lenses before analysis. The production Climate-FCV Lens is manual-only and is never auto-suggested. Once selected, it automatically screens both climate-intent operations and wider development projects, prioritizes adaptation and resilience, and uses deep mitigation analysis only where a clear material pathway exists.

Core-only runs retain the standard 4-5 substantive priorities and the lightweight conditional Climate-FCV check. Active-lens runs supersede that lightweight check, use one integrated list of no more than five substantive priorities, and apply a flexible evidence-led mix of core, Climate-linked, and blended actions. Optional CCDR material is validated contextual support and must not dominate recommendations.

### Climate-FCV country evidence bank

The Climate-FCV lens can use a public, version-pinned companion repository at
`data/climate-fcv-country-bank`. Clone this application with submodules, or
initialize it after cloning:

```bash
git clone --recurse-submodules https://github.com/ljonestz/FCV-AGENT.git
git submodule update --init --recursive  # existing clone
```

The runtime reads only `releases/current/runtime.json`. A country is usable only
when that release passes schema/checksum checks and the country record is
approved and within its review window. Draft and reviewed candidates are never
promoted automatically. Missing, stale, incompatible, unapproved, unsupported
multi-country, or oversized content degrades safely to live research or thematic
sources; it does not terminate the Climate assessment.

The companion bank also contains a reviewed, non-production candidate release at
`data/climate-fcv-country-bank/releases/candidates/2026.08/runtime.json`. It
contains 24 country packages, including the six previously available candidates
and the 18-country expansion, but it is not loaded by default. To run an explicit
candidate preview, set both variables below; the output remains labelled
`preview; not approved`:

```text
CLIMATE_COUNTRY_BANK_PATH=data/climate-fcv-country-bank/releases/candidates/2026.08/runtime.json
CLIMATE_COUNTRY_BANK_PREVIEW=reviewed-candidate
```

For local testing or a deployment artifact outside the submodule, set
`CLIMATE_COUNTRY_BANK_PATH` to either the companion repository root or a specific
`runtime.json`. The default remains the pinned public submodule. Render must
initialize the root `.gitmodules` entry during checkout. The version-controlled
`render_build.py` entry point does this before installing application dependencies.

Selection is deterministic and project-specific. It targets 8 and caps 12 bank
items, with a 6,000-character bank boundary and 12,000-character combined
bank-plus-live boundary. The provenance states are `bank+research`, `bank-only`,
`research-only`, and `thematic-only`; live enrichment is non-fatal. The pinned
South Sudan pilot remains the approved production release with a review due date
of 2027-07-31; the 24-country release is a reviewable preview only. The bank
stores structured summaries and citations only: it does not redistribute raw
PDFs or cite its own generated text.

## Prerequisites

- Python 3.10+
- An Anthropic API key ([console.anthropic.com](https://console.anthropic.com))

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | **Yes** | Anthropic API key for Claude access |
| `CLIMATE_VERIFIED_RUN_MODE` | No | `quality` (default, Sonnet) or `smoke` (Haiku). Server-only; never accepted from browser requests. |
| `CLIMATE_VERIFIED_ASSESSMENT_MODEL` | No | Explicit server-side model override for the verified assessment call. |
| `CLIMATE_VERIFIED_REVIEW_MODEL` | No | Explicit server-side model override for the verified reviewer call. |

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
3. Set the Render **Build Command** to `python render_build.py`; this initializes
   the pinned public Climate-FCV bank submodule and installs requirements
4. Render reads the `Procfile` start command automatically
5. The app runs on gunicorn + gevent with a 1,200s timeout for long-running SSE streams
6. Confirm the startup and Climate-grounding logs show the expected application
   build, bank content version, and country ISO3 before acceptance testing

### Low-cost Climate workflow checks

Use one commit for both services. The production service leaves
`CLIMATE_VERIFIED_RUN_MODE` unset (or sets it to `quality`). A separate smoke
service sets it to `smoke`, which runs the same verified Climate-FCV pipeline
with Haiku for both structured calls. Smoke output is visibly labelled in the
browser, HTML export, DOCX export, and technical annex; it tests orchestration
and completeness, not analytical quality.

Do not expose model selection in a request or UI control. Keep the profile in
Render environment settings so a browser user cannot downgrade a production
assessment. A reviewed country-bank candidate still requires the separate,
explicit `CLIMATE_COUNTRY_BANK_PATH` and
`CLIMATE_COUNTRY_BANK_PREVIEW=reviewed-candidate` safeguards. The smoke profile
does not relax approval, provenance, checksum, or preview-labelling rules.

### Long-Running PforR Notes

PforR/P4R project documents generate the largest outputs in the app because Stage 2 and Stage 3 include DLI/PAP/ESSA/ESMS-specific checks and a PforR watch list. The current `main` branch includes:

- backend per-stage stream caps of 8 minutes for Stage 1, 9 minutes for Stage 2, and 9 minutes for Stage 3;
- frontend abort budgets of 9/10/10 minutes, so backend stage errors surface before the browser aborts the stream;
- deterministic PforR/DPO vocabulary scrubbing, replacing a previous blocking model repair call;
- Stage 1 preprocessing/extraction diagnostics in Render logs;
- explicit 413 handling plus frontend preflight warnings for uploads that exceed Render's base64 JSON payload limit.

Recent live checks against `https://fcv-agent.onrender.com/` confirmed that the Morocco Green Generation PforR PAD can complete end-to-end. A later India STARS PforR PAD test hung before response headers, which should be treated as a live Render worker/gateway stall until Render logs show otherwise.

## Concurrency

The app isolates state per browser tab via a per-assessment ID. Express Analysis runs off the request thread via a background executor. Combined with multi-worker gunicorn settings in `Procfile`, multiple users and sessions can run assessments concurrently.

## Key Files

| File | Purpose |
|---|---|
| `app.py` | Flask backend — all stage prompts, routes, document processing |
| `sector_lenses/` | Validated optional sector-lens packages, budgets, detection, and diagnostic parsing |
| `index.html` | Single-page frontend UI |
| `background_docs.py` | WBG FCV framework reference constants (knowledge base) |
| `requirements.txt` | Python dependencies |
| `Procfile` | Render deployment config |
| `docs/20260714_ITS_handover_p4r_timeout_patch.md` | Current IPS/ITS handover on PforR timeout and Render-main state |

## Documentation

- `CLAUDE.md` — full developer guide: architecture, prompt design, stage pipeline, design decisions
- `docs/reference/` — detailed reference docs for prompts, routes, and frontend functions
- `docs/reference/reference_sector_lenses.md` — sector-lens module and cross-build contract
- `docs/fcv-agent-knowledge-architecture.html` — visual overview of how knowledge sources flow through the pipeline
