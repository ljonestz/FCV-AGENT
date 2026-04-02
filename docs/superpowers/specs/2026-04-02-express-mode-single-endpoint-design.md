# Express Mode — Single Endpoint Redesign

**Date:** 2026-04-02
**Status:** Approved
**Scope:** Replace the frontend-chained 3-request express mode with a single backend SSE endpoint, and switch to a production WSGI server
**Supersedes:** Frontend chain approach from `2026-04-01-express-mode-design.md` (express execution flow only — landing page UI, progress screen, post-express navigation, and session persistence from that spec remain valid)

---

## 1. Problem Statement

Express mode chains 3 sequential SSE connections (`runStage(1)` → `runStage(2)` → `runStage(3)`) through the frontend. On Render's free tier, this fails repeatedly because:

1. **Free instances sleep after 15 min** — cold starts add 30-60s before anything happens
2. **Render's reverse proxy kills connections** during pre-streaming dead time (web research, Haiku extraction, time-to-first-token gaps between stages)
3. **Flask dev server** (`python app.py`) is not production-grade for long-lived SSE
4. **3 separate HTTP requests** means 3 opportunities for the connection to die, plus inter-request gaps where no data flows

10 sessions of fixes (httpx timeouts, ThreadPoolExecutor timeouts, keepalive pings, Haiku extraction, reduced web searches) treated symptoms without addressing the structural issue: multiple HTTP connections through a constrained proxy.

**Goal:** Replace the 3-request chain with a single SSE connection that runs all 3 stages server-side, and switch to a production WSGI server.

---

## 2. Solution: Single `/api/run-express` Endpoint

### 2.1 Overview

A new backend route `/api/run-express` accepts the document payload, then runs Stage 1 → Stage 2 → Stage 3 sequentially within a single SSE stream. The frontend opens one connection and receives progressive updates for all 3 stages.

- Same prompts, same models, same context passing, same parsing — output quality is identical to step-by-step mode
- Keepalive pings flow continuously across all stages — no dead time between requests
- Backend controls the chain — no frontend-to-backend round trips between stages
- Completed stage data is sent incrementally so the frontend can cache it

### 2.2 SSE Event Protocol

All events are JSON-encoded, sent as `data: {json}\n\n`.

| Event type | Payload fields | When sent |
|---|---|---|
| `stage_start` | `{stage_start: N}` | Before each stage begins (N = 1, 2, or 3) |
| `research_status` | `{research_status: "...", country: "..."}` | During Stage 1 web research phase (same payloads as current `/api/run-stage`) |
| `preprocess` | `{preprocess: "message"}` | During Stage 1 doc extraction (same as current) |
| `chunk` | `{chunk: "text", stage: N}` | Streaming LLM text. `stage` field added so frontend knows which stage buffer to append to |
| `stage_done` | `{stage_done: N, result: "...", ...stage-specific data}` | After each stage's LLM stream completes and output is parsed. Contains all parsed data for that stage (see Section 2.3) |
| `keepalive` | `{keepalive: true}` | Every 20s if no data has been sent (covers gaps during web research, TTFT waits, inter-stage transitions) |
| `error` | `{error: "message", failed_stage: N}` | If a stage fails. Includes which stage failed. Previously completed stages' data has already been sent via `stage_done` |
| `express_done` | `{express_done: true}` | All 3 stages completed successfully |

### 2.3 `stage_done` Payloads

**Stage 1 `stage_done`:**
```json
{
  "stage_done": 1,
  "result": "...full Stage 1 output text...",
  "history": [...messages array for context passing...],
  "research_brief": "...",
  "research_country": "Honduras",
  "doc_type": "PAD"
}
```
- `doc_type` extracted from `%%%DOC_TYPE:...%%%` line in Stage 1 output (backend parses it here so the frontend doesn't need to)
- `history` is the truncated conversation history for passing to Stage 2

**Stage 2 `stage_done`:**
```json
{
  "stage_done": 2,
  "result": "...full Stage 2 output text...",
  "display_text": "...cleaned text (delimiters stripped)...",
  "history": [...updated messages array...],
  "sensitivity_rating": "Adequate",
  "responsiveness_rating": "Low",
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

**Stage 3 `stage_done`:**
```json
{
  "stage_done": 3,
  "result": "...full Stage 3 output text (cleaned)...",
  "history": [...final messages array...],
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

### 2.4 Backend Route Structure

```python
@app.route('/api/run-express', methods=['POST'])
def run_express():
    data = request.get_json()
    # Expects: {documents: [...], user_message: "", prompt_overrides: {}}

    def generate():
        # ── Stage 1 ──
        yield stage_start(1)
        # Run web research (with keepalive pings)
        # Build Stage 1 messages (same logic as current run_stage for stage==1)
        # Stream Stage 1 LLM (with keepalive queue)
        # Parse output: extract doc_type from %%%DOC_TYPE:...%%%
        # Build truncated history for Stage 2
        yield stage_done(1, ...)

        # ── Stage 2 ──
        yield stage_start(2)
        # Build Stage 2 messages from Stage 1 history + Stage 2 prompt + reference material
        # Stream Stage 2 LLM (with keepalive queue)
        # Parse: extract_stage2_ratings(), extract_under_hood()
        # Build history for Stage 3
        yield stage_done(2, ...)

        # ── Stage 3 ──
        yield stage_start(3)
        # Build Stage 3 messages from history + stage-aware prompt + playbook
        # Stream Stage 3 LLM (with keepalive queue)
        # Parse: extract_priorities(), clean_stage3_output()
        yield stage_done(3, ...)

        yield express_done()

    return Response(stream_with_context(generate()),
                    mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})
```

The route reuses all existing functions:
- `extract_country_name()`, `extract_sector_name()`, `run_fcv_web_research()`
- `extract_fcv_content_haiku()` for large docs
- `extract_stage2_ratings()`, `extract_under_hood()`, `clean_stage2_output()`
- `extract_priorities()`, `clean_stage3_output()`
- `build_doc_type_context()`, `get_prompt_for_stage()`
- `get_client()`, `get_fast_client()`, `get_research_client()`
- Queue-based keepalive streaming pattern (already implemented)

No existing functions are modified. The route composes them in sequence within a single generator.

### 2.5 Context Passing Between Stages (Server-Side)

This replicates exactly what the frontend currently does between stages:

1. **After Stage 1:** Build `messages` array with Stage 1 output as assistant message. Truncate large content_parts to a placeholder (same as current `run_stage` Stage 1 logic). Extract `doc_type` from output.

2. **After Stage 2:** Append Stage 2 output to messages array. Inject `doc_type` and stage-appropriate Playbook constant for Stage 3 prompt. Same `build_doc_type_context()` + `STAGE_GUIDANCE_MAP` logic as current Stage 3 handling.

3. **History truncation:** Same `MAX_ASSISTANT_CHARS = 40000` truncation. Same 20-message cap.

### 2.6 Error Handling

- **Stage failure:** If any stage's LLM call throws an exception, yield an `error` event with `failed_stage: N`. All `stage_done` events already sent for prior stages remain valid — the frontend has cached them.
- **Stage 2 parse error:** If `extract_under_hood()` fails, set `parse_error: true` in Stage 2's `stage_done` and continue to Stage 3 (same behaviour as current step-by-step mode).
- **Web research failure:** Proceed without research (same graceful degradation as current code).
- **Haiku extraction failure:** Fall back to truncated raw text (same as current code).

---

## 3. Frontend Changes

### 3.1 `runExpress()` Rewrite

Current `runExpress()` chains 3 `runStage()` calls via `onComplete` callbacks. The new version opens a single fetch/SSE connection to `/api/run-express`:

```javascript
async function runExpress() {
  showExpressProgress();
  startTimer();

  const response = await fetch('/api/run-express', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({documents: getDocumentPayload()}),
    signal: expressAbortController.signal
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, {stream: true});

    // Parse SSE events from buffer
    const lines = buffer.split('\n');
    buffer = lines.pop(); // keep incomplete line

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      const data = JSON.parse(line.slice(6));

      if (data.stage_start) handleStageStart(data.stage_start);
      else if (data.chunk) handleChunk(data.chunk, data.stage);
      else if (data.stage_done) handleStageDone(data);
      else if (data.research_status) handleResearchStatus(data);
      else if (data.preprocess) handlePreprocess(data);
      else if (data.error) handleExpressError(data);
      else if (data.express_done) handleExpressDone();
      // keepalive silently ignored
    }
  }
}
```

### 3.2 Event Handlers

- `handleStageStart(n)`: Update progress screen stepper and active stage card. Same visual updates as current code.
- `handleChunk(text, stage)`: Append to `stageBuffers[stage]`. (Not rendered live on progress screen — user sees stage cards advance, not streaming text.)
- `handleStageDone(data)`: Store `stageOutputs[data.stage_done]` in localStorage. Extract stage-specific data (ratings, under_hood, priorities). Update progress screen with completion checkmark and summary line.
- `handleExpressError(data)`: Show error on progress screen for `data.failed_stage`. Offer "Retry" and "Switch to step-by-step" buttons.
- `handleExpressDone()`: Transition to Stage 3 output view. Same as current completion logic.

### 3.3 What Changes in `runStage()`

- Remove the `onComplete` callback parameter (no longer needed)
- `runStage()` reverts to its simpler pre-express form — only used by step-by-step mode
- All express-specific callback wiring is removed

### 3.4 What Stays the Same

Everything from the original express mode spec that isn't the execution chain:
- Landing page mode selection cards
- Progress screen HTML/CSS (stepper, stage cards, timer, rotating messages)
- Post-express clickable stepper and stage navigation
- Re-run banner and refine flow
- Bottom arrow navigation
- Session persistence (same localStorage keys)
- `saveSession()` / `loadSession()` with `analysisMode` field
- Step-by-step mode — completely untouched

---

## 4. Production Server: Gunicorn + Gevent

### 4.1 Procfile Change

```
# Before:
web: python app.py

# After:
web: gunicorn app:app --worker-class gevent --bind 0.0.0.0:$PORT --timeout 600
```

### 4.2 Requirements Addition

```
gunicorn>=21.2.0
gevent>=23.9.0
```

### 4.3 Why This Matters

- `gevent` workers use cooperative multitasking — SSE connections don't block the server
- `--timeout 600` allows each request up to 10 minutes (covers full express chain)
- Flask dev server (`app.run()`) stays in code — used only for local `python app.py` development
- Zero code changes required — gunicorn is a drop-in WSGI server

---

## 5. Files to Modify

| File | Change | Lines (est.) |
|---|---|---|
| `app.py` | Add `/api/run-express` route. No changes to existing routes or functions. | +120-150 |
| `index.html` | Rewrite `runExpress()` to consume single SSE stream. Remove `onComplete` from `runStage()`. Add event handler functions. | ~80 changed |
| `requirements.txt` | Add `gunicorn>=21.2.0` and `gevent>=23.9.0` | +2 |
| `Procfile` | Switch to gunicorn command | 1 line |
| `CLAUDE.md` | Document `/api/run-express` route and SSE protocol | ~30 |

**No changes to:**
- `background_docs.py`
- Prompts (DEFAULT_PROMPTS)
- Step-by-step mode
- Progress screen HTML/CSS
- Post-express navigation
- Session persistence logic
- Any existing parsing functions

---

## 6. Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Single endpoint vs. fix chain | Single endpoint | Eliminates root cause (3 HTTP connections); 10 sessions proved chain approach is unreliable on free tier |
| Stream chunks per stage | Yes, with `stage` field | Allows future live-preview if desired; keeps frontend informed of progress |
| Keepalive interval | 20s | Matches existing implementation; covers Render proxy idle timeouts |
| Gunicorn worker class | gevent | Non-blocking I/O required for long-lived SSE; better than sync workers |
| Error recovery | Send completed stages, halt on failure | Frontend has partial data; user can retry failed stage or switch modes |
| Backend reuse | Compose existing functions, no modifications | Minimises risk; all parsing/extraction logic is proven |
