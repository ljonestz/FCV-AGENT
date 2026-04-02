# Express Mode Single-Endpoint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the frontend-chained 3-request express mode with a single `/api/run-express` backend SSE endpoint, and switch to gunicorn+gevent for production serving.

**Architecture:** New backend route runs Stage 1→2→3 sequentially in one SSE generator, reusing all existing extraction/parsing functions. Frontend `runExpress()` is rewritten to consume this single stream. Step-by-step mode is untouched.

**Tech Stack:** Python/Flask backend, vanilla JS frontend, gunicorn+gevent for production, Anthropic SDK for LLM calls.

**Spec:** `docs/superpowers/specs/2026-04-02-express-mode-single-endpoint-design.md`

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `app.py` | Modify (add route at ~line 1960, before `/api/run-deeper`) | New `/api/run-express` route + `_stream_stage()` helper |
| `index.html` | Modify (~lines 2366-2460: `runExpress()`, ~line 2458: `runStage()` signature) | Rewrite `runExpress()` to single SSE consumer; remove `onComplete` from `runStage()` |
| `requirements.txt` | Modify | Add `gunicorn>=21.2.0` and `gevent>=23.9.0` |
| `Procfile` | Modify | Switch to gunicorn command |

---

## Task 1: Add gunicorn + gevent to requirements and Procfile

**Files:**
- Modify: `requirements.txt`
- Modify: `Procfile`

This is the infrastructure change — must happen on the `feat/express-mode` branch.

- [ ] **Step 1: Switch to express-mode branch**

```bash
git checkout feat/express-mode
```

- [ ] **Step 2: Update requirements.txt**

Add two lines at the end of `requirements.txt`:

```
gunicorn>=21.2.0
gevent>=23.9.0
```

Full file should be:
```
flask==3.0.3
anthropic>=0.40.0
python-docx==1.1.2
pypdf>=4.0.0
gunicorn>=21.2.0
gevent>=23.9.0
```

- [ ] **Step 3: Update Procfile**

Replace the single line in `Procfile`:

```
web: gunicorn app:app --worker-class gevent --bind 0.0.0.0:$PORT --timeout 600
```

The `--timeout 600` gives each request up to 10 minutes (covers the full express chain). The `--worker-class gevent` enables non-blocking I/O for long-lived SSE. The existing `app.run()` block at the bottom of `app.py` is still used for local development (`python app.py`) — gunicorn ignores it.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt Procfile
git commit -m "chore: switch to gunicorn+gevent for production SSE reliability"
```

---

## Task 2: Add `_stream_stage()` helper to app.py

**Files:**
- Modify: `app.py` (on `feat/express-mode` branch, add before the `/api/run-deeper` route at ~line 1960)

This helper encapsulates the queue-based keepalive streaming pattern that already exists in `run_stage()`. It runs a single Anthropic streaming call in a background thread and yields SSE events with keepalive pings. The express route (Task 3) will call it once per stage.

- [ ] **Step 1: Add the helper function**

Insert the following function in `app.py` at approximately line 1960 (after the `run_stage` route's closing `except` block, before the `@app.route('/api/run-deeper')` decorator):

```python
def _stream_stage(messages, max_tokens, stage_num):
    """Run one Anthropic streaming call with keepalive pings.

    Yields SSE-formatted strings:
      - {"chunk": "...", "stage": N}  for each text chunk
      - {"keepalive": true}           every 20s if no data flowing

    Returns the full collected text after the generator is exhausted.
    The caller retrieves it via the .collected attribute set on the generator.
    """
    import queue as _q
    collected = []
    stream_q = _q.Queue()

    def _run():
        try:
            with get_client().messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                messages=messages
            ) as s:
                for chunk in s.text_stream:
                    stream_q.put(('chunk', chunk))
            stream_q.put(('done', None))
        except Exception as e:
            stream_q.put(('error', str(e)))

    t = threading.Thread(target=_run, daemon=True)
    t.start()

    while True:
        try:
            kind, payload = stream_q.get(timeout=20)
        except _q.Empty:
            yield f"data: {json.dumps({'keepalive': True})}\n\n"
            continue
        if kind == 'chunk':
            collected.append(payload)
            yield f"data: {json.dumps({'chunk': payload, 'stage': stage_num})}\n\n"
        elif kind == 'done':
            break
        elif kind == 'error':
            raise Exception(payload)

    # Store collected text so the caller can access it after iteration
    _stream_stage._last_result = ''.join(collected)
```

Note: We use `_stream_stage._last_result` as a simple way for the caller to retrieve the collected text after iterating. This avoids the complexity of a custom generator class while keeping the function composable.

- [ ] **Step 2: Verify the existing `run_stage` route still works**

Run locally:
```bash
python app.py
```
Open `http://localhost:5000`, run a step-by-step analysis through Stage 1. Confirm it completes. The new helper is not yet called — this just confirms no syntax errors were introduced.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "refactor: extract _stream_stage() helper for reusable keepalive SSE streaming"
```

---

## Task 3: Add `/api/run-express` backend route

**Files:**
- Modify: `app.py` (add route after `_stream_stage()`, before `/api/run-deeper`)

This is the core change. The route runs all 3 stages in a single SSE generator, reusing existing functions for document processing, research, prompt building, and output parsing.

- [ ] **Step 1: Add the route**

Insert the following route after `_stream_stage()` in `app.py`:

```python
@app.route('/api/run-express', methods=['POST'])
def run_express():
    """Run all 3 stages in a single SSE stream for express mode."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request.'}), 400

        documents = data.get('documents', [])
        if not documents:
            return jsonify({'error': 'Please upload at least one project document.'}), 400

        MAX_ASSISTANT_CHARS = 40000

        def generate():
            # ── Variables that persist across stages ──
            stage1_output = ''
            stage2_output = ''
            doc_type = 'Unknown'
            research_brief_text = ''
            research_country = ''
            conversation_history = []

            try:
                # ════════════════════════════════════════════════════════════
                # STAGE 1 — Context & Extraction
                # ════════════════════════════════════════════════════════════
                yield f"data: {json.dumps({'stage_start': 1})}\n\n"

                project_docs = [d for d in documents if not d.get('isContext')]
                context_docs = [d for d in documents if d.get('isContext')]

                # Pre-extract raw text for all docs
                doc_parts = []
                for doc in project_docs:
                    name = doc.get('name', 'document')
                    file_type = doc.get('type', 'text')
                    raw = doc.get('content', '')
                    if file_type == 'pdf':
                        text, page_count = extract_pdf_text(raw, name)
                    else:
                        text = raw[:MAX_DOC_CHARS]
                        page_count = 0
                    doc_parts.append({'label': 'PROJECT DOCUMENT', 'name': name,
                                      'raw_text': text[:MAX_DOC_CHARS], 'page_count': page_count})
                for doc in context_docs:
                    name = doc.get('name', 'document')
                    file_type = doc.get('type', 'text')
                    raw = doc.get('content', '')
                    if file_type == 'pdf':
                        text, page_count = extract_pdf_text(raw, name)
                    else:
                        text = raw[:MAX_DOC_CHARS]
                        page_count = 0
                    doc_parts.append({'label': 'CONTEXT DOCUMENT', 'name': name,
                                      'raw_text': text[:MAX_DOC_CHARS], 'page_count': page_count})

                # ── Web research phase ──
                try:
                    first_doc_text = doc_parts[0]['raw_text'] if doc_parts else ''
                    yield f"data: {json.dumps({'research_status': 'extracting_country'})}\n\n"
                    fast = get_fast_client()
                    with ThreadPoolExecutor(max_workers=2) as pool:
                        country_future = pool.submit(extract_country_name, first_doc_text, fast)
                        sector_future = pool.submit(extract_sector_name, first_doc_text, fast)
                        research_country = country_future.result()
                        research_sector = sector_future.result()

                    cache_key = f"{research_country.lower().strip()}::{research_sector.lower().strip()}"
                    if cache_key in _research_cache:
                        research_data = _research_cache[cache_key]
                        research_brief_text = research_data['brief']
                        yield f"data: {json.dumps({'research_status': 'cached', 'country': research_country})}\n\n"
                    else:
                        yield f"data: {json.dumps({'research_status': 'searching', 'country': research_country})}\n\n"
                        research_data = run_fcv_web_research(research_country, research_sector, get_research_client())
                        research_brief_text = research_data['brief']
                        _research_cache[cache_key] = research_data

                    yield f"data: {json.dumps({'research_status': 'complete', 'country': research_country, 'brief': research_brief_text})}\n\n"
                except Exception:
                    research_brief_text = ''
                    yield f"data: {json.dumps({'research_status': 'error', 'country': research_country})}\n\n"

                # ── Assemble Stage 1 content_parts ──
                content_parts = []
                context_sep_added = False
                for dp in doc_parts:
                    if dp['label'] == 'CONTEXT DOCUMENT' and not context_sep_added:
                        content_parts.append({"type": "text", "text": "\n\n--- CONTEXTUAL DOCUMENTS ---\n"})
                        context_sep_added = True
                    if len(dp['raw_text']) > STAGE1_EXTRACT_THRESHOLD:
                        yield f"data: {json.dumps({'preprocess': f'Extracting FCV content from {dp[\"name\"]}...'})}\n\n"
                        final_text = extract_fcv_content_haiku(dp['raw_text'], dp['name'], get_research_client())
                    else:
                        final_text = dp['raw_text']
                    suffix = f" ({dp['page_count']} pages)" if dp['page_count'] else ""
                    content_parts.append({"type": "text", "text": f"=== {dp['label']}: {dp['name']}{suffix} ===\n\n{final_text}"})

                if research_brief_text:
                    content_parts.append({"type": "text", "text": (
                        "\n\n--- AUTOMATED FCV WEB RESEARCH (supplemental — uploaded documents take precedence) ---\n"
                        "The following is an automated research brief compiled from public sources via web search. "
                        "It is supplemental only. Where uploaded contextual documents address the same topic, "
                        "those documents take precedence. Use these findings to fill gaps not covered by uploads, "
                        "or to supplement with more recent or different perspectives. "
                        "Label all findings drawn from this source as [From: web research / source type].\n\n"
                        + research_brief_text +
                        "\n--- END AUTOMATED WEB RESEARCH ---\n"
                    )})

                content_parts.append({"type": "text", "text": (
                    "\n\n--- WBG FCV Sensitivity and Responsiveness Guide (always included) ---\n" + FCV_GUIDE +
                    "\n\n--- FCV Operational Playbook — Diagnostics Phase (always included) ---\n" + PLAYBOOK_DIAGNOSTICS +
                    "\n\n--- WBG FCV Strategy Refresh Framework (always included) ---\n" + FCV_REFRESH_FRAMEWORK
                )})

                stage1_prompt = get_prompt_for_stage(1)
                content_parts.append({"type": "text", "text": stage1_prompt})

                stage1_messages = [{"role": "user", "content": content_parts}]

                # ── Stream Stage 1 ──
                yield f"data: {json.dumps({'status': 'preparing_analysis'})}\n\n"
                for event in _stream_stage(stage1_messages, 8000, 1):
                    yield event
                stage1_output = _stream_stage._last_result

                # Extract doc_type from Stage 1 output
                dt_match = re.search(r'%%%DOC_TYPE:\s*([^%\n]+)%%%', stage1_output)
                if dt_match:
                    doc_type = dt_match.group(1).strip()

                # Build truncated history for next stages
                conversation_history = [
                    {"role": "user", "content": "[Stage 1 — project documents and FCV context analysed]"},
                    {"role": "assistant", "content": stage1_output[:MAX_ASSISTANT_CHARS] if len(stage1_output) > MAX_ASSISTANT_CHARS else stage1_output}
                ]

                # ── Stage 1 done event ──
                yield f"data: {json.dumps({'stage_done': 1, 'result': stage1_output, 'history': conversation_history, 'research_brief': research_brief_text, 'research_country': research_country, 'doc_type': doc_type})}\n\n"

                # ════════════════════════════════════════════════════════════
                # STAGE 2 — FCV Assessment
                # ════════════════════════════════════════════════════════════
                yield f"data: {json.dumps({'stage_start': 2})}\n\n"

                stage2_prompt = get_prompt_for_stage(2)
                doc_type_ctx = build_doc_type_context(doc_type, 2)
                if doc_type_ctx:
                    stage2_prompt = doc_type_ctx + "\n\n" + stage2_prompt
                stage2_prompt = (
                    stage2_prompt +
                    "\n\n--- WBG FCV Operational Manual (12 Recommendations, 25 Key Questions, 3 Key Elements) ---\n" +
                    FCV_OPERATIONAL_MANUAL +
                    "\n\n--- WBG FCV Strategy Refresh Framework (4 Shifts) ---\n" +
                    FCV_REFRESH_FRAMEWORK +
                    "\n\n--- WBG FCV Sensitivity and Responsiveness Guide ---\n" +
                    FCV_GUIDE
                )

                # Build messages: prior context + Stage 2 prompt
                stage2_messages = [
                    {"role": "user", "content": f"Prior FCV analysis context:\n\nStage 1 output:\n{conversation_history[1]['content']}\n\nUse this as the basis for the next stage."},
                    {"role": "assistant", "content": "Understood. I will build on this prior analysis."},
                    {"role": "user", "content": stage2_prompt}
                ]

                # ── Stream Stage 2 ──
                for event in _stream_stage(stage2_messages, 16000, 2):
                    yield event
                stage2_output = _stream_stage._last_result

                # Parse Stage 2 output
                stage2_ratings = extract_stage2_ratings(stage2_output)
                under_hood = extract_under_hood(stage2_output)
                s2_parse_error = under_hood.get('error', False) or stage2_ratings.get('error', False)
                s2_parse_error_msg = under_hood.get('message', '') or stage2_ratings.get('message', '')

                # Update conversation history
                s2_truncated = stage2_output[:MAX_ASSISTANT_CHARS] if len(stage2_output) > MAX_ASSISTANT_CHARS else stage2_output
                conversation_history.extend([
                    {"role": "user", "content": stage2_prompt},
                    {"role": "assistant", "content": s2_truncated}
                ])
                if len(conversation_history) > 20:
                    conversation_history = conversation_history[-20:]

                # ── Stage 2 done event ──
                yield f"data: {json.dumps({'stage_done': 2, 'result': stage2_output, 'display_text': under_hood.get('display_text', stage2_output), 'history': conversation_history, 'sensitivity_rating': stage2_ratings.get('sensitivity_rating', ''), 'responsiveness_rating': stage2_ratings.get('responsiveness_rating', ''), 'under_hood': {'recs_table': under_hood.get('recs_table', ''), 'dnh_checklist': under_hood.get('dnh_checklist', ''), 'questions_map': under_hood.get('questions_map', ''), 'evidence_trail': under_hood.get('evidence_trail', '')}, 'parse_error': s2_parse_error, 'parse_error_message': s2_parse_error_msg})}\n\n"

                # ════════════════════════════════════════════════════════════
                # STAGE 3 — Recommendations Note
                # ════════════════════════════════════════════════════════════
                yield f"data: {json.dumps({'stage_start': 3})}\n\n"

                stage3_prompt = get_prompt_for_stage(3)
                doc_type_ctx = build_doc_type_context(doc_type, 3)
                if doc_type_ctx:
                    stage3_prompt = doc_type_ctx + "\n\n" + stage3_prompt

                # Stage-aware playbook injection
                stage_config = STAGE_GUIDANCE_MAP.get(doc_type, STAGE_GUIDANCE_MAP.get('Unknown', {}))
                playbook_phase = stage_config.get('playbook_phase', 'Preparation')
                if playbook_phase == 'Implementation':
                    playbook = PLAYBOOK_IMPLEMENTATION
                elif playbook_phase == 'Closing':
                    playbook = PLAYBOOK_CLOSING
                else:
                    playbook = PLAYBOOK_PREPARATION
                if doc_type == 'ISR':
                    playbook = PLAYBOOK_IMPLEMENTATION + "\n\n" + PLAYBOOK_CLOSING

                timing_opts = stage_config.get('timing_options', ['Preparation'])
                timing_str = ' / '.join(timing_opts) if isinstance(timing_opts, list) else str(timing_opts)

                try:
                    stage3_prompt = stage3_prompt.format(
                        doc_type=doc_type,
                        timing_emphasis=timing_str,
                        playbook_guidance=playbook
                    )
                except KeyError:
                    pass

                stage3_prompt = (
                    stage3_prompt +
                    "\n\n--- WBG FCV Strategy Refresh Framework (4 Shifts) ---\n" +
                    FCV_REFRESH_FRAMEWORK
                )

                # Build Stage 3 messages from conversation history
                stage3_messages = conversation_history + [
                    {"role": "user", "content": stage3_prompt}
                ]

                # ── Stream Stage 3 ──
                for event in _stream_stage(stage3_messages, 16000, 3):
                    yield event
                stage3_output = _stream_stage._last_result

                # Parse Stage 3 output
                uploaded_doc_names = [doc.get('name', '') for doc in documents if doc.get('name')]
                parsed = extract_priorities(stage3_output, uploaded_doc_names)
                stage3_output_clean = clean_stage3_output(stage3_output)
                from datetime import date
                header = DO_NO_HARM_HEADER.format(date=date.today().strftime('%d %B %Y'))
                stage3_output_clean = header + stage3_output_clean

                # Final conversation history
                s3_truncated = stage3_output[:MAX_ASSISTANT_CHARS] if len(stage3_output) > MAX_ASSISTANT_CHARS else stage3_output
                conversation_history.append({"role": "user", "content": stage3_prompt})
                conversation_history.append({"role": "assistant", "content": s3_truncated})
                if len(conversation_history) > 20:
                    conversation_history = conversation_history[-20:]

                # ── Stage 3 done event ──
                yield f"data: {json.dumps({'stage_done': 3, 'result': stage3_output_clean, 'history': conversation_history, 'priorities': parsed.get('priorities', []), 'fcv_rating': parsed.get('fcv_rating', ''), 'fcv_responsiveness_rating': parsed.get('fcv_responsiveness_rating', ''), 'sensitivity_summary': parsed.get('sensitivity_summary', ''), 'responsiveness_summary': parsed.get('responsiveness_summary', ''), 'risk_exposure': parsed.get('risk_exposure'), 'gap_table': extract_gap_table(stage3_output), 'parse_error': parsed.get('error', False), 'parse_error_message': parsed.get('message', '')})}\n\n"

                # ── Express complete ──
                yield f"data: {json.dumps({'express_done': True})}\n\n"

            except Exception as e:
                # Determine which stage failed based on what's been completed
                failed_stage = 1
                if stage1_output and not stage2_output:
                    failed_stage = 2
                elif stage2_output:
                    failed_stage = 3
                yield f"data: {json.dumps({'error': str(e), 'failed_stage': failed_stage})}\n\n"

        return Response(stream_with_context(generate()),
                        mimetype='text/event-stream',
                        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

- [ ] **Step 2: Verify syntax — run the app locally**

```bash
python app.py
```

Confirm the server starts without import errors. The new route exists but is not yet called by the frontend.

- [ ] **Step 3: Quick smoke test with curl**

In a separate terminal, test the endpoint responds (it will fail on missing documents, but confirms routing works):

```bash
curl -X POST http://localhost:5000/api/run-express -H "Content-Type: application/json" -d '{}' -v
```

Expected: HTTP 400 with `{"error": "Please upload at least one project document."}`

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add /api/run-express single-endpoint route for all 3 stages in one SSE stream"
```

---

## Task 4: Rewrite frontend `runExpress()` to use single endpoint

**Files:**
- Modify: `index.html` (~lines 2366-2460: `runExpress()` function, ~line 2458: `runStage()` signature)

- [ ] **Step 1: Rewrite `runExpress()`**

Replace the entire `runExpress()` function (lines ~2366-2410) with:

```javascript
  async function runExpress(){
    if(busy)return;
    busy=true;
    document.getElementById('analysis-panel').style.display='block';
    document.getElementById('stepper-wrap').style.display='none';
    document.getElementById('main').style.display='none';
    showExpressProgress();updateExpressStage(1,'active',null);

    // Read files for upload payload
    const readF=(file,isCtx)=>new Promise((res,rej)=>{
      const isPdf=file.name.toLowerCase().endsWith('.pdf');
      const r=new FileReader();
      if(isPdf){r.onload=e=>res({name:file.name,type:'pdf',content:e.target.result.split(',')[1],isContext:isCtx});r.readAsDataURL(file)}
      else{r.onload=e=>res({name:file.name,type:'text',content:e.target.result,isContext:isCtx});r.readAsText(file)}
      r.onerror=()=>rej(new Error('Could not read '+file.name));
    });

    let payload;
    try{
      payload={documents:[
        ...await Promise.all(pF.map(f=>readF(f,false))),
        ...await Promise.all(cF.map(f=>readF(f,true)))
      ]};
    }catch(e){
      showExpressError(1,'Could not read documents: '+(e.message||e));
      busy=false;return;
    }

    const expressAbort=new AbortController();
    const expressTimeout=setTimeout(()=>expressAbort.abort(new Error('Express analysis timed out after 10 minutes.')),10*60*1000);

    let res;
    try{
      res=await fetch('/api/run-express',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(payload),
        signal:expressAbort.signal
      });
    }catch(e){
      clearTimeout(expressTimeout);
      showExpressError(1,e.name==='AbortError'?(e.message||'Request timed out'):'Could not reach the server.');
      busy=false;return;
    }

    if(!res.ok){
      clearTimeout(expressTimeout);
      let msg='Server error '+res.status;
      try{const d=await res.json();msg=d.error||msg}catch(e){}
      showExpressError(1,msg);busy=false;return;
    }

    const reader=res.body.getReader(),dec=new TextDecoder();
    let buf='';
    let currentStage=1;

    try{
      while(true){
        const{done,value}=await reader.read();
        if(done)break;
        buf+=dec.decode(value,{stream:true});
        const lines=buf.split('\n');buf=lines.pop();

        for(const line of lines){
          if(!line.startsWith('data: '))continue;
          let p;
          try{p=JSON.parse(line.slice(6));}catch(e){continue;}

          // ── Stage start ──
          if(p.stage_start){
            currentStage=p.stage_start;
            updateExpressStage(currentStage,'active',null);
          }

          // ── Research status (Stage 1) ──
          else if(p.research_status){
            let rsMsg='';
            if(p.research_status==='extracting_country') rsMsg='Identifying project country\u2026';
            else if(p.research_status==='searching'&&p.country){researchCountry=p.country;rsMsg='Searching FCV context: '+esc(p.country)+'\u2026';}
            else if(p.research_status==='cached'&&p.country){researchCountry=p.country;rsMsg='Loading cached FCV research\u2026';}
            else if(p.research_status==='complete'){if(p.brief)researchBrief=p.brief;if(p.country)researchCountry=p.country;rsMsg='Research complete \u2014 generating analysis\u2026';}
            else if(p.research_status==='error'){rsMsg='Web research unavailable \u2014 proceeding\u2026';}
            if(rsMsg){const epSum=document.getElementById('ep-summary-1');if(epSum)epSum.innerHTML='<div class="ep-stage-spinner"><div class="ep-spinner-dot"></div><div class="ep-spinner-dot"></div><div class="ep-spinner-dot"></div><span>'+rsMsg+'</span></div>';}
          }

          // ── Preprocess (Stage 1 Haiku extraction) ──
          else if(p.preprocess){
            const epSum=document.getElementById('ep-summary-1');
            if(epSum)epSum.innerHTML='<div class="ep-stage-spinner"><div class="ep-spinner-dot"></div><div class="ep-spinner-dot"></div><div class="ep-spinner-dot"></div><span>'+esc(p.preprocess)+'</span></div>';
          }

          // ── Preparing analysis ──
          else if(p.status==='preparing_analysis'){
            const epSum=document.getElementById('ep-summary-1');
            if(epSum)epSum.innerHTML='<div class="ep-stage-spinner"><div class="ep-spinner-dot"></div><div class="ep-spinner-dot"></div><div class="ep-spinner-dot"></div><span>Generating analysis\u2026</span></div>';
          }

          // ── Streaming chunks (not rendered in express progress, but could be used for preview) ──
          else if(p.chunk){
            // Chunks arrive with p.stage — could buffer for live preview in future
          }

          // ── Keepalive ──
          else if(p.keepalive){/* silent */}

          // ── Stage done ──
          else if(p.stage_done){
            const sn=p.stage_done;

            if(sn===1){
              // Store Stage 1 data
              stageOutputs[1]=p.result;
              hist=p.history||[];stageHists[1]=hist.slice();
              if(p.doc_type&&p.doc_type!=='Unknown'){docType=p.doc_type;updateDocTypeBadge();}
              if(p.research_brief)researchBrief=p.research_brief;
              if(p.research_country)researchCountry=p.research_country;
              const summary1=(docType!=='Unknown'?docType:'Document')+' stage \u00B7 Context extracted';
              updateExpressStage(1,'done',summary1);
              epSafeStore(stageOutputs,stageHists,'1');
            }

            else if(sn===2){
              // Store Stage 2 data
              stageOutputs[2]=p.display_text||p.result;
              hist=p.history||hist;stageHists[2]=hist.slice();
              if(p.sensitivity_rating)fcvRating=p.sensitivity_rating;
              if(p.responsiveness_rating)fcvResponsivenessRating=p.responsiveness_rating;
              if(p.under_hood){stage2UnderHood=p.under_hood;localStorage.setItem('stage2_under_hood',JSON.stringify(p.under_hood));}
              localStorage.setItem('stage2_timestamp',Date.now());
              const sensR=p.sensitivity_rating||'\u2014',respR=p.responsiveness_rating||'\u2014';
              updateExpressStage(2,'done','Sensitivity: '+sensR+' \u00B7 Responsiveness: '+respR);
              epSafeStore(stageOutputs,stageHists,'2');
            }

            else if(sn===3){
              // Store Stage 3 data
              stageOutputs[3]=p.result;
              hist=p.history||hist;stageHists[3]=hist.slice();
              stageGapTable=p.gap_table||null;
              stageRiskExposure=p.risk_exposure||null;
              stageSensitivitySummary=p.sensitivity_summary||'';
              stageResponsivenessSummary=p.responsiveness_summary||'';
              if(p.fcv_rating)fcvRating=p.fcv_rating;
              if(p.fcv_responsiveness_rating)fcvResponsivenessRating=p.fcv_responsiveness_rating;
              if(p.priorities)stageThreePriorities=p.priorities;
              localStorage.setItem('stage3_timestamp',Date.now());
              updateExpressStage(3,'done','Complete');
              epSafeStore(stageOutputs,stageHists,'3');
            }
          }

          // ── Error ──
          else if(p.error){
            clearTimeout(expressTimeout);
            const failedStage=p.failed_stage||currentStage;
            showExpressError(failedStage,p.error);
            busy=false;return;
          }

          // ── Express complete ──
          else if(p.express_done){
            clearTimeout(expressTimeout);
            hideExpressProgress();
            document.getElementById('stepper-wrap').style.display='';
            document.getElementById('main').style.display='';
            curS=3;setStepper(3,'done');
            renderOut(3,stageOutputs[3],false);
            if(stageThreePriorities&&stageThreePriorities.length)initStage3UI();
            if(stage2UnderHood)localStorage.setItem('stage2_under_hood',JSON.stringify(stage2UnderHood));
            enableClickableStepper();
            localStorage.removeItem('fcv_express_stageOutputs');
            localStorage.removeItem('fcv_express_stageHists');
            localStorage.removeItem('fcv_express_curS');
            busy=false;
          }
        }
      }
    }catch(e){
      clearTimeout(expressTimeout);
      showExpressError(currentStage,e.message||'Connection lost');
      busy=false;
    }
  }
```

- [ ] **Step 2: Remove `onComplete` parameter from `runStage()`**

Find the `runStage` function signature (line ~2458):

```javascript
  async function runStage(stage,followOn=null,onComplete=null){
```

Replace with:

```javascript
  async function runStage(stage,followOn=null){
```

Then find the line (~2618) that checks for onComplete:

```javascript
              if(onComplete){busy=false;try{onComplete(stage,p);}catch(e){showExpressError(stage,(e&&e.message)||'Express chain error');busy=false;}return;}
```

Delete this entire line.

- [ ] **Step 3: Update `retryExpressStage()` to use new approach**

Replace the existing `retryExpressStage()` function (lines ~2411-2445) with a simpler version that restarts the full express flow:

```javascript
  function retryExpressStage(stage){
    busy=false;
    // For simplicity, retry restarts the full express chain.
    // Completed stages will complete faster due to research cache.
    if(epTimerInterval)clearInterval(epTimerInterval);
    if(epMessageInterval)clearInterval(epMessageInterval);
    runExpress();
  }
```

Note: A more sophisticated version could resume from a specific stage, but that would require a backend parameter. For now, restarting is safe — web research is cached so Stage 1 reruns faster, and users expect a fresh run after an error.

- [ ] **Step 4: Test locally**

```bash
python app.py
```

1. Open `http://localhost:5000`
2. Upload a test document
3. Select Express mode, click "Begin FCV Analysis"
4. Verify: progress screen appears, stages advance, final output renders
5. Also test: Step-by-step mode still works (should be completely unaffected)

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: rewrite runExpress() to use single /api/run-express SSE endpoint

Replaces the 3-request frontend chain with a single SSE connection.
Removes onComplete callback from runStage() — no longer needed.
Step-by-step mode unchanged."
```

---

## Task 5: Clean up dead code and update CLAUDE.md

**Files:**
- Modify: `index.html` (remove dead `onComplete` references)
- Modify: `CLAUDE.md` (document new route)

- [ ] **Step 1: Search for any remaining `onComplete` references and fix `escHtml` bug**

Search for `onComplete` in `index.html`. If any references remain (other than the function signature change already made), remove them. The `switchToStepByStep()` function should not reference `onComplete` — check it still works correctly. It accesses `stageOutputs` which are populated by the new `runExpress()` via `stage_done` events, so it should work as-is.

Also fix existing bug: `escHtml()` is used in `updateExpressStage()` and `showExpressError()` but is not defined — replace with `esc()` (the actual HTML-escape function defined in the codebase). Search for all `escHtml` occurrences in `index.html` and replace with `esc`.

- [ ] **Step 2: Update CLAUDE.md**

In the `CLAUDE.md` file, add the following to the **5.1 Main Routes** section, after the `/api/run-stage` entry:

```markdown
# Express mode (single SSE stream — all 3 stages)
POST /api/run-express
  Input: {documents[]}
  Output: Single SSE stream with events:
    stage_start: {stage_start: N}
    research_status/preprocess/status: same as run-stage Stage 1
    chunk: {chunk: "text", stage: N}
    stage_done: {stage_done: N, result, history, ...stage-specific parsed data}
    keepalive: {keepalive: true} (every 20s)
    error: {error: "msg", failed_stage: N}
    express_done: {express_done: true}
  Note: Reuses all existing functions. No prompt or parsing changes.
        Frontend runExpress() consumes this single stream.
        Step-by-step mode still uses /api/run-stage.
```

- [ ] **Step 3: Commit**

```bash
git add index.html CLAUDE.md
git commit -m "docs: update CLAUDE.md for /api/run-express route; clean up dead onComplete references"
```

---

## Task 6: End-to-end verification

**Files:** None (testing only)

- [ ] **Step 1: Local test — Express mode**

```bash
python app.py
```

1. Open `http://localhost:5000`
2. Upload a test PDF (a World Bank PAD or similar)
3. Select "Express Analysis"
4. Click "Begin FCV Analysis"
5. Watch progress screen — verify:
   - Stage 1 card shows research status updates
   - Stage 1 completes with checkmark and summary
   - Stage 2 activates, completes with sensitivity/responsiveness ratings
   - Stage 3 activates, completes
   - Progress screen transitions to full Stage 3 output
   - Priority cards render correctly
   - Clickable stepper works (navigate to Stage 1, Stage 2 outputs)
6. Check browser console for errors

- [ ] **Step 2: Local test — Step-by-step mode**

1. Reload page, select "Step-by-Step"
2. Upload same document
3. Run through all 3 stages manually
4. Verify identical behaviour to pre-change

- [ ] **Step 3: Local test — Express error recovery**

1. Start Express mode
2. While Stage 1 is running, disconnect network briefly (or stop the Flask server)
3. Verify error screen appears with "Retry" and "Switch to step-by-step" buttons
4. Click "Switch to step-by-step" — verify it drops to step-by-step mode correctly

- [ ] **Step 4: Push to remote for Render deployment**

```bash
git push origin feat/express-mode
```

- [ ] **Step 5: Verify on Render**

After Render deploys the branch:
1. Open the Render URL
2. Run Express mode with a test document
3. Confirm the full chain completes without timeout
4. This is the critical test — if it passes, the timeout issue is resolved
