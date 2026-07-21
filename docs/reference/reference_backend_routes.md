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
    Stage 3: {done, output, priorities[], fcv_rating, fcv_responsiveness_rating,
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
    - Appends a sector-lens source/evidence appendix when lens data is present
    - Frontend: downloadReport() POSTs JSON payload; receives blob; triggers browser save

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
