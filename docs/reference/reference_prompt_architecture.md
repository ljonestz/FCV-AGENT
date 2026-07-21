# Prompt Architecture — Detailed Reference

> Extracted from CLAUDE.md to keep the main file under the 40k context limit.
> Keep this file updated when prompt schemas, delimiters, or parsing logic change.

---

## Optional Sector-Lens Overlay

Both workflow paths call the same bounded composer. Stage 1 receives evidence/research intents and emits `%%%LENS_EVIDENCE_START/END%%%`. Stage 2 receives distilled guidance plus conditional questions and emits JSON in `%%%LENS_DIAGNOSTIC_START/END%%%`. Each finding contains lens/source provenance and an explicit `ost:*`, `dnh:*`, or `shift:*` mapping. Stage 3 merges overlapping findings and may add `lens_ids` and `lens_relevance` to affected priorities in the single existing recommendation set. Lenses never add a score or change the rating denominator. See `reference_sector_lenses.md` for the module schema and compatibility contract.

## Stage 1: "Context & Extraction"

**Purpose:** Extract FCV-relevant content from the primary project document, enriched by distilled secondary document cards, automated web research, and Playbook Diagnostics framing.

Current upload tiering: exactly one primary project document anchors the assessment; up to 10 project-package documents are distilled into key-signal cards; up to 3 contextual documents are distilled into RRA driver / CPF pillar cards or generic context cards.

**Secondary-document distillation:** Before Stage 1 assembly, package and contextual documents are passed through `fcv_distillation.distill_doc_parts_stream()`. Each secondary document is classified and extracted in isolation using Haiku, then mutated into a compact, source-labelled card. Package cards are injected under `SUPPORTING PACKAGE EVIDENCE (not independently assessed)`. Context cards are injected under `CONTEXT ANCHOR: CONFLICT DRIVERS AND COUNTRY PILLARS`, preserving RRA drivers and CPF pillars for Stage 3 matching. Failed or overflowed distillation produces a named stub rather than silently dropping a document. As of 2026-07-14, distillation streams each completed/timeout card as it arrives and emits `distilling_wait` keepalives while pending documents remain, avoiding a silent collect-all window before Stage 1 model streaming.

**Input:** Any WBG appraisal or design-stage project document (Concept Note, PID, PCN, PAD, Additional Financing, Restructuring Paper, DPF/DPO Program Document, PforR document, MPA, or regional operation). Optionally up to 10 project-package documents and up to 3 contextual documents (RRA, CPF, country risk report, policy matrix, DLI matrix, etc.).

**Automated FCV web research phase (runs before LLM generation):**
1. `extract_country_name()` — brief LLM call to identify project country (first 4000 chars)
2. `extract_sector_name()` — brief LLM call to identify primary project sector
3. `run_fcv_web_research(country, sector)` — Anthropic web_search tool, 9 targeted searches, up to 5500 tokens
   - Covers: conflict/security, governance, humanitarian, economic, FCV actors, structural drivers, vulnerable groups, regional dimensions, sector-specific FCV considerations
   - Results cached in-memory by `"country::sector"` key; lost on server restart
4. Research brief injected into Stage 1 context as supplemental material
5. Research brief shown as collapsible dropdown at TOP of Stage 1 output

**Three-tier citation priority:**
- Tier 1 — Uploaded contextual docs: `[From: document name]` (highest precedence)
- Tier 2 — Automated web research: `[From: web research]` or named source (e.g. `[From: ICG]`)
- Tier 3 — Training knowledge: `[From: training knowledge]` or named org/report

**Key behaviors:**
- Part A: Extract only from the primary project document plus package evidence cards. No outside knowledge.
- Part B: Use tiers 1→2→3 in strict priority order; always label the source tier at each point.
- Extraction guided by Playbook Diagnostics questions (RRA utilisation, compound risks, forced displacement, CPSD)
- FCV classification context from FCV Strategy 2026-2030 injected (is this an FCS country? what trajectory?)

**Large document handling:**
- Primary documents are extracted up to `MAX_DOC_CHARS`, then truncated to `STAGE1_MAX_DOC_CHARS = 60_000` before Stage 1.
- Secondary package/context documents are extracted up to `MAX_DOC_CHARS`, then distilled into capped cards before Stage 1. The old 25k/30k secondary full-read caps are no longer the effective Stage 1 payload size.
- Truncation warnings shown to users when triggered.

**Document type classification (embedded in Stage 1):**
- The very last line of every Stage 1 response is: `%%%DOC_TYPE: [PCN/PID/PAD/AF/Restructuring/ISR/Unknown]%%%`
- Stage 1 also emits `%%%INSTRUMENT_TYPE: [IPF/PforR/DPO/TA/MPA/IPF-DDO/Unknown]%%%` for instrument-aware Stage 2/3 calibration.
- The frontend extracts this via regex when Stage 1 completes and sets the `docType` state
- The DOC_TYPE line is stripped from the display text before rendering to the user
- `docType` is passed in the Stage 3 request body for stage-aware prompt injection

**Prompt constants injected:** `FCV_GUIDE`, `PLAYBOOK_DIAGNOSTICS`, `FCV_REFRESH_FRAMEWORK`

**Loading time note:** Stage 1 can be materially longer than 60-90 seconds for large PforR/P4R PADs because PDF extraction, web research, and the first Stage 1 model call all occur before the main Stage 1 text is visible. Render logs now include Stage 1 preprocessing and extraction diagnostics for both `/api/run-stage` and `/api/run-express`.

---

## Stage 2: "FCV Assessment" (merged Screening + Gaps)

**Purpose:** Assess project FCV sensitivity and responsiveness using the full OST framework. Identify gaps and Do No Harm status. Produce both a TTL-facing thematic summary and detailed analytical record for FCV CCs.

**Internal analytical engine:** All 12 OST recommendations + 25 key questions + 3 key elements. The TTL sees themed findings only — the framework structure is in "Under the Hood" panels.

**TTL-facing output (400–500 words, thematic narrative):**
- FCV Sensitivity findings: what the project addresses well, where it falls short
- Do No Harm traffic-light inline (e.g., "6 of 9 principles addressed | 1 partial | 1 gap")
- FCV Responsiveness findings: framed around the 4 FCV Strategy 2026-2030 pillars (not old pillars)
- Key gaps: 3–5 most critical, prioritised, with evidence

**Responsiveness assessment — 4 FCV Strategy 2026-2030 pillars:**
- Shift A: Anticipate — does the project design reflect current fragility classification?
- Shift B: Differentiate — is it calibrated to the country's FCV trajectory/context type?
- Shift C: Jobs & private sector — does it address economic livelihoods/job creation as a stability pathway?
- Shift D: Enhanced toolkit — does it leverage operational flexibilities (OP7.30, TPIs, hazard-appropriate CERC, etc.)?

**CERC guardrail:** Stage 2 must not score CERC absence as a flexibility gap on the basis of violence/conflict escalation, insecurity, civil unrest, armed-group activity, or access constraints alone. CERC is relevant only where there is a credible natural-hazard, climate, health, or economic emergency exposure and a plausible borrower emergency declaration/request pathway. For conflict-driven implementation risk, assess adaptive management, restructuring, SORT updating, security planning, TPM/GEMS, or urgent-need/condensed procedures instead.

**Do No Harm — canonical 9 principles:**
1. Conflict-sensitive targeting and beneficiary selection
2. Avoiding reinforcement of existing power asymmetries
3. Preventing exacerbation of inter-group tensions
4. Ensuring equitable geographic distribution of benefits
5. Safeguarding against elite capture of project resources
6. Protecting project staff and beneficiaries from security risks
7. Monitoring for unintended negative consequences
8. Establishing accessible and trusted grievance mechanisms

**Strict [S+R] definition:**
[S+R] only valid for: (1) inclusion/targeting of conflict-affected populations; (2) FCV logic in ToC/PDO; (3) adaptive M&E for harm + resilience; (4) GRM for state-citizen accountability.
If in doubt → [S] or [R].

**"Under the Hood" panels (collapsed, expandable `<details>`):**
- Panel 1: Full 12-rec assessment (table: rec | status | evidence | gaps | shift alignment)
- Panel 2: Detailed DNH checklist (9 principles, traffic-light table with evidence)
- Panel 3: 25 key questions mapping (answerable/gaps, evidence for each)
- Panel 4: Evidence trail (sources used, citation tier, confidence level)

**Delimiter blocks (stripped from display, parsed by frontend):**
```
%%%STAGE2_RATINGS_START%%%
{"sensitivity_rating": "Adequate", "responsiveness_rating": "Low"}
%%%STAGE2_RATINGS_END%%%

%%%RATING_REASONING_START%%%
[step-by-step scoring logic — auditing only]
%%%RATING_REASONING_END%%%

%%%UNDER_HOOD_START%%%
  %%%RECS_TABLE_START%%%    [12-rec table with S/R Tag column]  %%%RECS_TABLE_END%%%
  %%%DNH_CHECKLIST_START%%% [9-principle DNH checklist]         %%%DNH_CHECKLIST_END%%%
  %%%QUESTIONS_MAP_START%%% [25 key questions with findings]    %%%QUESTIONS_MAP_END%%%
  %%%EVIDENCE_TRAIL_START%%% [sources, types, contributions]    %%%EVIDENCE_TRAIL_END%%%
%%%UNDER_HOOD_END%%%
```

**Backend parsing functions:**
- `extract_stage2_ratings()` — parses `%%%STAGE2_RATINGS_START/END%%%` → `{sensitivity_rating, responsiveness_rating}`; also extracts `%%%RATING_REASONING_START/END%%%` → `rating_reasoning`
- `extract_under_hood()` — parses `%%%UNDER_HOOD_START/END%%%` → `{recs_table, dnh_checklist, questions_map, evidence_trail}`
- `clean_stage2_output()` — strips ratings + under_hood + rating_reasoning blocks from display text

**Rating Rubric (v7.5):**
- **Sensitivity:** Count of 12 OST recs rated "Strongly/Partially addressed" → 6-tier baseline. Quality gates cap if 3+ DNH gaps, no conflict analysis, or no geographic specificity.
- **Responsiveness:** Count of 4 FCV Strategy 2026-2030 pillars actively addressed → 6-tier baseline. Quality gates cap if zero shift alignment or no adaptive M&E.
- **Stage 3 inheritance:** Stage 3 copies Stage 2 ratings verbatim — no independent rating generation.

**Error handling:** If `extract_under_hood()` fails, `parse_error: true` in SSE done event; raw text shown; yellow banner displayed; Stage 3 can still proceed.

**Prompt constants injected:** `FCV_OPERATIONAL_MANUAL`, `FCV_REFRESH_FRAMEWORK`, `FCV_GUIDE`

---

## Stage 3: "Recommendations Note" (stage-aware)

**Purpose:** Generate a formal, memo-ready Recommendations Note with actionable priority cards, tailored to the project's lifecycle stage using Playbook guidance.

**Stage-awareness logic (doc_type passed in request body):**
- PCN/PID → PLAYBOOK_PREPARATION, timing: "Identification / Preparation"
- PAD → PLAYBOOK_PREPARATION, timing: "Preparation / Appraisal"
- AF/Restructuring → PLAYBOOK_IMPLEMENTATION, timing: "Implementation / Restructuring"
- ISR → PLAYBOOK_IMPLEMENTATION + PLAYBOOK_CLOSING, timing: "Implementation"
- Unknown → PLAYBOOK_PREPARATION (safe default)

**CERC recommendation guardrail:** Stage 3 must not recommend CERC, operationalise CERC readiness, or flag missing CERC readiness for conflict/violence escalation alone. CERC priority cards are allowed only for natural-hazard, climate, health, or economic emergency exposure with a plausible borrower declaration/request pathway, and must name that hazard pathway. Do not invent substitute activation paths such as UN appeals or certified statements of facts for conflict-triggered CERC activation.

**Narrative output structure:**
```
Preamble (50–75 words)
Opening Assessment (1 bold sentence)
Operational Context (150–200 words)
FCV Risk Exposure:
  RISKS_TO_PROJECT: How FCV dynamics threaten project delivery
  RISKS_FROM_PROJECT: How project design could worsen fragility
Strengths (80–120 words)
Gaps (100–130 words)
FCV Sensitivity Summary (80–100 words) ← extracted via delimiter, shown as card
FCV Responsiveness Summary (80–100 words) ← extracted via delimiter, shown as card
Stage badge (e.g., "Recommendations tailored for PCN stage")
```

**JSON block format (appended after narrative):**
```
%%%JSON_START%%%
{
  "fcv_rating": "Adequate",
  "fcv_responsiveness_rating": "Low",
  "sensitivity_summary": "...",
  "responsiveness_summary": "...",
  "risk_exposure": {
    "risks_to": "...",
    "risks_from": "..."
  },
  "priorities": [
    {
      "title": "Priority 1 · [Actionable verb phrase]",
      "fcv_dimension": "Inclusion",
      "tag": "[S]",
      "refresh_shift": "Shift B: Differentiate",
      "risk_level": "High",
      "the_gap": "...",
      "why_it_matters": "...",
      "actions": [
        {
          "document_element": "ESCP Commitment (new)",
          "guidance": "2–4 sentences describing what to add/revise and why",
          "suggested_language": "2–3 sentences of ready-to-paste draft PAD text"
        }
      ],
      "who_acts": "TTL; PIU",
      "when": "Preparation",
      "resources": "Moderate (dedicated allocation)",
      "pad_sections": "Annex 5: Stakeholder Engagement Plan; ESCP Commitment #4",
      "implementation_note": "1–2 sentences on timing, cost, or key dependency"
    }
  ]
}
%%%JSON_END%%%
```

**Field value sets:**
- `tag`: `[S]` | `[R]` | `[S+R]`
- `refresh_shift`: `Shift A: Anticipate` | `Shift B: Differentiate` | `Shift C: Jobs & private sector` | `Shift D: Enhanced toolkit`
- `risk_level`: `High` | `Medium` | `Low`
- `who_acts` (semicolon-separated): `TTL` | `PIU` | `Government` | `FCV CC` | `FM Team` | `ESF Team` | `Technical Team` | `M&E Team`
- `when`: `Identification` | `Preparation` | `Appraisal` | `Implementation` | `Restructuring`
- `resources`: `Minimal (existing budget)` | `Moderate (dedicated allocation)` | `Significant (requires restructuring)`

**`actions` array rules:**
- 2–4 structured actions per priority, each naming a specific document element to revise
- Must NOT be an options menu ("Consider A / Or B / Or C" is NOT allowed)
- Must name specific location, mechanism, and entry point in guidance
- S/R pillar justification sentence required in `why_it_matters` for [R] and [S+R] priorities

**`extract_priorities()` return shape:**
```python
{
  'error': bool,
  'message': str,              # only when error=True
  'priorities': [...],
  'fcv_rating': str,
  'fcv_responsiveness_rating': str,
  'sensitivity_summary': str,
  'responsiveness_summary': str,
  'risk_exposure': {'risks_to': str, 'risks_from': str}
}
# Each priority also gets: specificity_warning (bool), citation_warnings (list)
```

**`clean_stage3_output()` stripping order:**
1. Strip `%%%JSON_START%%%...%%%JSON_END%%%` block
2. Strip `%%%RISK_NARRATIVE_START%%%...%%%RISK_NARRATIVE_END%%%` block
3. Strip everything from `%%%PRIORITIES_START%%%` onwards
4. Fallback legacy delimiter stripping: `%%%RISK_EXPOSURE_START/END%%%`, `%%%SENSITIVITY_SUMMARY_START/END%%%`, `%%%RESPONSIVENESS_SUMMARY_START/END%%%`, `%%%FCV_RATING/RESPONSIVENESS_RATING%%%`, `%%%PRIORITY_START/END%%%`, `%%%GAP_TABLE_START/END%%%`

**Citation policy:**
- ONLY cite documents that appeared as `[From: document name]` in Stage 1. NEVER fabricate titles.
- Non-uploaded sources → `[From: training knowledge]` or `[From: web research]`
- `uploaded_doc_names` must be in `/api/run-stage` request body for citation check

**Prompt constants injected:** stage-appropriate PLAYBOOK constant + `FCV_REFRESH_FRAMEWORK`

---

## Priority Questions Prompt (v9.13 — "priority_questions" key in DEFAULT_PROMPTS)

**Purpose:** After the main three-stage run completes, answer the user's priority points (custom questions / areas of focus entered in the Analysis Guidance box) by cross-referencing the full Stage 1–3 outputs.

**When invoked:** Fired by `maybeRunPriorityQuestions()` in `index.html` AFTER the main run finishes (after `express_done` in Express mode, or after Stage 3 `done` in Step-by-Step). Never called inline during `run-express` or `run-stage`.

**Stage 2 rating guardrail:** The soft-emphasis injection does NOT alter the rating or DNH/rec-set logic. The Stage 2 prompt blocks override by the priority-questions block, keeping ratings/DNH/rec-set unaffected by the user's specific focus areas.

**Soft-emphasis injection into Stages 1–3 (`build_priority_questions_block(questions, stage)`):**
- Returns a bounded plain-English paragraph placed at the END of the user's context in each stage prompt
- Framed as "soft emphasis" — the LLM is instructed to draw out evidence relating to these questions where natural, but not to restructure or omit other required output
- Bounded: if questions text exceeds a character threshold, it is truncated with a disclosure note
- Injected into both `/api/run-stage` (step-by-step) and `/api/run-express` (express) paths

**System prompt structure (DEFAULT_PROMPTS["priority_questions"]):**
- Receives: stage1_output, stage2_output, stage2_ratings, stage3_output, stage3_priorities, priority_questions[], user_context
- Instruction: for each question, search across all stage outputs, produce a direct answer with evidence, link to matching priorities, flag gaps
- Output constraint: emit ONLY the %%%FOCUS_QUESTIONS_START/END%%% block (no prose wrapping)

**`%%%FOCUS_QUESTIONS_START/END%%%` JSON schema:**
```
%%%FOCUS_QUESTIONS_START%%%
{
  "overview": "2-3 sentence intro: how many points flagged, coverage note in natural language (no status labels).",
  "responses": [
    {
      "id":                  "1",
      "question":            "original question text as entered by the user",
      "status":              "addressed",
      "direct_answer":       "One full paragraph or two shorter paragraphs (~5–9 sentences) with operational detail. Two-paragraph answers use a blank line as separator.",
      "linked_priorities":   ["Priority title A", "Priority title B"],
      "confidence_gap_note": null
    }
  ]
}
%%%FOCUS_QUESTIONS_END%%%
```

Note: `evidence_basis` has been removed from this schema (v9.15). The `direct_answer` field is now a fuller response — one full paragraph or two shorter paragraphs (roughly 5–9 sentences), including relevant operational specifics. When the model uses two paragraphs it separates them with a blank line; the DOCX renderer splits on blank lines so each paragraph renders separately.

**Field value sets:**
- `overview`: top-level string; introduces the responses panel for readers who have not seen the internal Stage 1-3 analysis. Parsed and passed through by `extract_focus_questions()` as `overview` in the return dict.
- `status`: `"addressed"` | `"partially_addressed"` | `"not_yet_addressed"` (unknown values coerced to `"not_yet_addressed"` by `extract_focus_questions()`). **Internal-only — not displayed to the user.** Still used by the frontend's re-run nudge logic.
- `confidence_gap_note`: `null` (no gap) or a short string explaining uncertainty, preferring to name what is absent from the uploaded documents.

**Parsing:** `extract_focus_questions(text)` — see reference_backend_routes.md for full signature and return shape. Return dict includes `overview` alongside `responses` and `summary`. The parser tolerates an absent `evidence_basis` field via `setdefault`.

---

## Go Deeper "alternatives" tab output format (legacy — tab removed in v7.2, prompt retained)

- Only `%%%GO_FURTHER_START%%%...%%%GO_FURTHER_END%%%` markers used
- Each item uses `%%%GF_ITEM%%%` + `%%%GF_TITLE%%%` markers
- Parsed by `parseGoFurtherText()` → `goFurtherItems[]`
- Rendered by `renderGoFurtherHtml(parsed)` into `.beyond-item` cards

---

*Last updated: 2026-07-02 — added Priority Questions prompt, %%%FOCUS_QUESTIONS_START/END%%% schema, and soft-emphasis injection pattern (v9.13); added top-level `overview` field, plain-language `evidence_basis` constraint, `status` marked internal-only (v9.14); removed `evidence_basis` field, expanded `direct_answer` to one or two full paragraphs with blank-line separator, raised max_tokens to 10000 (v9.15)*
