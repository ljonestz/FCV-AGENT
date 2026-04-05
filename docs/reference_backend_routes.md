# Backend Routes & Parsing — Detailed Reference

> Extracted from CLAUDE.md to keep the main file under the 40k context limit.
> Keep this file updated when routes, parsing functions, or SSE event shapes change.

---

## Main Routes

```python
# Core analysis route (all 3 stages)
POST /api/run-stage
  Input: {stage, documents[], history[], user_message, prompt_override,
          doc_type (Stage 3 only — for stage-aware prompt injection),
          uploaded_doc_names (Stage 3 only — for citation check)}
  Output: SSE stream with chunks, then:
    Stage 1: {done, output}
    Stage 2: {done, output, sensitivity_rating, responsiveness_rating,
              under_hood: {recs_table, dnh_checklist, questions_map, evidence_trail},
              rating_reasoning, parse_error, parse_error_message}
    Stage 3: {done, output, priorities[], fcv_rating, fcv_responsiveness_rating,
              sensitivity_summary, responsiveness_summary,
              risk_exposure: {risks_to, risks_from},
              parse_error, parse_error_message}

# Express mode route (single SSE endpoint for all 3 stages)
POST /api/run-express
  Input: {documents[]}
  Output: SSE stream with events:
    stage_start: {stage_start: N}
    research_status: {research_status, country}
    preprocess: {preprocess: message}
    chunk: {chunk: text, stage: N}
    stage_done: {stage_done: N, result, history, ...stage-specific data}
    keepalive: {keepalive: true}  — every 20s if no data sent
    error: {error: message, failed_stage: N}
    express_done: {express_done: true}
  Notes: Runs Stage 1→2→3 in a single SSE connection. Keepalive pings cover
    web research gaps and inter-stage transitions.

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

# Follow-on post-analysis route (Stage 3 bottom card)
POST /api/run-followon
  Input: {messages[]} — full conversationHistory + user message
  Output: SSE stream (same chunk/done format as run-stage)
  System prompt: DEFAULT_PROMPTS["followon"]
  max_tokens: 4000
  Note: Route truncates large assistant messages to 40,000 chars before sending
```

---

## Document Handling

**Large document pre-processing:**
```python
if len(doc_content) > MAX_DOC_CHARS:
    # Use LLM to extract FCV-relevant content
    # Returns: extracted_text, page_count, truncation_warning
```

**PDF extraction:**
```python
# Uses pypdf library
extracted_text, page_count = extract_pdf_text(base64_content, filename)
```

**Extraction steps in `extract_pdf_text()`:**
1. Decode base64 PDF content from frontend
2. Use PyPDF to read PDF pages
3. Extract text from each page sequentially
4. Return: (extracted_text, page_count)
5. Handle errors gracefully with fallback messages

**Large document condensation in `extract_fcv_content()`:**
1. Check if document length exceeds EXTRACT_THRESHOLD (150,000 chars)
2. If yes, use Claude API to summarize FCV-relevant content
3. Preserve key information while reducing size
4. Append truncation warning to user output

---

## Priority Parsing — Stage 3 (`extract_priorities()`)

```python
def extract_priorities(stage3_output, uploaded_doc_names=None):
    # 1. Find %%%JSON_START%%%...%%%JSON_END%%% block
    # 2. Parse via json.loads()
    # 3. Validate refresh_shift (one of 4 shifts)
    # 4. Validate who_acts (semicolon-separated, expanded set)
    # 5. Validate when (Identification|Preparation|Appraisal|Implementation|Restructuring)
    # 6. Run _check_specificity(): mid-sentence capitalised words as proper-noun proxy
    # 7. Run _check_citations(): cross-ref [From: ...] against uploaded_doc_names + org whitelist
    # 8. Return unified dict with all fields + specificity_warning / citation_warnings per priority
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

*Last updated: 2026-04-05 — split from CLAUDE.md v7.5*
