# Climate Verified HTML Visual Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the approved restrained visual refresh to the verified Climate-FCV live reader and standalone HTML export while preserving all existing assessment prose and analytical behavior.

**Architecture:** Keep the change inside the existing frontend rendering boundary. Refactor `renderClimateVerifiedAssessment()` into a prose-led sequence of semantic report sections, derive tailored guidance deterministically from existing `core_questions[].source` and `sources[]` fields, and rely on `downloadHTML()` reusing the same renderer and collected CSS for export parity. No backend, schema, prompt, model, or DOCX changes are required.

**Tech Stack:** Static HTML/CSS/JavaScript in `index.html`; Python `pytest` contract tests; Node.js execution from Python tests for renderer behavior.

---

## Constraints from the approved design

- Preserve ratings, findings, priorities, detailed narrative, suggested drafting, checks, watch items, caveats, and evidence content.
- Keep context and the executive readout above priorities.
- Keep nuanced prose visible; do not convert the report into short bullets or a dashboard.
- Put smaller Climate-FCV considerations before mechanical document checks.
- Put tailored WBG guidance near the end and include only sources linked to this assessment.
- Add no new tabs, popovers, modals, side panels, schemas, endpoints, dependencies, or model calls.
- Scope every new visual rule beneath `.climate-verified-assessment`.
- Do not touch the restricted OPCS/ESF corpus.

## File map

- Modify: `index.html`
  - Owns verified-reader CSS.
  - Owns `renderClimateVerifiedAssessment()`.
  - Owns the standalone verified HTML export via `downloadHTML()`.
- Modify: `tests/test_climate_lens_frontend.py`
  - Executes extracted JavaScript helpers with Node.
  - Verifies rendered hierarchy, content preservation, deterministic guidance selection, and fallback behavior.
- Modify: `tests/test_sector_lens_app_contract.py`
  - Verifies static structural and CSS/export contracts.
- Modify: `claude.md`
  - Records the new verified-reader presentation contract and version-history entry after implementation.

## Task 1: Lock the reader hierarchy and content-preservation contract

**Files:**
- Modify: `tests/test_climate_lens_frontend.py`
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Add a reusable JavaScript escape helper for renderer tests**

Add this Python helper below `_extract_js_function()` so each Node test uses the same browser-equivalent escaping contract:

```python
def _js_escape_helper() -> str:
    return """
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
"""
```

- [ ] **Step 2: Write the failing renderer hierarchy test**

Add a test that extracts `renderClimateVerifiedAssessment()` and executes it against a compact reader fixture:

```python
def test_verified_reader_visual_refresh_preserves_depth_and_orders_sections():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "renderClimateVerifiedAssessment")
    script = f"""
{_js_escape_helper()}
const renderClimateRelevantGuidance = () => '';
{helper}
const reader = {{
  evidence_status:'approved',
  executive_readout:'The project already addresses important risks.\\n\\nResidual gaps still require attention.',
  climate_sensitivity_rating:{{
    question:'How sensitive is this project to climate and FCV considerations?',
    label:'Moderate',tone:'mid',level:2,
    scale:['Very limited','Moderate','Very strong'],
    description:'The design recognizes key interactions.',
    overview_summary:'The project is directionally sound but not yet fully operationalized.',
    caveat:'This is a subjective judgement.'
  }},
  core_questions:[{{
    question:'How can compound shocks affect delivery?',
    source:'FCV-Sensitive Climate Action Framework',
    summary:'A detailed diagnostic paragraph remains visible.',
    watch:'Monitor access constraints.'
  }}],
  priority_summary:{{statement:'One material action is ready for the team.'}},
  priorities:[{{
    rank:1,title:'Complete the risk narrative',
    narrative:'Detailed priority reasoning remains visible.\\n\\nA second paragraph preserves nuance.',
    current_document_drafting:{{
      target_document:'PCN',target_section:'Risk section',
      text:'Ready-to-use drafting remains visible.'
    }},
    decision:'Revise the narrative.',minimum_action:'Add the missing pathway.',
    responsible_function:'Task team',completion_evidence:'Revised section'
  }}],
  minor_climate_points:[{{
    point:'Clarify benefit sharing.',why:'Capture risks remain.',how_to_check:'Confirm the rule.'
  }}],
  review_readiness_flags:[{{
    flag:'Confirm the instrument type.',why_it_matters:'Terms differ.',
    suggested_verification:'Update the cover page.'
  }}],
  sources:[],
  advisory_notice:'Advisory only.'
}};
const output=renderClimateVerifiedAssessment(reader);
const ordered=[
  'Overview','Core climate-FCV questions','Ranked operational priorities',
  'Points to check before the decision meeting','What to keep an eye on'
].map(label=>output.indexOf(label));
if(ordered.some(index=>index<0) || ordered.some((value,index)=>index && value<=ordered[index-1])) {{
  throw new Error('section order incorrect | '+ordered+' | '+output);
}}
const minor=output.indexOf('Smaller climate and fragility points to consider');
const documentChecks=output.indexOf('Document points to confirm');
if(minor<0 || documentChecks<0 || minor>=documentChecks) throw new Error('check groups reversed | '+output);
for(const expected of [
  'Detailed priority reasoning remains visible.',
  'A second paragraph preserves nuance.',
  'Ready-to-use drafting remains visible.',
  'Recommendation details',
  'climate-report-section','climate-section-heading','climate-section-number'
]) {{
  if(!output.includes(expected)) throw new Error('missing '+expected+' | '+output);
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
```

- [ ] **Step 3: Run the test and verify the expected failure**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_lens_frontend.py::test_verified_reader_visual_refresh_preserves_depth_and_orders_sections -v
```

Expected: FAIL because the new semantic section classes do not exist, there is no Overview heading, and document checks currently precede smaller Climate-FCV points.

- [ ] **Step 4: Commit the failing contract**

```powershell
git add -- tests/test_climate_lens_frontend.py
git commit -m "test: define climate reader visual hierarchy"
```

## Task 2: Implement the prose-led report structure and visual system

**Files:**
- Modify: `index.html`
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Add the semantic section builder inside `renderClimateVerifiedAssessment()`**

Immediately after `statusHtml`, add a local counter and two helpers:

```javascript
let climateSectionNumber=0;
const nextClimateSectionHeading=title=>{
  climateSectionNumber+=1;
  const number=String(climateSectionNumber).padStart(2,'0');
  return `<header class="climate-section-heading"><span class="climate-section-number">${number}</span><h2>${esc(title)}</h2></header>`;
};
const climateReportSection=(title,className,body)=>
  `<section class="climate-report-section ${className}">${nextClimateSectionHeading(title)}${body}</section>`;
```

Keep the counter local so every render begins at `01` and optional sections do not create gaps.

- [ ] **Step 2: Remove presentation-only inline styles from the rating and core-question markup**

Replace the rating return template with semantic classes while preserving every existing field:

```javascript
return `<div class="climate-sens-rating"><p class="climate-rating-question"><strong>${esc(csr.question||'')}</strong></p><p class="climate-rating-label" style="color:${active}">${esc(csr.label||'')}</p><div class="climate-rating-scale">${scale.map((lab,i)=>{const on=(i+1)===level;return `<span class="climate-rating-segment${on?' is-active':''}" style="${on?`--rating-tone:${active}`:''}">${esc(lab)}</span>`;}).join('')}</div><p class="climate-rating-description">${esc(csr.description||'')}</p>${csr.overview_summary?`<p class="climate-overview-summary">${esc(csr.overview_summary)}</p>`:''}<p class="climate-rating-caveat">${esc(csr.caveat||'')}</p></div>`;
```

Render each core question as a quiet subsection, not a `.cj` card:

```javascript
return `<section class="climate-core-question"><h3>${esc(q.question||'')}</h3>${src}${summ}</section>`;
```

Change the source cue to use `.climate-question-source` and retain its current wording and source title.

- [ ] **Step 3: Give points-to-check markup explicit classes and reverse the group order**

Replace `ptcGroupHead`, `ptcItem`, and `flagsHtml` with:

```javascript
const ptcGroup=(title,intro,items)=>items.length
  ?`<section class="climate-check-group"><h3>${esc(title)}</h3>${intro?`<p class="climate-check-intro">${esc(intro)}</p>`:''}${items.join('')}</section>`
  :'';
const ptcItem=(title,body,check)=>`<article class="climate-check-item"><h4>${esc(title)}</h4><p>${esc(body)}</p><p class="climate-check-action"><strong>How to address:</strong> ${esc(check)}</p></article>`;
const minorPointsHtml=ptcGroup(
  'Smaller climate and fragility points to consider',
  'These are smaller, climate- and fragility-specific points that were not large enough to become a recommendation above, but are still worth a look.',
  minorPoints.map(pt=>ptcItem(pt.point||'',pt.why||'',pt.how_to_check||''))
);
const docFlagsHtml=ptcGroup(
  'Document points to confirm','',
  flags.map(flag=>ptcItem(flag.flag||'Point to verify',flag.why_it_matters||'',flag.suggested_verification||''))
);
const flagsHtml=(minorPoints.length||flags.length)
  ?flagsIntro+minorPointsHtml+docFlagsHtml
  :'<p>No points were flagged for verification in this run.</p>';
```

- [ ] **Step 4: Assemble report sections in the approved order**

Change the watch renderer to produce body content only:

```javascript
const watchList=(Array.isArray(r.core_questions)?r.core_questions:[])
  .map(q=>({q:q.question||'',w:q.watch||''})).filter(item=>item.w);
const watchBodyHtml=watchList.length
  ?`<p class="climate-section-lead">These are things to monitor as the project develops. They are not actions to take now - just points to keep in view.</p><ul>${watchList.map(item=>`<li>${item.q?`<strong>${esc(item.q)}</strong> `:''}${esc(item.w)}</li>`).join('')}</ul>`
  :'';
```

At the bottom of the function, assemble sections in this order:

```javascript
const sections=[];
sections.push(climateReportSection(
  'Overview','climate-overview-section',
  `${ratingHtml}<h3 class="climate-subheading">Executive readout</h3><div class="climate-exec">${execHtml}</div>`
));
sections.push(climateReportSection(
  'Core climate-FCV questions','climate-core-questions-section',
  `<p class="climate-section-lead">${esc(CORE_QUESTIONS_INTRO)}</p>${coreQuestionsHtml}`
));
sections.push(climateReportSection(
  'Ranked operational priorities','climate-priorities-section',
  `${prioritySummaryHtml}${priorityHtml}`
));
sections.push(climateReportSection(
  'Points to check before the decision meeting','climate-quick-fixes',flagsHtml
));
if(watchBodyHtml){
  sections.push(climateReportSection('What to keep an eye on','climate-watch',watchBodyHtml));
}
```

Guidance and methodology are appended in Tasks 3 and 4. Return the article with `smokeHtml`, `statusHtml`, `sections.join('')`, and the existing advisory notice.

- [ ] **Step 5: Replace the verified-reader CSS block with the approved restrained system**

Retain the existing priority and drafting rules but replace the global verified-reader heading/card treatment with these scoped foundations:

```css
.out-body .climate-verified-assessment{max-width:820px;margin:0 auto;font-size:14px;color:var(--text);line-height:1.68}
.climate-report-section{margin:0 0 38px}
.climate-section-heading{display:flex;align-items:baseline;gap:12px;margin:0 0 18px;padding:0 0 10px;border-bottom:1px solid #d9e1e8}
.climate-section-number{flex:none;font-family:'Open Sans',sans-serif;font-size:10px;font-weight:700;letter-spacing:.08em;color:var(--wbg-blue)}
.out-body .climate-section-heading h2{font-family:'Open Sans',sans-serif;font-size:22px;font-weight:400;line-height:1.25;letter-spacing:-.015em;text-transform:none;color:var(--wbg-navy);border:0;padding:0;margin:0}
.out-body .climate-section-heading h2::before{display:none}
.climate-section-lead{max-width:720px;color:#4b5563;margin:0 0 18px;line-height:1.65}
.out-body .climate-subheading{font-family:'Open Sans',sans-serif;font-size:16px;font-weight:600;text-transform:none;letter-spacing:0;color:var(--wbg-navy);margin:20px 0 10px}
.climate-sens-rating{padding:0 0 20px;margin:0 0 18px;border-bottom:1px solid #e4e8ed}
.climate-rating-question,.climate-rating-description,.climate-overview-summary,.climate-rating-caveat{margin:0 0 8px}
.climate-rating-label{font-size:24px;font-weight:600;line-height:1.2;margin:4px 0 10px}
.climate-rating-scale{display:flex;gap:3px;max-width:420px;margin:0 0 13px;border-radius:4px;overflow:hidden}
.climate-rating-segment{flex:1;padding:7px 5px;text-align:center;background:#eef0f3;color:#6b7280;font-size:11px}
.climate-rating-segment.is-active{background:var(--rating-tone);color:#fff;font-weight:700}
.climate-rating-caveat{font-size:11px;color:#7b8794}
.climate-exec{background:transparent;border:0;border-left:3px solid var(--wbg-blue);border-radius:0;padding:1px 0 1px 18px;margin:0}
.climate-exec p{font-size:14px;line-height:1.72;color:#1f2937;margin:0 0 12px}
.climate-core-question{background:transparent;border:0;border-top:1px solid #e4e8ed;border-radius:0;box-shadow:none;padding:18px 0 10px;margin:0}
.climate-core-question:first-of-type{border-top:0;padding-top:2px}
.out-body .climate-core-question h3{font-family:'Open Sans',sans-serif;font-size:16px;font-weight:600;line-height:1.45;text-transform:none;letter-spacing:0;color:var(--wbg-navy);margin:0 0 7px}
.climate-question-source{font-size:12px;color:#35789a;margin:0 0 9px}
.climate-check-group{margin:22px 0 0}
.out-body .climate-check-group h3{font-family:'Open Sans',sans-serif;font-size:16px;font-weight:500;text-transform:none;letter-spacing:0;color:var(--wbg-navy);margin:0 0 10px;padding-bottom:7px;border-bottom:1px solid #e4e8ed}
.climate-check-intro{color:#4b5563;margin:0 0 12px}
.climate-check-item{padding:0 0 14px;margin:0 0 14px;border-bottom:1px solid #edf0f3}
.climate-check-item:last-child{border-bottom:0}
.out-body .climate-check-item h4{font-family:'Open Sans',sans-serif;font-size:13px;font-weight:700;text-transform:none;letter-spacing:0;color:var(--wbg-navy);margin:0 0 4px}
.climate-check-item p{margin:0 0 4px}
.climate-check-action{color:#4b5563}
.climate-watch ul{margin:.2em 0 0 1.25em}
.climate-watch li{margin:0 0 9px}
@media(max-width:760px){
  .out-body .climate-verified-assessment{font-size:13.5px}
  .climate-report-section{margin-bottom:30px}
  .out-body .climate-section-heading h2{font-size:19px}
  .climate-section-heading{gap:9px}
  .climate-rating-scale{max-width:none}
  .climate-rating-segment{font-size:10px;padding:7px 3px}
  .climate-priority-card{padding:15px 14px}
}
```

Keep the existing `.climate-priority-card`, `.pc-*`, `.climate-drafting-*`, `.climate-priority-detail`, `.climate-fold`, and `.climate-advisory` rules, adjusting only margins where needed to align with the new section rhythm.

- [ ] **Step 6: Run the hierarchy test and verify it passes**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_lens_frontend.py::test_verified_reader_visual_refresh_preserves_depth_and_orders_sections -v
```

Expected: PASS.

- [ ] **Step 7: Commit the report structure and visual system**

```powershell
git add -- index.html tests/test_climate_lens_frontend.py
git commit -m "feat: refresh verified climate HTML reader"
```

## Task 3: Add deterministic, project-relevant WBG guidance

**Files:**
- Modify: `tests/test_climate_lens_frontend.py`
- Modify: `index.html`
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write the failing guidance-selection test**

Add:

```python
def test_verified_reader_guidance_includes_only_sources_used_by_current_questions():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "normalizeClimateSourceTitle",
            "buildClimateGuidanceItems",
            "renderClimateRelevantGuidance",
        )
    )
    script = f"""
{_js_escape_helper()}
{helpers}
const reader={{
  core_questions:[
    {{question:'How can compound shocks affect delivery?',source:'FCV-Sensitive Climate Action Framework'}},
    {{question:'Can shared benefits reduce tension?',source:'Maximizing the Peace and Social Dividends of Climate Action'}}
  ],
  sources:[
    {{title:'FCV-Sensitive Climate Action Framework',url:'https://www.worldbank.org/framework',description:'A framework description.'}},
    {{title:'Maximizing the Peace and Social Dividends of Climate Action',url:'https://www.worldbank.org/dividends',description:'A peace-dividends description.'}},
    {{title:'Unrelated standard report',url:'https://www.worldbank.org/unrelated',description:'Must not be promoted.'}},
    {{title:'Internal source',url:'',description:'No confirmed public URL.'}}
  ]
}};
const items=buildClimateGuidanceItems(reader);
if(items.length!==2) throw new Error('wrong item count '+items.length);
const output=renderClimateRelevantGuidance(reader);
for(const expected of [
  'Relevant WBG guidance for this project','FCV-Sensitive Climate Action Framework',
  'Maximizing the Peace and Social Dividends of Climate Action',
  'Most useful for following up on','How can compound shocks affect delivery?'
]) {{
  if(!output.includes(expected)) throw new Error('missing '+expected+' | '+output);
}}
for(const forbidden of ['Unrelated standard report','Internal source']) {{
  if(output.includes(forbidden)) throw new Error('promoted '+forbidden+' | '+output);
}}
if(renderClimateRelevantGuidance({{core_questions:[],sources:reader.sources}})!=='') {{
  throw new Error('empty match set should omit guidance');
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
```

- [ ] **Step 2: Run the test and verify the expected failure**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_lens_frontend.py::test_verified_reader_guidance_includes_only_sources_used_by_current_questions -v
```

Expected: FAIL because the three guidance helpers do not exist.

- [ ] **Step 3: Implement title normalization and exact source matching**

Add these helpers immediately before `renderClimateVerifiedAssessment()`:

```javascript
function normalizeClimateSourceTitle(value){
  return String(value||'')
    .normalize('NFKD')
    .toLowerCase()
    .replace(/&/g,' and ')
    .replace(/[^a-z0-9]+/g,' ')
    .trim();
}

function buildClimateGuidanceItems(reader){
  const r=reader&&typeof reader==='object'?reader:{};
  const questions=Array.isArray(r.core_questions)?r.core_questions:[];
  const sources=Array.isArray(r.sources)?r.sources:[];
  return sources.flatMap(source=>{
    const url=String(source&&source.url||'');
    const sourceKey=normalizeClimateSourceTitle(source&&source.title);
    if(!sourceKey||!url.startsWith('https://'))return [];
    const matchedQuestions=questions.filter(question=>
      normalizeClimateSourceTitle(question&&question.source)===sourceKey
    ).map(question=>String(question.question||'').trim()).filter(Boolean).slice(0,2);
    if(!matchedQuestions.length)return [];
    return [{
      title:String(source.title||''),url,
      description:String(source.description||''),
      questions:matchedQuestions
    }];
  });
}

function renderClimateRelevantGuidance(reader){
  const items=buildClimateGuidanceItems(reader);
  if(!items.length)return '';
  return `<div class="climate-guidance-intro">The sources below are selected because they speak directly to issues identified in this assessment. They are not a standard reading list for every project.</div>`+
    items.map(item=>{
      const questionText=item.questions.map(question=>`&ldquo;${esc(question)}&rdquo;`).join(' and ');
      return `<article class="climate-guidance-item"><h3><a href="${esc(item.url)}" target="_blank" rel="noopener">${esc(item.title)}</a></h3>${item.description?`<p>${esc(item.description)}</p>`:''}<p class="climate-guidance-use"><strong>Most useful for following up on:</strong> ${questionText}.</p></article>`;
    }).join('');
}
```

Exact normalized equality is intentional. Do not use substring or fuzzy matching; unmatched literature stays in methodology rather than being guessed into the tailored section.

- [ ] **Step 4: Append guidance after Watch and before methodology**

Inside `renderClimateVerifiedAssessment()`:

```javascript
const relevantGuidanceHtml=renderClimateRelevantGuidance(r);
if(relevantGuidanceHtml){
  sections.push(climateReportSection(
    'Relevant WBG guidance for this project',
    'climate-guidance',
    relevantGuidanceHtml
  ));
}
```

- [ ] **Step 5: Add the guidance styles**

```css
.climate-guidance{background:#fffaf0;border-top:3px solid #b37a09;padding:22px 22px 8px}
.climate-guidance .climate-section-heading{border-bottom-color:#ead9b4}
.climate-guidance-intro{color:#4b5563;margin:0 0 18px;line-height:1.65}
.climate-guidance-item{padding:0 0 17px;margin:0 0 17px;border-bottom:1px solid #eadfc7}
.climate-guidance-item:last-child{border-bottom:0;margin-bottom:0}
.out-body .climate-guidance-item h3{font-family:'Open Sans',sans-serif;font-size:15px;font-weight:600;text-transform:none;letter-spacing:0;margin:0 0 6px}
.climate-guidance-item h3 a{color:#006a9e;text-decoration:none}
.climate-guidance-item h3 a:hover,.climate-guidance-item h3 a:focus-visible{text-decoration:underline}
.climate-guidance-item p{margin:0 0 7px}
.climate-guidance-use{color:#4b5563}
@media(max-width:760px){.climate-guidance{padding:18px 15px 5px}}
```

- [ ] **Step 6: Run both focused renderer tests**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_lens_frontend.py -k "verified_reader_visual_refresh or verified_reader_guidance" -v
```

Expected: 2 passed.

- [ ] **Step 7: Commit tailored guidance**

```powershell
git add -- index.html tests/test_climate_lens_frontend.py
git commit -m "feat: tailor WBG guidance to climate findings"
```

## Task 4: Preserve methodology, responsive behavior, and HTML export parity

**Files:**
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `index.html`
- Test: `tests/test_sector_lens_app_contract.py`
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Add static contracts for scoped CSS and shared export rendering**

Extend `test_verified_climate_ui_contract_is_ranked_and_multidimensional()` with:

```python
assert ".climate-verified-assessment{" in html
assert ".climate-report-section{" in html
assert ".climate-section-heading{" in html
assert ".climate-guidance{" in html
assert "@media(max-width:760px)" in html
assert "buildClimateGuidanceItems" in body
assert "renderClimateRelevantGuidance" in body
assert "minorPointsHtml+docFlagsHtml" in body
```

Add a separate export contract:

```python
def test_verified_climate_html_export_reuses_refreshed_reader_and_styles():
    html = (Path(app_module.__file__).parent / "index.html").read_text(
        encoding="utf-8"
    )
    start = html.index("function downloadHTML")
    end = html.index("\n  function ", start + 20)
    helper = html[start:end]
    assert "renderClimateVerifiedAssessment(climateVerifiedReader)" in helper
    assert "document.querySelectorAll('style')" in helper
    assert 'name="viewport"' in helper
```

- [ ] **Step 2: Run the static contracts**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_sector_lens_app_contract.py -k "verified_climate_ui_contract or verified_climate_html_export" -v
```

Expected: the existing export assertions pass; any class/order assertion not yet satisfied fails and must be corrected in `index.html` without weakening the test.

- [ ] **Step 3: Wrap methodology as the final numbered section**

Keep the existing `provenanceHtml` disclosure content unchanged, but append it after guidance:

```javascript
if(provenanceHtml){
  sections.push(climateReportSection(
    'How this analysis was produced',
    'climate-methodology-section',
    provenanceHtml
  ));
}
```

Change the existing details summary from “How this analysis was produced” to “Method, evidence key, sources, limitations, and diagnostics” so the outer section heading and disclosure do not repeat one another.

- [ ] **Step 4: Verify accessibility semantics and fallbacks in the Node renderer fixture**

Extend the Task 1 fixture assertions:

```javascript
for(const expected of [
  '<article class="climate-verified-assessment">',
  '<section class="climate-report-section',
  '<header class="climate-section-heading">',
  '<details class="climate-priority-detail">'
]) {
  if(!output.includes(expected)) throw new Error('missing semantic markup '+expected);
}
```

Add a second render with no rating, no priorities, no checks, and no guidance. Assert that it renders the executive readout and “No points were flagged for verification in this run.” without `undefined`, `[object Object]`, or an empty guidance section.

- [ ] **Step 5: Run the focused frontend files**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py -q
```

Expected: PASS with no failures.

- [ ] **Step 6: Perform desktop and mobile visual verification**

Use a completed verified Climate-FCV reader payload to render the page locally. Check at approximately `1280 x 900` and `390 x 844`:

- Overview is the first report section.
- Core questions are prose sections, not a two-column tile grid.
- Priority drafting remains fully readable.
- Climate/fragility points precede document checks.
- Guidance is near the end and contains only relevant sources.
- No horizontal overflow occurs.
- Focus rings are visible on literature links and disclosures.

Capture one desktop and one mobile screenshot into the ignored `output/` directory for review; do not commit screenshots unless the user asks.

- [ ] **Step 7: Commit export and accessibility contracts**

```powershell
git add -- index.html tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py
git commit -m "test: protect climate HTML refresh contracts"
```

## Task 5: Update project guidance and run the full regression suite

**Files:**
- Modify: `claude.md`
- Test: repository test suite

- [ ] **Step 1: Update the project version history and frontend contract**

Add a concise version-history entry describing:

```markdown
- **v9.34** - Verified Climate-FCV HTML visual refresh:
  - Replaced the dense card-led reader with a prose-led numbered report hierarchy.
  - Preserved full priority narratives, suggested drafting, checks, watch items, and audit content.
  - Ordered smaller Climate-FCV considerations before document checks.
  - Added deterministic project-relevant WBG guidance using only sources referenced by the current core questions.
  - Kept live and standalone HTML on the same renderer and stylesheet contract; no prompt, schema, backend, or DOCX changes.
```

Also update the frontend-function reference if `claude.md` routes renderer details there. Document the three new helper names and the rule that source matching is exact after normalization.

- [ ] **Step 2: Run whitespace and diff checks**

Run:

```powershell
git diff --check
git status --short
```

Expected: no whitespace errors; only intended files are modified. The existing untracked handover files and `output/` remain unstaged.

- [ ] **Step 3: Run targeted Climate-FCV regressions**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py -q
```

Expected: PASS.

- [ ] **Step 4: Run the full repository suite**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest -q
```

Expected: PASS with zero failures. Record the actual pass count; do not rely on the older baseline recorded in prior specs.

- [ ] **Step 5: Review the final diff against the approved design**

Confirm explicitly:

- No prompt, schema, backend, rating, or recommendation content changed.
- No source is promoted unless referenced by a current core question and backed by an HTTPS URL.
- Minor Climate-FCV points precede document checks.
- Methodology retains the complete evidence and source list.
- All new CSS is scoped to the verified reader.
- The live reader and HTML export still call the same rendering function.

- [ ] **Step 6: Commit documentation and final verification state**

```powershell
git add -- claude.md
git commit -m "docs: record climate HTML reader refresh"
```

- [ ] **Step 7: Push the feature branch after final status review**

Run:

```powershell
git status --short --branch
git log -5 --oneline
git push origin HEAD:refs/heads/feat/climate-reader-lay-comprehensibility
```

Expected: the intended commits are on the existing feature branch; unrelated untracked files remain uncommitted.
