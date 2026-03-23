# FCV Project Screening App — Claude Development Guide

> **Claude Code Maintenance Instruction:** After every substantial change to this app (new features, prompt changes, new delimiters, UI additions, architectural decisions), update this `CLAUDE.md` to reflect the change before committing. Keep the Stage pipeline summary, Prompt Architecture, and Priority Parsing sections accurate at all times.

---

## Overview

This is a **World Bank FCV (Fragility, Conflict, and Violence) Project Screener** — a Flask-based web app guiding Task Team Leaders (TTLs) through a 4-stage workflow to assess FCV integration and generate targeted recommendations.

Two concepts are explicitly distinguished:
- **FCV Sensitivity [S]** — avoiding harm: do-no-harm, contextual awareness, conflict-informed design, operational readiness.
- **FCV Responsiveness [R]** — actively addressing root drivers of fragility, anchored to the four pillars of the WBG FCV Strategy 2020–2025.

All prompt outputs tag recommendations, mitigations, and priorities as `[S]`, `[R]`, or `[S+R]`.

**Core mandate:** Recommendations must name locations and mechanisms — not broad policy suggestions. Bad: *"service delivery needs to be targeted."* Good: *"Focus on Nzerekore, Kindia, and Kankan — historically excluded — to rebuild state-society relationships."*

---

## 1. Architecture

### 1.1 Tech Stack
- **Backend:** Python Flask 3.0.3 + Anthropic Claude API (`claude-sonnet-4-20250514`)
- **Frontend:** HTML + vanilla JavaScript + Markdown rendering (single-page app)
- **Hosting:** Render.com (auto-deploys from `main`)
- **Document processing:** pypdf + LLM-assisted summarization for large docs
- **Session management:** Browser localStorage + JSON conversation history

### 1.2 Core Files
```
app.py               # Flask backend, DEFAULT_PROMPTS, all routes, document processing
index.html           # Frontend UI (~4000 lines), Stage 1–4, Explorer, prompt modal
background_docs.py   # FCV_GUIDE and FCV_OPERATIONAL_MANUAL constants
prompts.json         # Session-specific prompt overrides (empty by default)
requirements.txt     # Flask, anthropic, pypdf, python-docx
Procfile             # Render: gunicorn app:app
```

### 1.3 Stage Pipeline Summary

| Stage | Input | Key Output | Non-obvious behaviour |
|---|---|---|---|
| **1 — FCV Risks** | Project doc + optional contextual docs | Part A (doc extract) + Part B (contextualised) | Runs automated web research (9 searches) before LLM call; embeds `%%%DOC_TYPE: [type]%%%` as last line (stripped from display) |
| **2 — Sensitivity Screening** | Stage 1 output | Risk ratings across 6 dimensions + S/R classification + Responsiveness Probe | Pre-assigned default tags for 6 OST recommendations (see §3 below) |
| **3 — Gap Analysis** | Stages 1–2 | Parts A–E: gaps, mitigations (tagged), Do-No-Harm checklist, Responsiveness opportunities, Top 5 priorities | Part C table is parsed by frontend regex and rendered as collapsible checklist in Stage 4 |
| **4 — Recommendations Note** | Stages 1–3 | Preamble + exec summary + 4–5 priority cards | Heavy delimiter-based parsing; `clean_stage4_output()` strips all delimiters before display |
| **Explorer** | Priority + full history | 3–5 design options (A/B/C) with PAD callouts | Loaded async per priority; cached per priority index |

**Stage 1 web research:** `extract_country_name()` → `extract_sector_name()` → `run_fcv_web_research()` (Anthropic `web_search` tool, 9 searches, ≤5500 tokens). Results cached in-memory by `"country::sector"` key (lost on restart). Shown as collapsible dropdown at top of Stage 1 output.

**Stage 1 citation tiers:**
- Tier 1 — Uploaded docs: `[From: document name]`
- Tier 2 — Web research: `[From: web research]`
- Tier 3 — Training knowledge: `[From: training knowledge]`

**Large document handling:** Docs >150k chars are condensed via LLM extraction. Docs >500k chars are truncated to `MAX_DOC_CHARS`.

---

## 2. S/R Tagging Rules (Non-Obvious — Must Be Preserved)

**`[S+R]` is strictly limited to four overlap zones:**
1. Inclusion/targeting of conflict-affected populations (harm-avoidance AND active resilience)
2. FCV logic embedded in the ToC/PDO framing (not just a risk note)
3. Adaptive M&E that monitors harm AND adapts to build resilience
4. GRM designed to strengthen state-citizen accountability (not just complaint handling)

If in doubt → use `[S]` or `[R]`. Most recommendations will not qualify for `[S+R]`.

**Stage 2 OST recommendation defaults:**
| Rec | Default |
|---|---|
| Rec 1 — RRA/CRSS utilization | `[S]` |
| Rec 2 — Conflict-sensitive targeting | `[S]` |
| Rec 3 — Inclusive stakeholder engagement | `[S+R]` |
| Rec 4 — Do No Harm / conflict-sensitive design | `[S]` |
| Rec 5 — Adaptive management | `[S]` |
| Rec 6 — M&E / GRM | `[S+R]` |

LLM may override defaults where project evidence justifies it.

**Rating scale** (used for both Sensitivity and Responsiveness gauges):
`Extremely Low | Very Low | Low | Adequate | Well Embedded | Very Well Embedded`

---

## 3. Prompt Architecture

### 3.1 Where Prompts Live

```python
# app.py — top-level dictionary
DEFAULT_PROMPTS = {
    "1": "...",        # Stage 1
    "2": "...",        # Stage 2
    "3": "...",        # Stage 3
    "4": "...",        # Stage 4 (Recommendations Note)
    "explorer": "..."  # Explorer deep-dive
}
```

Session overrides stored in `prompts.json`; merged with defaults via `load_prompts()`. Override via UI: Admin tab → per-stage editor. Override globally: edit `DEFAULT_PROMPTS` in `app.py`.

### 3.2 Stage 4 Delimiters (Critical for Parsing)

`clean_stage4_output()` strips these blocks before rendering display text:

```
%%%RISK_EXPOSURE_START%%%
RISKS_TO_PROJECT: [paragraph]
RISKS_FROM_PROJECT: [paragraph]
%%%RISK_EXPOSURE_END%%%

%%%SENSITIVITY_SUMMARY_START%%%
[80–100 word assessment]
%%%SENSITIVITY_SUMMARY_END%%%

%%%RESPONSIVENESS_SUMMARY_START%%%
[80–100 word assessment]
%%%RESPONSIVENESS_SUMMARY_END%%%

%%%FCV_RATING: [level]%%%
%%%FCV_RESPONSIVENESS_RATING: [level]%%%

%%%PRIORITY_START%%%
TITLE: Priority N · [phrase]
FCV_DIMENSION: [dimension]
TAG: [S] | [R] | [S+R]
RISK_LEVEL: High | Medium | Low
THE_GAP: [text]
WHY_IT_MATTERS: [text]
SUGGESTED_DIRECTIONS: [text]
WHO_ACTS: [text]
WHEN: [text]
RESOURCES: [text]
%%%PRIORITY_END%%%
```

`%%%GAP_TABLE_START/END%%%` extraction code exists in backend but table is **not rendered** in the current UI.

### 3.3 Citation Policy (Stage 4 Hallucination Guard)

**Only cite documents that appeared as `[From: doc name]` in Stage 1.** Never fabricate titles. Non-uploaded sources → `[From: training knowledge]` or `[From: web research]`. This guards against hallucinated citations like `[RRA 2022]` when no RRA was uploaded. If modifying Stage 4 prompt, preserve this guard.

### 3.4 AI Disclaimer Header

All Stage 4 outputs are prepended with a disclaimer via the `DO_NO_HARM_HEADER` constant in `app.py`. Includes generation date.

---

## 4. Key Constants & Limits

```python
MAX_DOC_CHARS = 500_000        # Hard truncation limit
EXTRACT_THRESHOLD = 150_000    # Triggers LLM condensation
ADMIN_PASSWORD = "fcv-admin-2024"  # From env var ADMIN_PASSWORD
PROMPTS_FILE = 'prompts.json'
```

---

## 5. How to Modify

### Change a prompt
1. Admin tab → select stage → edit → Save & Close (session-scoped)
2. Or edit `DEFAULT_PROMPTS` in `app.py` (global, persists)

### Change the 6 FCV dimensions
Edit Stage 2 prompt. If changing the count, also update Stage 3 and 4 prompts to reference them correctly.

### Add/remove a Stage 4 priority field
1. Update the `%%%PRIORITY_START/END%%%` block in the Stage 4 prompt
2. Update `extract_priorities()` in `app.py`
3. Update `showPriority()` in `index.html`

### Add a 5th stage
1. New key in `DEFAULT_PROMPTS`
2. New case in `/api/run-stage` switch logic
3. New stage card and input panel in `index.html`
4. Update stepper

---

## 6. Deployment

### Local
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
export ADMIN_PASSWORD="fcv-admin-2024"   # optional
python3 app.py
# Open http://localhost:5000
```

### Render.com
- Connect GitHub repo → Web Service → reads `Procfile` + `requirements.txt`
- Auto-deploys on push to `main`
- Required env vars in Render dashboard: `ANTHROPIC_API_KEY`, `ADMIN_PASSWORD`

### Branch workflow
```bash
git checkout -b feat/my-change
# make changes, test locally
git add app.py index.html
git commit -m "feat: describe change"
git push origin feat/my-change
# open PR → merge → Render auto-deploys
```

---

## 7. Testing

**Manual workflow:**
1. Upload a test PAD + contextual doc (RRA or country risk assessment)
2. Run all 4 stages; check:
   - Stage 1 Part A extracts from project doc only; Part B cites tiers correctly
   - Stage 2 ratings are reasonable; S/R tags match the strict definition
   - Stage 3 mitigations name specific locations and mechanisms
   - Stage 4 priorities are concrete with geographic callouts; citations not fabricated
   - Explorer offers distinct A/B/C options with PAD change callouts
3. Test the refine loop at each stage
4. Test Explorer deep-dive for 1–2 priorities

**Prompt quality check:** Are recommendations specific (geography, mechanism, entry points)? Evidence-based? Multiple options offered?

---

## 8. Debugging

**App hangs on Stage 1 large PDF** — LLM is condensing the doc (expected, 30–60s). Check browser console; if no errors, wait.

**Stage 2 ratings seem off** — Use the refine box to add local knowledge, or edit Stage 2 prompt via Admin modal and re-run.

**Explorer options not specific enough** — Update Explorer prompt to require geographic naming and mechanism specification.

**Do No Harm checklist not showing in Stage 4** — Stage 3 must generate a `## Part C` section with a Markdown table. Check the regex in `index.html` if the table format differs.

**Debugging steps:**
1. Browser console (F12) for JS errors
2. Flask server logs (Render dashboard stdout) for backend errors
3. Admin modal to inspect the exact prompt used
4. Copy LLM output and ask Claude: *"Why might this recommendation be vague?"*

---

## 9. Known Limitations

- **localStorage scope:** Sessions are browser/device-specific — no team sharing or archival
- **Research cache is in-process:** Lost on server restart; repeat runs with same country+sector use cached results
- **Large PDFs:** Docs >500k chars are truncated; very large projects may lose nuance
- **Citation hallucination:** Stage 4 prompt guards against this — preserve the guard if modifying Stage 4

---

*Last updated: 2026-03-23*
*Version: FCV Project Screener 5.0 (S/R distinction, dual gauges, embedded doc type detection)*
*Model: claude-sonnet-4-20250514*
