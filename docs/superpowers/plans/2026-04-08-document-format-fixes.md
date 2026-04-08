# Document Format & Extraction Fixes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix three document-handling bugs reported by a user: broken DOCX parsing, silent PDF extraction failures, and missing PPTX support.

**Architecture:** All three fixes follow the same pattern — add a backend extraction function, update the frontend file-reading paths to send binary files as base64 (not plain text), and add the corresponding `file_type` branch in the backend doc-processing loops. The existing `extract_pdf_text()` pattern is the template for DOCX and PPTX extractors.

**Tech Stack:** Python (`python-docx`, `python-pptx`, `pypdf`), vanilla JS (`FileReader`), Flask SSE

---

## File Map

| File | Changes |
|---|---|
| `app.py` | Add `extract_docx_text()`, `extract_pptx_text()`, empty-text warning SSE event, `file_type` branches in 4 doc-processing loops, update `/api/detect-document-type` |
| `index.html` | Update `accept` attributes (2), update `readF()` functions (3 locations), update `fetchFileMetadata()`, surface extraction warnings |
| `requirements.txt` | Add `python-pptx>=1.0.0` |

---

### Task 1: Add DOCX text extraction to backend

**Files:**
- Modify: `app.py:1-21` (imports)
- Modify: `app.py:1315-1336` (add new function after `extract_pdf_text`)

- [ ] **Step 1: Add `docx` import alongside existing imports**

In `app.py`, after the `pypdf` import block (lines 18-21), add:

```python
try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None
```

- [ ] **Step 2: Add `extract_docx_text()` function**

In `app.py`, immediately after `extract_pdf_text()` (after line 1335), add:

```python
def extract_docx_text(b64_data, name):
    """Extract text from a .docx file sent as base64."""
    if DocxDocument is None:
        return f'[python-docx not installed — cannot extract {name}]', 0
    try:
        doc_bytes = base64.standard_b64decode(b64_data)
        doc = DocxDocument(io.BytesIO(doc_bytes))
        parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                parts.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if cells:
                    parts.append(' | '.join(cells))
        full_text = '\n\n'.join(parts)
        if len(full_text) > MAX_DOC_CHARS:
            full_text = full_text[:MAX_DOC_CHARS] + (
                f'\n\n[DOCX read limit reached at {MAX_DOC_CHARS // 1000}k chars.]'
            )
        return full_text, len(doc.paragraphs)
    except Exception as e:
        return f'[Could not extract text from {name}: {str(e)}]', 0
```

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add DOCX text extraction via python-docx"
```

---

### Task 2: Add PPTX text extraction to backend

**Files:**
- Modify: `app.py:18-21` (imports)
- Modify: `app.py` (after the new `extract_docx_text` from Task 1)
- Modify: `requirements.txt`

- [ ] **Step 1: Add `python-pptx` to requirements**

In `requirements.txt`, add after the `python-docx` line:

```
python-pptx>=1.0.0
```

- [ ] **Step 2: Add `pptx` import**

In `app.py`, after the `docx` import block added in Task 1, add:

```python
try:
    from pptx import Presentation
except ImportError:
    Presentation = None
```

- [ ] **Step 3: Add `extract_pptx_text()` function**

In `app.py`, immediately after `extract_docx_text()`, add:

```python
def extract_pptx_text(b64_data, name):
    """Extract text from a .pptx file sent as base64."""
    if Presentation is None:
        return f'[python-pptx not installed — cannot extract {name}]', 0
    try:
        pptx_bytes = base64.standard_b64decode(b64_data)
        prs = Presentation(io.BytesIO(pptx_bytes))
        parts = []
        for slide_num, slide in enumerate(prs.slides, 1):
            slide_texts = []
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for para in shape.text_frame.paragraphs:
                        text = para.text.strip()
                        if text:
                            slide_texts.append(text)
                if shape.has_table:
                    for row in shape.table.rows:
                        cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                        if cells:
                            slide_texts.append(' | '.join(cells))
            if slide_texts:
                parts.append(f'[Slide {slide_num}]\n' + '\n'.join(slide_texts))
        full_text = '\n\n'.join(parts)
        slide_count = len(prs.slides)
        if len(full_text) > MAX_DOC_CHARS:
            full_text = full_text[:MAX_DOC_CHARS] + (
                f'\n\n[PPTX read limit reached at {MAX_DOC_CHARS // 1000}k chars of {slide_count} slides.]'
            )
        return full_text, slide_count
    except Exception as e:
        return f'[Could not extract text from {name}: {str(e)}]', 0
```

- [ ] **Step 4: Commit**

```bash
git add app.py requirements.txt
git commit -m "feat: add PPTX text extraction via python-pptx"
```

---

### Task 3: Update backend doc-processing loops to handle DOCX and PPTX types

**Files:**
- Modify: `app.py:1688-1709` (run-stage doc loop)
- Modify: `app.py:2087-2108` (run-express doc loop)

There are 4 identical doc-processing blocks (2 in run-stage for project/context docs, 2 in run-express). Each currently has:

```python
if file_type == 'pdf':
    text, page_count = extract_pdf_text(raw, name)
else:
    text = raw[:MAX_DOC_CHARS]
    page_count = 0
```

- [ ] **Step 1: Update the run-stage project docs loop (line ~1692)**

Replace the `if/else` block at lines 1692-1696 with:

```python
                if file_type == 'pdf':
                    text, page_count = extract_pdf_text(raw, name)
                elif file_type == 'docx':
                    text, page_count = extract_docx_text(raw, name)
                elif file_type == 'pptx':
                    text, page_count = extract_pptx_text(raw, name)
                else:
                    text = raw[:MAX_DOC_CHARS]
                    page_count = 0
```

- [ ] **Step 2: Update the run-stage context docs loop (line ~1703)**

Apply the same change to the context docs loop at lines 1703-1707.

- [ ] **Step 3: Update the run-express project docs loop (line ~2091)**

Apply the same change at lines 2091-2095.

- [ ] **Step 4: Update the run-express context docs loop (line ~2102)**

Apply the same change at lines 2102-2106.

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat: route DOCX and PPTX files to new extractors in stage and express modes"
```

---

### Task 4: Update `/api/detect-document-type` route for DOCX and PPTX

**Files:**
- Modify: `app.py:1609-1637` (detect-document-type route)

The route currently accepts `doc_b64` (PDF) or `doc_text` (everything else). It needs to also handle base64-encoded DOCX and PPTX files.

- [ ] **Step 1: Update the route to accept a `doc_type` field and extract accordingly**

Replace the text/b64 branching logic at lines 1621-1627 with:

```python
        file_type = data.get('file_type', 'text')
        if file_type == 'pdf' and 'doc_b64' in data:
            text, _ = extract_pdf_text(data['doc_b64'], data.get('doc_name', 'document.pdf'))
        elif file_type == 'docx' and 'doc_b64' in data:
            text, _ = extract_docx_text(data['doc_b64'], data.get('doc_name', 'document.docx'))
        elif file_type == 'pptx' and 'doc_b64' in data:
            text, _ = extract_pptx_text(data['doc_b64'], data.get('doc_name', 'document.pptx'))
        elif 'doc_b64' in data:
            # Legacy fallback: assume PDF if doc_b64 present without file_type
            text, _ = extract_pdf_text(data['doc_b64'], data.get('doc_name', 'document.pdf'))
        elif 'doc_text' in data:
            text = data['doc_text']
        else:
            return jsonify({'error': 'doc_text or doc_b64 required'}), 400
```

- [ ] **Step 2: Add empty-text detection after extraction**

After the extraction block above and before `doc_type = detect_document_type_from_text(...)` (line 1628), add:

```python
        # Detect empty extraction (e.g. scanned PDF, corrupted file)
        stripped = text.strip() if not text.startswith('[Could not extract') else ''
        if len(stripped) < 100 and not text.startswith('[Could not extract'):
            extraction_status = 'empty'
        elif text.startswith('[Could not extract'):
            extraction_status = 'failed'
        else:
            extraction_status = 'ok'
```

Then update the existing `extraction_status` assignment (line 1630) — remove it, since we now compute it above. The return block becomes:

```python
        word_count = len(text.split()) if extraction_status == 'ok' else 0
        doc_type = detect_document_type_from_text(text, get_client()) if extraction_status == 'ok' else 'Unknown'
        return jsonify({
            'document_type': doc_type,
            'word_count': word_count,
            'extraction_status': extraction_status
        })
```

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: detect-document-type route handles DOCX, PPTX, and empty extractions"
```

---

### Task 5: Update frontend file-reading to send DOCX/PPTX as base64

**Files:**
- Modify: `index.html:1823` (project file accept attribute)
- Modify: `index.html:1834` (context file accept attribute)
- Modify: `index.html:2211-2234` (`fetchFileMetadata` function)
- Modify: `index.html:2340-2345` (Express mode `readF`)
- Modify: `index.html:2570-2574` (Step-by-step mode `readF`)

The key change: DOCX and PPTX files must be read as `DataURL` (base64), not `readAsText`. We introduce a helper to detect binary file types.

- [ ] **Step 1: Update accept attributes to include PPTX**

Line 1823 — change:
```html
<input type="file" id="ip" name="project_doc" multiple accept=".pdf,.txt,.docx,.doc,.md">
```
to:
```html
<input type="file" id="ip" name="project_doc" multiple accept=".pdf,.txt,.docx,.doc,.pptx,.ppt,.md">
```

Line 1834 — change:
```html
<input type="file" id="ic" name="context_doc" multiple accept=".pdf,.txt,.docx,.doc,.md">
```
to:
```html
<input type="file" id="ic" name="context_doc" multiple accept=".pdf,.txt,.docx,.doc,.pptx,.ppt,.md">
```

- [ ] **Step 2: Add a file-type detection helper**

Add this helper function near the top of the `<script>` block (before `renderChips`), or just before `fetchFileMetadata`:

```javascript
function detectFileType(fileName) {
    const ext = fileName.toLowerCase().split('.').pop();
    if (ext === 'pdf') return 'pdf';
    if (ext === 'docx' || ext === 'doc') return 'docx';
    if (ext === 'pptx' || ext === 'ppt') return 'pptx';
    return 'text';
}
function isBinaryType(ft) { return ft === 'pdf' || ft === 'docx' || ft === 'pptx'; }
```

- [ ] **Step 3: Update `fetchFileMetadata` (lines 2211-2234)**

Replace the `isPdf` branching with:

```javascript
  async function fetchFileMetadata(file) {
    try {
      const ft = detectFileType(file.name);
      let payload;
      if (isBinaryType(ft)) {
        await new Promise((res, rej) => {
          const r = new FileReader();
          r.onload = e => {
            payload = { doc_b64: e.target.result.split(',')[1], doc_name: file.name, file_type: ft };
            res();
          };
          r.onerror = rej;
          r.readAsDataURL(file);
        });
      } else {
        await new Promise((res, rej) => {
          const r = new FileReader();
          r.onload = e => {
            payload = { doc_text: e.target.result.slice(0, 10000), file_type: ft };
            res();
          };
          r.onerror = rej;
          r.readAsText(file);
        });
      }
      const resp = await fetch('/api/detect-document-type', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!resp.ok) return;
      const data = await resp.json();
      fileMetadata[file.name] = {
        word_count: data.word_count || 0,
        doc_type: data.doc_type || data.document_type || 'Unknown',
        extraction_status: data.extraction_status || 'ok'
      };
      renderChips();
    } catch(e) {
      // Metadata fetch failed — no update to chip, no error shown (non-blocking)
    }
  }
```

- [ ] **Step 4: Update Express mode `readF` (lines 2340-2345)**

Replace:
```javascript
    const readF=(file,isCtx)=>new Promise((res,rej)=>{
      const isPdf=file.name.toLowerCase().endsWith('.pdf');
      const r=new FileReader();
      if(isPdf){r.onload=e=>res({name:file.name,type:'pdf',content:e.target.result.split(',')[1],isContext:isCtx});r.readAsDataURL(file)}
      else{r.onload=e=>res({name:file.name,type:'text',content:e.target.result,isContext:isCtx});r.readAsText(file)}
      r.onerror=()=>rej(new Error('Could not read '+file.name));
    });
```

with:

```javascript
    const readF=(file,isCtx)=>new Promise((res,rej)=>{
      const ft=detectFileType(file.name);
      const r=new FileReader();
      if(isBinaryType(ft)){r.onload=e=>res({name:file.name,type:ft,content:e.target.result.split(',')[1],isContext:isCtx});r.readAsDataURL(file)}
      else{r.onload=e=>res({name:file.name,type:'text',content:e.target.result,isContext:isCtx});r.readAsText(file)}
      r.onerror=()=>rej(new Error('Could not read '+file.name));
    });
```

- [ ] **Step 5: Update Step-by-step mode `readF` (lines 2570-2574)**

Apply the exact same replacement as Step 4 to the `readF` inside `runStage()` at lines 2570-2574.

- [ ] **Step 6: Commit**

```bash
git add index.html
git commit -m "feat: frontend sends DOCX and PPTX as base64, adds PPTX to accept list"
```

---

### Task 6: Surface extraction warnings in frontend chips

**Files:**
- Modify: `index.html:2186-2188` (chip rendering for extraction status)

The chip already shows a red error for `extraction_status === 'failed'`. We need to also handle `'empty'` (scanned PDFs that extract to near-zero text).

- [ ] **Step 1: Update the `renderChips` extraction_status block**

Replace lines 2187-2188:
```javascript
        if (meta.extraction_status === 'failed') {
          metaHtml = `<span class="chip-meta chip-meta-error">Could not extract text — may be scanned or password-protected. Try uploading a DOCX version.</span>`;
```

with:

```javascript
        if (meta.extraction_status === 'failed') {
          metaHtml = `<span class="chip-meta chip-meta-error">Could not extract text — may be scanned or password-protected. Try uploading a text-based version.</span>`;
        } else if (meta.extraction_status === 'empty') {
          metaHtml = `<span class="chip-meta chip-meta-error">Very little text extracted — this may be a scanned document. Try uploading a text-based version.</span>`;
```

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "feat: show warning chip for empty/scanned document extractions"
```

---

### Task 7: Add extraction warning SSE events during analysis

**Files:**
- Modify: `app.py:1684-1709` (run-stage doc loop — collect warnings)
- Modify: `app.py:1775+` (run-stage `generate()` — yield warnings)
- Modify: `app.py:2085-2108` (run-express doc loop — collect warnings)
- Modify: `app.py:2067+` (run-express `generate()` — yield warnings)

**Important context:** The doc-processing loops (lines 1684-1709 and 2085-2108) are **outside** the `generate()` inner functions (which start at lines 1775 and 2067 respectively). This means we cannot `yield` SSE events directly from the doc loop. Instead, collect warnings into a list, then yield them early inside `generate()`.

- [ ] **Step 1: Add a helper to check extraction quality**

In `app.py`, after the extraction functions and before the routes, add:

```python
def _check_extraction(text, name):
    """Return a warning string if extracted text is empty or an error, else None."""
    if text.startswith('[Could not extract'):
        return f'{name}: could not extract text — may be scanned or password-protected'
    stripped = text.strip()
    if len(stripped) < 100:
        return f'{name}: very little text extracted — may be a scanned document'
    return None
```

- [ ] **Step 2: Collect warnings in run-stage doc processing (lines 1684-1709)**

Before the doc loop (after `doc_parts = []` at line 1687), add:

```python
            extraction_warnings = []
```

After each `doc_parts.append(...)` call (lines 1697-1698 and 1708-1709), add:

```python
                warning = _check_extraction(text, name)
                if warning:
                    extraction_warnings.append(warning)
```

- [ ] **Step 3: Yield warnings inside run-stage `generate()` (line 1775+)**

Inside `generate()`, just after the initial `yield f"data: {json.dumps({'ping': True})}\n\n"` (line 1780), add:

```python
                for w in extraction_warnings:
                    yield f"data: {json.dumps({'extraction_warning': w})}\n\n"
```

The `extraction_warnings` list is accessible in `generate()` via closure over the enclosing `run_stage()` scope.

- [ ] **Step 4: Apply the same pattern in run-express (lines 2085-2108, 2067+)**

Collect `extraction_warnings` in the express doc loop (same as Step 2), and yield them early inside the express `generate()` function.

- [ ] **Step 5: Handle `extraction_warning` SSE event in frontend**

In `index.html`, find the SSE event handler in `runStage()` (where it processes `data.research_status`, `data.token`, etc.) and add handling for the new event:

```javascript
if (data.extraction_warning) {
    const warnDiv = document.createElement('div');
    warnDiv.className = 'callout warn ani';
    warnDiv.innerHTML = `<div class="callout-icon">⚠️</div><div class="callout-body"><strong>Document warning:</strong> ${data.extraction_warning}. Consider uploading a text-based version for better results.</div>`;
    document.getElementById('stage-disp').insertBefore(warnDiv, document.getElementById('stage-disp').querySelector('.load-card'));
}
```

Add the same handler in the Express mode SSE event processing loop.

- [ ] **Step 6: Commit**

```bash
git add app.py index.html
git commit -m "feat: emit SSE extraction warnings for empty or unreadable documents"
```

---

### Task 9: Smoke test

- [ ] **Step 1: Install new dependency**

```bash
pip install python-pptx>=1.0.0
```

- [ ] **Step 2: Start the local server**

```bash
python app.py
```

- [ ] **Step 3: Test DOCX upload**

Upload a `.docx` Word document. Verify:
- Chip shows word count and document type (not "Could not extract")
- Stage 1 output references content from the document (not garbled text)
- Country extraction identifies the correct country

- [ ] **Step 4: Test PPTX upload**

Upload a `.pptx` PowerPoint file. Verify:
- File is accepted (no browser rejection)
- Chip shows word count
- Stage 1 output references slide content

- [ ] **Step 5: Test scanned/empty PDF**

Upload a scanned (image-only) PDF. Verify:
- Chip shows the "very little text extracted" warning
- SSE warning banner appears during analysis

- [ ] **Step 6: Test normal PDF (regression)**

Upload a standard text-based PDF. Verify everything still works as before.

- [ ] **Step 7: Final commit**

```bash
git add -A
git commit -m "chore: verify all document format fixes working"
```
