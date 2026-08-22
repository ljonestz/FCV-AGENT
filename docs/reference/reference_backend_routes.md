# Backend Routes & Parsing — Detailed Reference

> Extracted from CLAUDE.md to keep the main file under the 40k context limit.
> Keep this file updated when routes, parsing functions, or SSE event shapes change.

---

## Main Routes

```python
# Core analysis route (all 3 stages)
POST /api/run-stage
  Input: {stage, documents[], history[], user_message, prompt_override,
          active_lenses[] (max 2), lens_versions{}, lens_diagnostic{},
          doc_type (Stage 3 only — for stage-aware prompt injection),
          uploaded_doc_names (Stage 3 only — for citation check)}
  Output: SSE stream with chunks, then:
    Stage 1: {done, output, active_lenses[], lens_warnings[]}
    Stage 2: {done, output, sensitivity_rating, responsiveness_rating,
              under_hood: {recs_table, dnh_checklist, questions_map, evidence_trail},
              rating_reasoning, lens_diagnostic, active_lenses[], lens_warnings[],
              parse_error, parse_error_message}
    Stage 3: {done, output, priorities[], concise_readout,
              fcv_rating, fcv_responsiveness_rating,
              sensitivity_summary, responsiveness_summary,
              risk_exposure: {risks_to, risks_from},
              parse_error, parse_error_message}

# Express mode route (single SSE endpoint for all 3 stages)
POST /api/run-express
  Input: {documents[], assessment_id, review_mode, user_context, priority_questions,
          active_lenses[], lens_versions{}}
  Output: SSE stream with events:
    assessment_id: {assessment_id}
    stage_start: {stage_start: N}
    research_status: {research_status, country}
    preprocessing: {status: "preprocessing", preprocessing: {...}}  # secondary-doc distillation progress
    preprocess: {preprocess: message}
    chunk: {chunk: text, stage: N}
    stage_done: {stage_done: N, result, history, ...stage-specific data}
    keepalive: {keepalive: true, stage: N}  - every 20s if no data sent
    error: {error: message, failed_stage: N}
    express_done: {express_done: true}
  Notes: Runs Stage 1→2→3 in a single SSE connection. The workflow now executes
    on the background assessment executor and streams its events back to the
    client. Keepalive pings cover web research gaps and inter-stage transitions.
    The backend stream helper enforces per-stage wall-clock limits (Stage 1:
    8 min, Stage 2: 9 min, Stage 3: 9 min) so a provider stream that keeps the
    SSE alive without completing returns a clear stage error instead of running
    indefinitely.

# Oversized upload handling
POST /api/run-stage and POST /api/run-express
  If Flask raises RequestEntityTooLarge because the JSON body exceeds
  MAX_CONTENT_LENGTH, the app returns:
    HTTP 413
    {error: "...too large...", max_mb: <integer>}
  The frontend also preflights raw file sizes before base64 encoding and blocks
  requests likely to exceed the Render deployment limit.

# Go Deeper route
POST /api/run-deeper
  Input: {priority_index, tab, priority_title, priority_body, history[],
          doc_type, stage2_under_hood (for trail tab only)}
  tab values: "alternatives" | "trail" | "playbook_refs"
  Output:
    alternatives/playbook_refs: SSE stream with chunks, then {done, output}
    trail: {done, output} — no SSE; filtered from stage2_under_hood immediately

# Admin / Prompt management
GET  /api/admin/prompts         # Get current session prompts
POST /api/admin/prompts         # Save custom prompts for session
POST /api/admin/prompts/reset   # Reset to defaults

# System endpoints
GET /                           # Main app page
GET /health                     # Health check
GET /how-it-works               # Workflow explanation page
GET /admin                      # Admin panel (prompts modal)
GET /api/default-prompts        # Get default prompts for reference
GET /api/sector-lenses          # Enabled lens catalogue plus non-fatal load warnings
POST /api/detect-document-type  # Document metadata plus ranked lens_suggestions[]

# DOCX download route (v9.1; extended v9.13)
POST /api/download-report
  Input: {
    "summary": "<markdown string — Stage 3 executive summary>",
    "priorities": [ ...stageThreePriorities array... ],
    "focus_questions": { ...focusQuestionsResult... },  # optional (v9.13); omit or null to skip section
    "active_lenses": [{"id": "...", "version": "...", "position": "primary"}],
    "lens_diagnostic": {"lenses": [...], "findings": [...]},
    "lens_context_sources": [{"id": "context-ccdr", "lens_id": "climate", "source_type": "ccdr", "url": "https://...worldbank.org/..."}],
    "metadata": {
      "date_str": "18 April 2026",
      "classification_category": "Conflict-Affected",
      "classification_reasoning": "...",
      "finalized_pad": false,
      "finalized_pad_approval_date": null
    }
  }
  Output: Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
          Content-Disposition: attachment; filename="FCV-Recommendations-Note-YYYY-MM-DD.docx"
  Notes:
    - Builds a true DOCX binary using python-docx (not HTML masquerading as .docx)
    - Helpers: _md_to_docx_para(doc, text) — handles **bold**, *italic*, - bullets line-by-line
    -          _safe_run(para) — safe para.runs[0] access
    - Document structure: Title → subtitle → disclaimer → HR → optional finalized-PAD notice →
        optional classification box → Exec Summary → HR → Strategic Priorities (Heading 3 per
        priority, metadata line, gap/actions/who/timing, implementation note) →
        optional "Responses to Your Priority Points" section (v9.13, rendered when focus_questions
        is supplied and non-error; one subsection per response with status label, answer,
        evidence basis, linked priorities, and gap note)
    - Appends a sector-lens source/evidence appendix when lens data is present; validated dynamic context appears under "Country context used"
    - Frontend: downloadReport() POSTs JSON payload; receives blob; triggers browser save

Sector-lens catalogue records expose `activation` and `readout_sections`. Both `/api/run-stage` and `/api/run-express` carry `lens_context_sources` in request/SSE state. Stage 2 lens diagnostics include `materiality_summary`, `analysis_emphasis`, `readout_sections`, and `other_pathways` in addition to mapped findings. If an active-lens diagnostic is missing or incomplete, both routes use the same single dedicated Haiku recovery request (120-second default/read timeout, 10-second connection timeout, zero SDK retries). The response is strictly parsed, normalized, and validated against the active-lens contract before it is used. Failure remains non-fatal to the core FCV assessment, is logged, and is surfaced through the Stage 2 parse-error payload. v9.18 adds no further SSE schema change: the already-existing additive `lens_diagnostic_recovered` boolean reports successful repair, while existing fields and the diagnostic schema remain compatible.

# Follow-on post-analysis route (Stage 3 bottom card)
POST /api/run-followon
  Input: {messages[], priority_responses (optional)} — full conversationHistory + user message;
         when priority_responses[] is supplied (non-empty), the route folds the Q/A pairs
         onto the final user turn so the follow-on LLM has full priority-point context
  Output: SSE stream (same chunk/done format as run-stage)
  System prompt: DEFAULT_PROMPTS["followon"]
  max_tokens: 4000
  Note: Route truncates large assistant messages to 40,000 chars before sending

# Priority Questions route (v9.13 — Priority Points feature)
POST /api/run-priority-questions
  Input: {
    user_context,           # free-text framing entered by the user
    priority_questions,     # array of question strings derived from the guidance box
    stage1_output,          # Stage 1 assistant output text
    stage2_output,          # Stage 2 assistant output text (clean, display text)
    stage2_ratings,         # {sensitivity_rating, responsiveness_rating}
    stage3_output,          # Stage 3 narrative (clean, display text)
    stage3_priorities       # parsed priorities array from Stage 3 JSON
  }
  Output: SSE stream — chunk events during generation, then a done event:
    chunk: {chunk: text}
    done:  {done: true, focus_questions: {error, responses[], summary}}
  Notes:
    - Fired by the frontend AFTER the main run completes (express_done or Stage 3 done);
      never called inline within run-express or run-stage, preserving the timeout design
    - Independently retryable without re-running the main analysis
    - Uses DEFAULT_PROMPTS["priority_questions"] system prompt
    - Responses use the %%%FOCUS_QUESTIONS_START/END%%% delimiter block (see reference_prompt_architecture.md)

  Each response object in responses[]:
    {
      "id":                  string,     # matches original question identifier / index
      "question":            string,     # the original question text
      "status":              string,     # "addressed" | "partially_addressed" | "not_yet_addressed"
      "direct_answer":       string,     # 2–4 sentence answer grounded in the stage outputs
      "evidence_basis":      string,     # specific source citations ([From: name] or stage reference)
      "linked_priorities":   string[],   # priority titles from Stage 3 that relate to this question
      "confidence_gap_note": string      # null or note explaining uncertainty / data gap
    }

  Rendered by the frontend as a "Responses to your priority points" panel:
    - Status pill: green (addressed) / amber (partially_addressed) / grey (not_yet_addressed)
    - Answer text, evidence basis, linked priorities as chips, gap note in italic
```

---

## Document Handling

**Supported formats:** PDF (`.pdf`), Word (`.docx`), PowerPoint (`.pptx`), plain text (`.txt`, `.md`). Legacy binary formats (`.doc`, `.ppt`) are not supported.

**Frontend → backend flow:**
- Binary files (PDF, DOCX, PPTX) are read as `DataURL` (base64) via `FileReader.readAsDataURL()` and sent with `type: 'pdf'|'docx'|'pptx'`
- Text files are sent as plain text with `type: 'text'`
- File type detection via `detectFileType()` in `index.html`

**Extraction functions (all return `(text: str, count: int)`):**
```python
extract_pdf_text(b64_data, name)   # pypdf — page-by-page text extraction
extract_docx_text(b64_data, name)  # python-docx — body-order traversal, merged-cell dedup
extract_pptx_text(b64_data, name)  # python-pptx — slide-labelled text + table extraction
```

**`extract_docx_text()` details:**
- Iterates `doc.element.body` children in document order (preserves paragraph/table interleaving)
- Deduplicates merged table cells via `id(cell._tc)` identity check
- Notes slides excluded from PPTX extraction (presenter-only content)

**Extraction quality check (`_check_extraction(text, name)`):**
- Returns a warning string if text starts with `[Could not extract` or `[python-` (error), or if `len(text.strip()) < 100` (near-empty / scanned doc)
- Returns `None` if extraction looks valid
- Warnings collected in `extraction_warnings[]` list, yielded as SSE `extraction_warning` events early in `generate()`

**`/api/detect-document-type` — extraction_status values:**
- `'ok'` — text extracted successfully (>= 100 chars)
- `'empty'` — extracted but near-zero text (scanned/image PDF)
- `'failed'` — extraction error (corrupt, password-protected, library missing)

**Size limits:**
```python
MAX_CONTENT_LENGTH = 50 * 1024 * 1024 # Flask request-body cap; browser base64 JSON counts against this
MAX_DOC_CHARS = 500_000       # Hard cap per document after extraction
STAGE1_MAX_DOC_CHARS = 60_000 # Truncation before sending to Claude (Stage 1)
CARD_CHARS_2A = 2_800         # Structured package card cap in fcv_distillation.py
CARD_CHARS_2B = 1_200         # Generic package card cap in fcv_distillation.py
CARD_CHARS_CONTEXT = 1_800    # Context card cap in fcv_distillation.py
SECONDARY_CARD_BUDGET_CHARS = 32_000 # Global package/context card budget
MAX_ASSISTANT_CHARS = 40_000  # Truncation applied to assistant turns stored in conversation_history
```

Zone 2 package documents and Zone 3 contextual documents are distilled by `fcv_distillation.distill_doc_parts_stream()` before Stage 1 prompt assembly. The primary Zone 1 document is not distilled. Distillation now yields each completed/timeout card as it arrives and emits `keepalive` / `distilling_wait` events while slower secondary documents remain pending, so Stage 1 does not sit silent behind a collect-all preprocessing step.

Both `/api/run-stage` and `/api/run-express` log low-cardinality Stage 1 preprocessing and extraction summaries in Render logs:

```text
Stage 1 preprocessing start route=<route> summary={docs, primary, package, context, content_chars}
Stage 1 extraction complete route=<route> elapsed_ms=<ms> doc_parts=<n> extracted_chars=<n> warnings=<n>
```

These diagnostics intentionally avoid filenames and document text, but identify whether a PforR failure happened before extraction, during extraction, or after model streaming began.

---

## Conversation History — Compact-Label Pattern

Both `/api/run-stage` (step-by-step) and `/api/run-express` (express) store a **compact label** for each stage's user turn in `conversation_history` instead of the full prompt with injected background constants.

**Why:** The Stage 2 prompt with all injected constants is ~85k chars (~21k tokens). Storing it in history means Stage 3 carries this as dead weight in its API call input — it was causing slow time-to-first-token and intermittent "BodyStreamBuffer was aborted" timeouts on Render.

**Pattern:**
```
Stage 1 user turn: "[Stage 1 — project documents and FCV context analysed]"
Stage 2 user turn: "[Stage 2 — analysis prompt with operational guidance injected]"
Stage 3 user turn: "[Stage 3 — analysis prompt with operational guidance injected]"
```

Each stage re-injects its own fresh background docs into the API call. The history only needs the **assistant outputs** for continuity — the compact labels preserve the conversation turn structure without inflating the token count.

**Implementation:**
- Express: `conversation_history.extend([{"role": "user", "content": compact_label}, {"role": "assistant", "content": s2_truncated}])` (not `stage2_prompt`)
- Step-by-step: `compact_messages = messages[:-1] + [{"role": "user", "content": compact_label}]` before building `updated_messages`

---

## Normal FCV concise bundle

Core normal-FCV Stage 3 adds optional `concise_readout` and `priority.concise`
fields. The prompt places the delimited JSON before the detailed narrative;
`extract_priorities()` remains delimiter-based and does not depend on block position.
Active sector-lens prompts are not given the core concise schema.

`concise_readout` contains a headline, 150-200 word `overview`, and exactly three
`{title, text}` strengths. Every ranked priority must carry a complete concise
object with title, rationale, two to four actions, optional supported drafting, and
project-cycle guidance. Normalization is atomic: if the readout or any priority
concise object is incomplete, the parser returns no concise bundle and removes all
partial priority concise objects while preserving the detailed result.

Both `/api/run-stage` and `/api/run-express` return the normalized optional bundle.
No repair model call is made when it is unavailable.

## Priority Parsing — Stage 3 (`extract_priorities()`)

```python
def extract_priorities(stage3_output, uploaded_doc_names=None):
    # 1. Find %%%JSON_START%%%...%%%JSON_END%%% block
    # 2. Parse via json.loads()
    # 3. Validate refresh_shift (one of 4 pillars)
    # 4. Validate who_acts (semicolon-separated, expanded set)
    # 5. Validate when (Identification|Preparation|Appraisal|Implementation|Restructuring)
    # 6. Run _check_specificity(): mid-sentence capitalised words as proper-noun proxy
    # 7. Run _check_citations(): cross-ref [From: ...] against uploaded_doc_names + org whitelist
    # 8. Return unified dict with all fields + specificity_warning / citation_warnings per priority
    #    Priority fields include cpf_alignment and rra_driver_alignment.
    # 9. On malformed JSON: return {error: True, message: ...} — NOT silent failure
```

**Return shape:**
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
# Each priority has 13 core fields + specificity_warning (bool) + citation_warnings (list)
```

**Backwards compatibility:** `extract_priorities()` converts old `recommendation` string field to single-item `actions[]` array if present.

---

## Priority Questions Parsing — `/api/run-priority-questions` (`extract_focus_questions()`)

```python
def extract_focus_questions(text: str) -> dict:
    # 1. Find %%%FOCUS_QUESTIONS_START%%%...%%%FOCUS_QUESTIONS_END%%% block
    # 2. Parse via json.loads()
    # 3. Validate status values — unknown statuses coerced to "not_yet_addressed"
    # 4. Truncation salvage: if the closing delimiter is missing (stream cut short),
    #    attempts json.loads() on text up to the last complete response object
    # 5. Returns {error, message, responses[], summary}
    # 6. On malformed JSON: return {error: True, message: ...} — NOT silent failure
    # Mirrors the interface of extract_priorities() for error handling consistency
```

**Return shape:**
```python
{
  'error':     bool,
  'message':   str,       # only when error=True
  'responses': [...],     # list of response objects (see route spec above for fields)
  'summary':   str        # 1–2 sentence overall coverage summary
}
```

---

## Stage 2 Output Parsing

```python
def extract_stage2_ratings(stage2_output):
    # Finds %%%STAGE2_RATINGS_START/END%%% → {sensitivity_rating, responsiveness_rating}
    # Also extracts %%%RATING_REASONING_START/END%%% → rating_reasoning (auditing only)

def extract_under_hood(stage2_output):
    # Finds %%%UNDER_HOOD_START/END%%% → {recs_table, dnh_checklist, questions_map, evidence_trail}
    # On failure: returns {error: True, message: ...}

def clean_stage2_output(stage2_output):
    # Strips %%%STAGE2_RATINGS_START/END%%%, %%%RATING_REASONING_START/END%%%,
    # and %%%UNDER_HOOD_START/END%%% from display text
```

---

## SSE Done Event Payloads

**Stage 2:**
```json
{
  "sensitivity_rating": "Adequate",
  "responsiveness_rating": "Low",
  "rating_reasoning": "...",
  "under_hood": {
    "recs_table": "...",
    "dnh_checklist": "...",
    "questions_map": "...",
    "evidence_trail": "..."
  },
  "parse_error": false,
  "parse_error_message": ""
}
```

**Stage 3:**
```json
{
  "priorities": [...],
  "fcv_rating": "...",
  "fcv_responsiveness_rating": "...",
  "sensitivity_summary": "...",
  "responsiveness_summary": "...",
  "risk_exposure": {"risks_to": "...", "risks_from": "..."},
  "parse_error": false,
  "parse_error_message": ""
}
```

---

*Last updated: 2026-07-02 — added /api/run-priority-questions, extract_focus_questions, focus_questions param for /api/download-report, priority_responses param for /api/run-followon (v9.13)*


---

## Dual-regime parsers & helpers (v9.21)

- `extract_regime_context(stage1_output: str, instrument: str = "IPF") -> dict` — parses
  `%%%REGIME_CONTEXT_START/END%%%`, classifies `preparation_regime` / `es_regime` /
  `processing_model` via `regime_router`, sets `verification_flag` when a governing signal is
  missing/contradictory. Missing block → all-safe defaults (`unresolved_policy_source` /
  `UNRESOLVED` / `unknown`). Stripped from display by `clean_stage1_output()`.
- `appraisal_document_label(preparation_regime, instrument) -> str` — PAD ↔ Project Paper /
  Program Paper / Program Document.
- `appraisal_reference_set(preparation_regime, es_regime, instrument) -> tuple` — regime-gated
  minimum reference set (ESS items only for ESF + IPF).
- `build_regime_header(preparation_regime, processing_model, es_regime, instrument) -> str` —
  compact new-model Stage 2/3 prompt header ("" for legacy/unresolved).
- `build_minimum_reference_block(preparation_regime, es_regime, instrument) -> str` — verbatim
  legacy block ↔ corrected new-model block for the Stage 3 `{minimum_reference_set}` placeholder.
- `regime_router` (pure module): `classify_preparation_regime`, `classify_processing_model`,
  `classify_es_regime`, `op_7_50_screen`, `op_7_60_screen`, `action_timing_vocab`,
  `resolve_action_timing`.
- `extract_priorities(...)` gains `preparation_regime` / `instrument` kwargs (new-model timing
  remap) and mirrors `pad_sections` ↔ `appraisal_document_sections`; `authority_basis` field
  validated (default `reviewer_judgment`). Done-event / Stage 3 requests carry `regime_context`.


---

## Climate-FCV readout redesign helpers (v9.22)

- `climate_question_bank.select_triggered_questions(project_signals) -> {theme: [question,...]}` — pure trigger selector; cq1 always present.
- `sector_lenses.pipeline.climate_integration_rating(value) -> str` — validate the 6-tier rating label ('' if absent/invalid).
- `sector_lenses.pipeline._normalize_climate_sw(value)` — bound the `strengths_weaknesses` list.
- `build_lens_stage_context(..., project_signals="")` — injects the triggered bank + §12 calibration into the Stage 2 climate suffix; drops `wider_fcv_context` and adds §12.5/§12.9 guardrails to the Stage 3 climate prefix.
- `climate_integration_payload(diagnostic)` now returns `{level, rating, summary}`.
- DOCX (`download_report`): `add_climate_strengths_weaknesses()` + `add_climate_core_questions()` replace the standalone reflections/dividend/wider-FCV sections in climate mode.

## Climate-FCV country-bank route contract (v9.23)

Stage 1 in both `/api/run-express` and `/api/run-stage` selects a compact bank
manifest before live research. Completion events include `climate_grounding`
alongside `climate_research`. Stage 2 accepts only
`climate_grounding.bank_manifest`, rematerializes canonical records from the
pinned server release, and ignores browser-supplied source/evidence prose.
`/api/download-report` uses the same resolver before rendering provenance.

The browser envelope contains `state`, `warning_code`, `content_version`,
`country_iso3`, `research_status`, a sanitized `bank_manifest`, and bounded source
metadata. It excludes `prompt_context`, evidence/pathway records, and live claims.
Manifest fields are `bank_status`, `warning_code`, `schema_version`,
`content_version`, `country_iso3`, `evidence_ids`, and `pathway_ids`.

Typed warnings include `bank_missing`, `bank_incompatible`,
`bank_version_mismatch`, `bank_country_unavailable`, `bank_country_unapproved`,
`bank_content_expired`, `bank_manifest_invalid`, `bank_scope_unsupported`, and
`bank_packet_too_large`. All degrade without terminating the Climate run.

## Verified Climate-FCV Express route (v9.24)

For a design review whose resolved active-lens set is exactly `climate`,
`/api/run-express` preserves the existing extraction, country profile, bank
selection, live research, and final grounding steps, then dispatches to
`climate-verified-v2`. Exactly one file explicitly placed in the Project Document
slot may supply bounded project-fact blocks. Its applicability/version are recorded as
`partial`/`user_designated`, not independently verified/latest; stage, geography, and
financed scope remain unresolved. Unresolved package uploads remain in the document inventory but
their blocks are withheld from fact extraction; multiple candidate primaries withhold
all fact authority until precedence is resolved. Runtime blocks are deterministic
chunks of extracted text rather than original DOCX/PDF structural locators. Uploaded
context, country-bank evidence, and live claims remain contextual.
The route emits the usual three completion markers for browser compatibility,
with additive `climate_assessment` and `climate_reader` fields on Stages 2 and 3.
No legacy Stage 1/2/3 model stream is called on this path. Keepalives are emitted
while verified calls execute. The worker has a 14-minute wall-clock ceiling, retries
share the call's original timeout budget, and cancellation prevents later paid calls
after timeout or disconnect. A synchronous provider request already in flight cannot
be killed safely and may continue until its bounded per-call timeout. Mixed-lens, implementation, step-by-step, and
legacy-session behavior is unchanged.

Before research planning, the verified route derives an additive
`operation_context` from strong primary-document filename and heading markers.
It carries `document_type`, base `instrument_type`, `country_scope`, `is_mpa`,
`has_ipf_component`, `preparation_regime`, `processing_model`, `es_regime`, and
bounded warning/evidence notes. This happens before bank selection so an explicit
regional or multi-country operation reaches the existing `bank_scope_unsupported`
guard instead of receiving a single-country package. The context is returned on
the Stage 1 completion event and passed into every verified model stage. Unknown
or ambiguous routes remain `Unknown`; they do not inherit IPF guidance.
When an explicit OIS creation date is present, the date-based classifier takes
precedence over document-nomenclature markers and a marker/date conflict is
recorded. This prevents a legacy DPF Program Document from being labelled new
model merely because DPF retains the same document name across regimes.

`POST /api/download-report` accepts `climate_assessment` when its schema is
`climate-verified-v2`, rebuilds and validates the canonical reader model, and
returns the verified DOCX. Reader-integrity failures return 422 with bounded reason
codes instead of exporting a malformed report. Zero-priority verified exports
retain the reader's explicit no-recommendation admission message in HTML and DOCX.

Completed verified runs emit one bounded `Climate recommendation diagnostics`
application-log line with counts, semantic-review state, up to 12 reason codes,
and up to 12 unsupported numeric tokens. It never logs candidate text, source
excerpts, or model reasoning.

The operational guidance registry is `climate-guidance-v3`. Its supported
current-document matrix is IPF PCN/PID/PAD/Project Paper/AF/Restructuring;
PforR PCN/PID/PAD/Program Paper; DPF PCN/PID/PAD/Program Document; with an MPA
program-layer overlay for any supported base instrument. Unknown documents,
TA, ISR, and unresolved instruments fail closed and receive no drafting packet.

`recommendation_diagnostics.reason_codes` includes
`RECOMMENDATIONS_ALL_SUPPRESSED` when at least one recommendation candidate was
parsed but none survives the deterministic gates. In that state,
`recommendation_diagnostics.review_status` is `attention`; the canonical reader
sets `recommendation_status` to `incomplete` and displays a bounded warning on
live HTML, standalone HTML, and DOCX. This state must not be rendered as a
successful no-priority result. When the compiler returns no candidates at all,
the ordinary neutral zero-priority message remains valid.

The operation-context resolver uses document nomenclature as a strong regime
signal when an OIS date is unavailable. Date-based routing uses the IPF/PforR
boundary of 17 April 2026 and the DPF boundary of 18 April 2026.
