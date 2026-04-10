# Express Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add dual-workflow mode (Express / Step-by-Step) to the FCV Project Screener so users can choose between an automated full-pipeline run or the existing interactive stage-by-stage flow.

**Architecture:** Frontend-only change. A new `runExpress()` function chains `runStage(1)` → `runStage(2)` → `runStage(3)` via an `onComplete` callback parameter added to `runStage()`. No backend modifications. All new UI (mode cards, progress screen, stage navigation) is added to `index.html`.

**Tech Stack:** Vanilla JavaScript, CSS (within `<style>` blocks in index.html), HTML. WBG Design System palette. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-04-01-express-mode-design.md`

---

## File Map

All changes are in a single file:

| File | Action | Responsibility |
|------|--------|---------------|
| `index.html` | Modify | CSS styles, HTML sections, JS functions for mode selection, express chain, progress screen, stage navigation, session persistence |
| `CLAUDE.md` | Modify | Document dual-mode architecture |

**Line references** (approximate, will shift as tasks are applied):
- CSS: Lines 8–1446 (two `<style>` blocks)
- Landing HTML: Lines 1648–1715 (upload panel)
- Stepper HTML: Lines 1635–1642
- JS state variables: Lines 1731–1737, 3017–3051
- `startAnalysis()`: Lines 2049–2086
- `runStage()`: Lines 2088–2289
- `renderOut()`: Lines 2478–2648
- `goBack()`: Lines 2676–2688
- `setStepper()`: Lines 2767–2775
- `saveSession()`: Lines 1759–1776
- `loadSession()`: Lines 1786–1844

---

### Task 1: Add CSS Styles for Mode Cards, Progress Screen, and Stage Navigation

**Files:**
- Modify: `index.html` — CSS section (before closing `</style>` tag near line 1323)

This task adds ALL new CSS at once. Later tasks add HTML/JS that reference these classes.

- [ ] **Step 1: Add mode selection card styles**

Insert before the closing `</style>` tag (around line 1323):

```css
/* ── Express/Step-by-Step Mode Selection ── */
.mode-section{border-top:1px solid var(--wbg-gray-100);padding-top:20px;margin-top:4px;margin-bottom:20px}
.mode-section-label{font-size:12px;font-weight:700;color:var(--wbg-navy);margin-bottom:12px;display:flex;align-items:center;gap:8px}
.mode-section-label svg{color:var(--wbg-cyan)}
.mode-cards{display:flex;gap:12px}
.mode-card{flex:1;border-radius:6px;padding:16px 18px;cursor:pointer;transition:all .2s ease;position:relative;border:1.5px solid var(--wbg-gray-100);background:var(--wbg-gray-50)}
.mode-card:hover{border-color:#B0C4D8}
.mode-card.selected{border-color:var(--wbg-cyan);background:#fff;box-shadow:0 0 0 1px rgba(0,157,218,.1)}
.mode-radio{width:16px;height:16px;border-radius:50%;border:2px solid var(--border);position:absolute;top:16px;right:16px;transition:all .2s}
.mode-card.selected .mode-radio{border-color:var(--wbg-cyan);background:var(--wbg-cyan);box-shadow:inset 0 0 0 2.5px #fff}
.mode-badge{display:inline-block;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;padding:2px 7px;border-radius:3px;margin-bottom:8px}
.mode-badge-default{background:var(--wbg-gray-100);color:var(--wbg-gray-500)}
.mode-badge-rec{background:var(--wbg-navy);color:#fff}
.mode-title{font-size:14px;font-weight:700;color:var(--wbg-navy);margin-bottom:4px;padding-right:24px}
.mode-desc{font-size:12px;color:var(--wbg-gray-500);line-height:1.5;margin-bottom:10px}
.mode-time{font-size:11px;color:#9CA3AF;font-weight:600;display:flex;align-items:center;gap:5px}
```

- [ ] **Step 2: Add express progress screen styles**

Append immediately after the mode card styles:

```css
/* ── Express Progress Screen ── */
.express-progress{display:none;max-width:680px;width:100%;margin:0 auto;padding:48px 32px 40px}
.express-progress.visible{display:block}
.ep-accent{width:100%;height:4px;background:linear-gradient(90deg,#002244 0%,#009FDA 50%,#002244 100%)}
.ep-header{text-align:center;margin-bottom:40px}
.ep-header h2{font-size:22px;font-weight:700;color:var(--wbg-navy);letter-spacing:-.3px;margin-bottom:8px}
.ep-header p{font-size:13px;color:var(--wbg-gray-500);line-height:1.5}
.ep-stepper{display:flex;align-items:center;justify-content:center;margin-bottom:24px;padding:0 12px}
.ep-step-node{display:flex;flex-direction:column;align-items:center;width:120px}
.ep-step-circle{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;transition:all .4s ease}
.ep-step-circle.done{background:var(--wbg-navy);color:#fff}
.ep-step-circle.active{background:#fff;color:var(--wbg-cyan);border:2.5px solid var(--wbg-cyan);box-shadow:0 0 0 4px rgba(0,157,218,.12)}
.ep-step-circle.pending{background:#fff;color:#C4C9D1;border:2px solid #D1D5DB}
.ep-step-label{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.8px;margin-top:8px;text-align:center;line-height:1.3}
.ep-step-label.done{color:var(--wbg-navy)}
.ep-step-label.active{color:var(--wbg-cyan)}
.ep-step-label.pending{color:#C4C9D1}
.ep-step-connector{flex:1;height:2px;margin:0 4px;margin-bottom:26px;max-width:80px}
.ep-step-connector.done{background:var(--wbg-navy)}
.ep-step-connector.pending{background:#E5E7EB}
.ep-step-connector.active{background:linear-gradient(90deg,#002244,#009FDA)}
.ep-progress-bar{width:100%;height:3px;background:var(--wbg-gray-100);border-radius:2px;margin-bottom:32px;overflow:hidden}
.ep-progress-fill{height:100%;background:linear-gradient(90deg,#002244,#009FDA);border-radius:2px;width:0;transition:width 1s ease}
.ep-stage-cards{display:flex;flex-direction:column;gap:10px;margin-bottom:24px}
.ep-stage-card{border-radius:6px;padding:16px 20px;transition:all .4s ease}
.ep-stage-card.done{background:#fff;border:1px solid #E5E7EB;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.ep-stage-card.active{background:#fff;border:1px solid var(--wbg-cyan);box-shadow:0 1px 3px rgba(0,157,218,.1),0 0 0 1px rgba(0,157,218,.08)}
.ep-stage-card.pending{background:var(--wbg-gray-50);border:1px solid var(--wbg-gray-100);opacity:.55}
.ep-stage-card.error{background:#FEF2F2;border:1px solid #FCA5A5}
.ep-stage-header{display:flex;align-items:center;justify-content:space-between}
.ep-stage-title{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.7px}
.ep-stage-title.done{color:var(--wbg-navy)}
.ep-stage-title.active{color:var(--wbg-cyan)}
.ep-stage-title.pending{color:#9CA3AF}
.ep-stage-title.error{color:#DC2626}
.ep-stage-check{width:20px;height:20px;border-radius:50%;background:var(--wbg-navy);color:#fff;display:flex;align-items:center;justify-content:center;font-size:11px}
.ep-stage-summary{font-size:13px;color:#4B5563;margin-top:6px;line-height:1.5}
.ep-stage-spinner{display:flex;align-items:center;gap:8px;margin-top:8px;font-size:13px;color:var(--wbg-gray-500)}
.ep-spinner-dot{width:6px;height:6px;background:var(--wbg-cyan);border-radius:50%;animation:epPulse 1.4s ease-in-out infinite}
.ep-spinner-dot:nth-child(2){animation-delay:.2s}
.ep-spinner-dot:nth-child(3){animation-delay:.4s}
@keyframes epPulse{0%,80%,100%{opacity:.25;transform:scale(.8)}40%{opacity:1;transform:scale(1.2)}}
.ep-timer{display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:28px;font-size:12px;color:#9CA3AF}
.ep-timer .elapsed{font-variant-numeric:tabular-nums;font-weight:600;color:var(--wbg-gray-500)}
.ep-message-card{text-align:center;padding:20px 24px;background:#fff;border:1px solid var(--wbg-gray-100);border-radius:6px;box-shadow:0 1px 2px rgba(0,0,0,.03);transition:opacity .5s ease}
.ep-message-card.fade-out{opacity:0}
.ep-message-icon{font-size:22px;margin-bottom:8px;filter:grayscale(30%)}
.ep-message-text{font-size:13px;color:var(--wbg-gray-500);font-style:italic;line-height:1.5}
.ep-bottom-note{text-align:center;margin-top:24px;font-size:11px;color:#9CA3AF;line-height:1.5}
.ep-error-actions{display:flex;gap:8px;margin-top:12px}
.ep-error-actions .btn{font-size:12px;padding:6px 14px}
```

- [ ] **Step 3: Add post-express navigation styles**

Append immediately after the progress screen styles:

```css
/* ── Post-Express Stage Navigation ── */
.stepper-clickable .step{cursor:pointer;transition:transform .15s ease}
.stepper-clickable .step:hover{transform:translateY(-2px)}
.stepper-clickable .step.current .step-num{background:var(--wbg-cyan);color:#fff;box-shadow:0 0 0 4px rgba(0,157,218,.15)}
.stepper-hint{text-align:center;font-size:11px;color:#9CA3AF;margin-top:-8px;margin-bottom:12px}
.rerun-banner{display:flex;align-items:center;gap:12px;padding:14px 20px;background:#FFFBEB;border:1px solid #FDE68A;border-radius:6px;margin-bottom:16px}
.rerun-banner-icon{font-size:18px;flex-shrink:0}
.rerun-banner-text{flex:1;font-size:12px;color:#92400E;line-height:1.5}
.rerun-banner-text strong{color:#92400E}
.rerun-btn{flex-shrink:0;padding:7px 16px;background:var(--wbg-navy);color:#fff;border:none;border-radius:5px;font-size:12px;font-weight:600;cursor:pointer;font-family:'Open Sans',sans-serif;transition:background .2s}
.rerun-btn:hover{background:#003366}
.read-only-badge{display:inline-block;font-size:10px;font-weight:600;color:var(--wbg-gray-500);background:var(--wbg-gray-100);padding:3px 10px;border-radius:4px;margin-bottom:8px}
.stage-nav-arrows{display:flex;justify-content:space-between;align-items:center;margin-top:16px}
.stage-nav-btn{display:flex;align-items:center;gap:6px;padding:8px 16px;background:#fff;border:1px solid #D1D5DB;border-radius:6px;font-size:12px;font-weight:600;color:var(--wbg-navy);cursor:pointer;font-family:'Open Sans',sans-serif;transition:all .2s}
.stage-nav-btn:hover{background:var(--wbg-gray-50);border-color:var(--wbg-cyan);color:var(--wbg-cyan)}
.stage-nav-btn.primary{background:var(--wbg-cyan);border-color:var(--wbg-cyan);color:#fff}
.stage-nav-btn.primary:hover{background:#0088C7}
@media(max-width:640px){.mode-cards{flex-direction:column}}
```

- [ ] **Step 4: Verify no CSS syntax errors**

Open the app locally (`python app.py`), load the page, open browser DevTools → Console. Confirm no CSS parse errors. The page should render identically to before since no HTML references the new classes yet.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: add CSS styles for express mode, progress screen, and stage navigation"
```

---

### Task 2: Add Mode Selection HTML to Landing Page

**Files:**
- Modify: `index.html` — HTML section inside `#upload-panel` (around line 1703)

- [ ] **Step 1: Insert mode selection section between confidentiality notice and upload-foot**

Find the closing `</div>` of the `confidential-notice` div (around line 1703). Insert the following HTML **after** it and **before** the `<div class="upload-foot">` (around line 1705):

```html
    <!-- ══ MODE SELECTION ══ -->
    <div class="mode-section" id="mode-section">
      <div class="mode-section-label">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        Choose your workflow
      </div>
      <div class="mode-cards">
        <div class="mode-card selected" id="mode-express" onclick="selectMode('express')">
          <div class="mode-radio"></div>
          <div class="mode-badge mode-badge-default">Default</div>
          <div class="mode-title">Express Analysis</div>
          <div class="mode-desc">Runs all stages automatically. Get your full Recommendations Note in one go. Review intermediate findings after.</div>
          <div class="mode-time">&#9201; ~4–5 min · No interaction needed</div>
        </div>
        <div class="mode-card" id="mode-stepbystep" onclick="selectMode('stepbystep')">
          <div class="mode-radio"></div>
          <div class="mode-badge mode-badge-rec">Recommended</div>
          <div class="mode-title">Step-by-Step</div>
          <div class="mode-desc">Guide the analysis stage by stage. Review findings, add local knowledge, and refine before proceeding.</div>
          <div class="mode-time">&#9201; ~8–12 min · Full control</div>
        </div>
      </div>
    </div>
```

- [ ] **Step 2: Add `analysisMode` state variable and `selectMode()` function**

Find the JS state variable declarations (around line 1733, where `let pF=[], cF=[], hist=[]` etc. are declared). Add after the existing declarations:

```javascript
let analysisMode='express';
```

Then find a suitable location near the state declarations (or just after `initOnboarding()`) and add:

```javascript
function selectMode(mode){
  analysisMode=mode;
  document.getElementById('mode-express').classList.toggle('selected',mode==='express');
  document.getElementById('mode-stepbystep').classList.toggle('selected',mode==='stepbystep');
  localStorage.setItem('fcv_analysis_mode',mode);
}
```

Also, in the `initOnboarding()` function or on page load, restore the mode:

```javascript
// Restore mode preference from localStorage
const savedMode=localStorage.getItem('fcv_analysis_mode');
if(savedMode==='stepbystep'){selectMode('stepbystep');}
```

- [ ] **Step 3: Verify mode cards render and toggle**

Open the app locally. Confirm:
- Two mode cards appear between the confidentiality notice and the "Begin FCV Analysis" button
- Express is pre-selected (blue border)
- Clicking Step-by-Step selects it (blue border moves)
- Clicking Express re-selects it
- Refresh page — the previously selected mode is restored

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add mode selection cards to landing page"
```

---

### Task 3: Add Express Progress Screen HTML

**Files:**
- Modify: `index.html` — HTML section after the `stepper-wrap` div (around line 1642), before `<main>`

- [ ] **Step 1: Insert progress screen HTML**

Find `</nav></div>` that closes the `stepper-wrap` (around line 1642). Insert the following HTML **after** it and **before** `<main class="main" id="main">`:

```html
<!-- ══ EXPRESS PROGRESS SCREEN ══ -->
<div class="ep-accent" id="ep-accent" style="display:none"></div>
<div class="express-progress" id="express-progress">
  <div class="ep-header">
    <h2>Preparing Your FCV Recommendations Note</h2>
    <p>Your documents are being analysed against 12 operational standards, 25 key questions, and the full FCV Playbook.</p>
  </div>

  <div class="ep-stepper">
    <div class="ep-step-node">
      <div class="ep-step-circle pending" id="ep-circle-1">1</div>
      <div class="ep-step-label pending" id="ep-label-1">Context &amp;<br>Extraction</div>
    </div>
    <div class="ep-step-connector pending" id="ep-conn-1"></div>
    <div class="ep-step-node">
      <div class="ep-step-circle pending" id="ep-circle-2">2</div>
      <div class="ep-step-label pending" id="ep-label-2">FCV<br>Assessment</div>
    </div>
    <div class="ep-step-connector pending" id="ep-conn-2"></div>
    <div class="ep-step-node">
      <div class="ep-step-circle pending" id="ep-circle-3">3</div>
      <div class="ep-step-label pending" id="ep-label-3">Recommendations<br>Note</div>
    </div>
  </div>

  <div class="ep-progress-bar"><div class="ep-progress-fill" id="ep-progress-fill"></div></div>

  <div class="ep-stage-cards" id="ep-stage-cards">
    <div class="ep-stage-card pending" id="ep-card-1">
      <div class="ep-stage-header">
        <div class="ep-stage-title pending" id="ep-title-1">Stage 1 — Context &amp; Extraction</div>
      </div>
      <div class="ep-stage-summary" id="ep-summary-1" style="color:#9CA3AF;margin-top:6px">Pending</div>
    </div>
    <div class="ep-stage-card pending" id="ep-card-2">
      <div class="ep-stage-header">
        <div class="ep-stage-title pending" id="ep-title-2">Stage 2 — FCV Assessment</div>
      </div>
      <div class="ep-stage-summary" id="ep-summary-2" style="color:#9CA3AF;margin-top:6px">Pending</div>
    </div>
    <div class="ep-stage-card pending" id="ep-card-3">
      <div class="ep-stage-header">
        <div class="ep-stage-title pending" id="ep-title-3">Stage 3 — Recommendations Note</div>
      </div>
      <div class="ep-stage-summary" id="ep-summary-3" style="color:#9CA3AF;margin-top:6px">Pending</div>
    </div>
  </div>

  <div class="ep-timer">
    <span>Elapsed:</span>
    <span class="elapsed" id="ep-elapsed">0:00</span>
    <span>·</span>
    <span>Estimated total: 4–5 minutes</span>
  </div>

  <div class="ep-message-card" id="ep-message-card">
    <div class="ep-message-icon" id="ep-message-icon">&#9749;</div>
    <div class="ep-message-text" id="ep-message-text">"Go grab a coffee — this will take a few minutes."</div>
  </div>

  <div class="ep-bottom-note">Keep this tab open. You'll be able to review each stage's findings once the analysis is complete.</div>
</div>
```

- [ ] **Step 2: Verify HTML renders (hidden by default)**

Open the app locally. The progress screen should NOT be visible (it has `display:none` via the `.express-progress` class). Confirm the landing page still looks correct.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add express progress screen HTML"
```

---

### Task 4: Implement Express Progress Screen JS (Timer, Messages, Stage Updates)

**Files:**
- Modify: `index.html` — JS section (add new functions near other utility functions)

- [ ] **Step 1: Add progress screen state variables and message array**

Near the existing state variables (around line 1733), add:

```javascript
let epTimerInterval=null;
let epMessageInterval=null;
let epStartTime=null;
let epMessageIdx=0;
const EP_MESSAGES=[
  {icon:'\u2615',text:'"Go grab a coffee \u2014 this will take a few minutes."'},
  {icon:'\uD83D\uDCDA',text:'"Your project is being assessed against 12 operational standards and 25 key questions."'},
  {icon:'\u23F3',text:'"Don\u2019t worry, the wait will be worth it."'},
  {icon:'\uD83C\uDF0D',text:'"In FCV settings, nothing good happens quickly."'},
  {icon:'\uD83D\uDCC8',text:'"We\u2019re cross-referencing your document against the full FCV Playbook."'},
  {icon:'\uD83D\uDCA1',text:'"Tip: You can review each stage\u2019s findings once the analysis is complete."'}
];
```

- [ ] **Step 2: Add progress screen control functions**

Add the following functions in the JS section (near other utility functions, e.g., near `setStepper()`):

```javascript
function showExpressProgress(){
  document.getElementById('ep-accent').style.display='block';
  const ep=document.getElementById('express-progress');
  ep.classList.add('visible');
  // Reset all cards to pending
  for(let i=1;i<=3;i++){
    const card=document.getElementById('ep-card-'+i);
    card.className='ep-stage-card pending';
    document.getElementById('ep-title-'+i).className='ep-stage-title pending';
    document.getElementById('ep-summary-'+i).innerHTML='Pending';
    document.getElementById('ep-summary-'+i).style.color='#9CA3AF';
    document.getElementById('ep-circle-'+i).className='ep-step-circle pending';
    document.getElementById('ep-circle-'+i).innerHTML=i;
    document.getElementById('ep-label-'+i).className='ep-step-label pending';
  }
  document.getElementById('ep-conn-1').className='ep-step-connector pending';
  document.getElementById('ep-conn-2').className='ep-step-connector pending';
  document.getElementById('ep-progress-fill').style.width='0%';
  // Start timer
  epStartTime=Date.now();
  epTimerInterval=setInterval(updateEpTimer,1000);
  updateEpTimer();
  // Start message rotation
  epMessageIdx=0;
  showEpMessage(0);
  epMessageInterval=setInterval(()=>{
    epMessageIdx=(epMessageIdx+1)%EP_MESSAGES.length;
    const card=document.getElementById('ep-message-card');
    card.classList.add('fade-out');
    setTimeout(()=>{
      showEpMessage(epMessageIdx);
      card.classList.remove('fade-out');
    },500);
  },15000);
}

function hideExpressProgress(){
  document.getElementById('ep-accent').style.display='none';
  document.getElementById('express-progress').classList.remove('visible');
  if(epTimerInterval){clearInterval(epTimerInterval);epTimerInterval=null;}
  if(epMessageInterval){clearInterval(epMessageInterval);epMessageInterval=null;}
}

function updateEpTimer(){
  if(!epStartTime)return;
  const secs=Math.floor((Date.now()-epStartTime)/1000);
  const m=Math.floor(secs/60);
  const s=secs%60;
  document.getElementById('ep-elapsed').textContent=m+':'+(s<10?'0':'')+s;
}

function showEpMessage(idx){
  const msg=EP_MESSAGES[idx];
  document.getElementById('ep-message-icon').textContent=msg.icon;
  document.getElementById('ep-message-text').textContent=msg.text;
}

function updateExpressStage(stage,status,summary){
  // Update stepper circles and connectors
  for(let i=1;i<=3;i++){
    const circle=document.getElementById('ep-circle-'+i);
    const label=document.getElementById('ep-label-'+i);
    if(i<stage||(i===stage&&status==='done')){
      circle.className='ep-step-circle done';
      circle.innerHTML='\u2713';
      label.className='ep-step-label done';
    }else if(i===stage&&status==='active'){
      circle.className='ep-step-circle active';
      circle.innerHTML=i;
      label.className='ep-step-label active';
    }else{
      circle.className='ep-step-circle pending';
      circle.innerHTML=i;
      label.className='ep-step-label pending';
    }
  }
  // Connectors
  const conn1=document.getElementById('ep-conn-1');
  const conn2=document.getElementById('ep-conn-2');
  if(stage>1||(stage===1&&status==='done'))conn1.className='ep-step-connector done';
  else if(stage===1&&status==='active')conn1.className='ep-step-connector active';
  else conn1.className='ep-step-connector pending';
  if(stage>2||(stage===2&&status==='done'))conn2.className='ep-step-connector done';
  else if(stage===2&&status==='active')conn2.className='ep-step-connector active';
  else conn2.className='ep-step-connector pending';
  // Progress bar
  let pct=0;
  if(stage===1&&status==='active')pct=10;
  else if(stage===1&&status==='done')pct=33;
  else if(stage===2&&status==='active')pct=45;
  else if(stage===2&&status==='done')pct=66;
  else if(stage===3&&status==='active')pct=75;
  else if(stage===3&&status==='done')pct=100;
  document.getElementById('ep-progress-fill').style.width=pct+'%';
  // Stage cards
  for(let i=1;i<=3;i++){
    const card=document.getElementById('ep-card-'+i);
    const title=document.getElementById('ep-title-'+i);
    const sum=document.getElementById('ep-summary-'+i);
    if(i<stage||(i===stage&&status==='done')){
      card.className='ep-stage-card done';
      title.className='ep-stage-title done';
    }else if(i===stage&&status==='active'){
      card.className='ep-stage-card active';
      title.className='ep-stage-title active';
      sum.innerHTML='<div class="ep-stage-spinner"><div class="ep-spinner-dot"></div><div class="ep-spinner-dot"></div><div class="ep-spinner-dot"></div><span>'+getStageActivityText(i)+'</span></div>';
      sum.style.color='';
    }else if(i===stage&&status==='error'){
      card.className='ep-stage-card error';
      title.className='ep-stage-title error';
    }else{
      card.className='ep-stage-card pending';
      title.className='ep-stage-title pending';
      sum.innerHTML='Pending';
      sum.style.color='#9CA3AF';
    }
  }
  // Summary for completed stage
  if(status==='done'&&summary){
    const sum=document.getElementById('ep-summary-'+stage);
    sum.innerHTML=escHtml(summary);
    sum.style.color='#4B5563';
    // Add checkmark to header
    const hdr=document.getElementById('ep-card-'+stage).querySelector('.ep-stage-header');
    if(!hdr.querySelector('.ep-stage-check')){
      hdr.insertAdjacentHTML('beforeend','<div class="ep-stage-check">\u2713</div>');
    }
  }
}

function getStageActivityText(stage){
  if(stage===1)return'Extracting FCV context from your documents\u2026';
  if(stage===2)return'Analysing sensitivity, responsiveness, and Do No Harm\u2026';
  if(stage===3)return'Generating your Recommendations Note\u2026';
  return'Processing\u2026';
}

function showExpressError(stage,errorMsg){
  updateExpressStage(stage,'error',null);
  const sum=document.getElementById('ep-summary-'+stage);
  sum.innerHTML='<div style="color:#DC2626;font-size:13px;margin-top:6px">'+escHtml(errorMsg)+'</div>'+
    '<div class="ep-error-actions">'+
    '<button class="btn" onclick="retryExpressStage('+stage+')" style="background:var(--wbg-navy);color:#fff;border:none;border-radius:5px;font-size:12px;padding:6px 14px;cursor:pointer">Retry this stage</button>'+
    '<button class="btn" onclick="switchToStepByStep('+stage+')" style="background:#fff;color:var(--wbg-navy);border:1px solid #D1D5DB;border-radius:5px;font-size:12px;padding:6px 14px;cursor:pointer">Switch to step-by-step</button>'+
    '</div>';
  sum.style.color='';
  if(epTimerInterval){clearInterval(epTimerInterval);epTimerInterval=null;}
  if(epMessageInterval){clearInterval(epMessageInterval);epMessageInterval=null;}
}
```

- [ ] **Step 3: Verify by temporarily making progress screen visible**

Temporarily add `showExpressProgress(); updateExpressStage(2,'active',null); updateExpressStage(1,'done','Guinea Water Supply · PCN · 4 risk factors');` to the end of the page load script. Confirm the progress screen renders with correct styling. Remove the temporary code.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add express progress screen JS (timer, messages, stage updates)"
```

---

### Task 5: Add `onComplete` Callback to `runStage()` and Implement `runExpress()`

**Files:**
- Modify: `index.html` — JS `runStage()` function (around line 2088) and new `runExpress()` function

This is the core chain logic. `runStage()` gets a minimal change (one new parameter). `runExpress()` orchestrates the chain.

- [ ] **Step 1: Add `onComplete` parameter to `runStage()`**

Find the `runStage` function signature (around line 2088):

```javascript
async function runStage(stage, followOn=null){
```

Change it to:

```javascript
async function runStage(stage, followOn=null, onComplete=null){
```

- [ ] **Step 2: Call `onComplete` after the done event is fully processed**

Find the end of the `p.done` handling block inside `runStage()`. This is after all stage-specific post-processing (after `initStage3UI()` for Stage 3, after `updateSidebar()` for Stage 2, after DOC_TYPE extraction for Stage 1). Look for where `busy=false` is set at the end of the done block (around line 2280–2285).

Just **before** `busy=false` at the end of the done handler, add:

```javascript
if(onComplete){onComplete(stage,p);return;}
```

This means: if an `onComplete` callback was provided (i.e., we're in express mode), call it and skip the normal "wait for user" flow. The `return` prevents `renderOut()` from being called during express — we render only at the end.

**IMPORTANT:** The `onComplete` callback must be called AFTER `stageOutputs[stage]` and `stageHists[stage]` are written, and AFTER stage-specific data extraction (docType, ratings, under_hood, priorities). But BEFORE `renderOut()`. Find the exact location where `renderOut()` is called in the done handler and insert the `onComplete` check just before it.

Look at the done handler flow:
1. `stageOutputs[stage] = p.result` — save output
2. `stageHists[stage] = hist.slice()` — save history
3. Stage-specific extraction (docType for S1, ratings/under_hood for S2, priorities for S3)
4. `renderOut(stage, result, followOn)` — render UI ← INSERT `onComplete` CHECK HERE
5. Stage-specific post-render (under_hood panels for S2, initStage3UI for S3)

The `onComplete` check should go between step 3 and step 4. For express mode, we skip rendering intermediate stages entirely — we only render Stage 3 at the end.

However, for Stage 2 and Stage 3, some post-render processing is needed (Stage 2: `stage2UnderHood` localStorage write; Stage 3: priority extraction). These already happen in step 3 (before renderOut), so the onComplete can safely skip renderOut.

Find the line that calls `renderOut()` in the done handler and add just before it:

```javascript
// Express mode: skip rendering, call chain callback
if(onComplete){busy=false;onComplete(stage,p);return;}
```

- [ ] **Step 3: Implement `runExpress()` function**

Add the following function near `runStage()`:

```javascript
async function runExpress(){
  if(busy)return;
  // Hide landing, show progress
  document.getElementById('upload-panel').style.display='none';
  document.getElementById('landing-hero').style.display='none';
  document.getElementById('stepper-wrap').style.display='none';
  document.getElementById('main').style.display='none';
  showExpressProgress();
  updateExpressStage(1,'active',null);

  // Stage 1
  try{
    await runStage(1,null,function(stage,p){
      // Extract summary for progress card
      const country=docType!=='Unknown'?docType:'document';
      const match=p.result?p.result.match(/country[:\s]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)/i):null;
      const countryName=match?match[1]:'Project';
      const summary=countryName+' \u00B7 '+docType+' stage \u00B7 Context extracted';
      updateExpressStage(1,'done',summary);
      // Save to localStorage for resume
      localStorage.setItem('fcv_express_stageOutputs',JSON.stringify(stageOutputs));
      localStorage.setItem('fcv_express_stageHists',JSON.stringify(stageHists));
      localStorage.setItem('fcv_express_curS','1');
      // Chain to Stage 2
      updateExpressStage(2,'active',null);
      runStage(2,null,function(stage2,p2){
        const sensR=p2.sensitivity_rating||'—';
        const respR=p2.responsiveness_rating||'—';
        const summary2='Sensitivity: '+sensR+' \u00B7 Responsiveness: '+respR;
        updateExpressStage(2,'done',summary2);
        localStorage.setItem('fcv_express_stageOutputs',JSON.stringify(stageOutputs));
        localStorage.setItem('fcv_express_stageHists',JSON.stringify(stageHists));
        localStorage.setItem('fcv_express_curS','2');
        // Chain to Stage 3
        updateExpressStage(3,'active',null);
        runStage(3,null,function(stage3,p3){
          updateExpressStage(3,'done','Complete');
          localStorage.setItem('fcv_express_stageOutputs',JSON.stringify(stageOutputs));
          localStorage.setItem('fcv_express_stageHists',JSON.stringify(stageHists));
          localStorage.setItem('fcv_express_curS','3');
          // Transition to results
          hideExpressProgress();
          document.getElementById('stepper-wrap').style.display='';
          document.getElementById('main').style.display='';
          // Render Stage 3 output
          curS=3;
          setStepper(3,'done');
          renderOut(3,stageOutputs[3],false);
          // Stage 3 post-processing (priorities UI)
          if(stageThreePriorities&&stageThreePriorities.length){
            initStage3UI();
          }
          // Build Under the Hood panels for Stage 2 (needed for Go Deeper trail tab)
          if(stage2UnderHood){
            localStorage.setItem('stage2_under_hood',JSON.stringify(stage2UnderHood));
          }
          // Enable clickable stepper
          enableClickableStepper();
          // Clean up express localStorage
          localStorage.removeItem('fcv_express_stageOutputs');
          localStorage.removeItem('fcv_express_stageHists');
          localStorage.removeItem('fcv_express_curS');
          busy=false;
        });
      });
    });
  }catch(e){
    showExpressError(curS||1,e.message||'An error occurred');
    busy=false;
  }
}

function retryExpressStage(stage){
  // Re-run from the failed stage in express mode
  busy=false;
  updateExpressStage(stage,'active',null);
  if(epTimerInterval)clearInterval(epTimerInterval);
  epTimerInterval=setInterval(updateEpTimer,1000);
  if(epMessageInterval)clearInterval(epMessageInterval);
  epMessageIdx=0;
  epMessageInterval=setInterval(()=>{
    epMessageIdx=(epMessageIdx+1)%EP_MESSAGES.length;
    const card=document.getElementById('ep-message-card');
    card.classList.add('fade-out');
    setTimeout(()=>{showEpMessage(epMessageIdx);card.classList.remove('fade-out');},500);
  },15000);
  // Re-trigger from this stage — rebuild the chain from here
  if(stage===1)runExpress();
  else if(stage===2){
    updateExpressStage(2,'active',null);
    runStage(2,null,function(s2,p2){
      const sensR=p2.sensitivity_rating||'\u2014';
      const respR=p2.responsiveness_rating||'\u2014';
      updateExpressStage(2,'done','Sensitivity: '+sensR+' \u00B7 Responsiveness: '+respR);
      updateExpressStage(3,'active',null);
      runStage(3,null,function(s3,p3){
        updateExpressStage(3,'done','Complete');
        hideExpressProgress();
        document.getElementById('stepper-wrap').style.display='';
        document.getElementById('main').style.display='';
        curS=3;setStepper(3,'done');
        renderOut(3,stageOutputs[3],false);
        if(stageThreePriorities&&stageThreePriorities.length)initStage3UI();
        enableClickableStepper();
        busy=false;
      });
    });
  }else if(stage===3){
    updateExpressStage(3,'active',null);
    runStage(3,null,function(s3,p3){
      updateExpressStage(3,'done','Complete');
      hideExpressProgress();
      document.getElementById('stepper-wrap').style.display='';
      document.getElementById('main').style.display='';
      curS=3;setStepper(3,'done');
      renderOut(3,stageOutputs[3],false);
      if(stageThreePriorities&&stageThreePriorities.length)initStage3UI();
      enableClickableStepper();
      busy=false;
    });
  }
}

function switchToStepByStep(stage){
  hideExpressProgress();
  analysisMode='stepbystep';
  localStorage.setItem('fcv_analysis_mode','stepbystep');
  document.getElementById('stepper-wrap').style.display='';
  document.getElementById('main').style.display='';
  busy=false;
  // If we have previous stage output, render it
  const prevStage=stage-1;
  if(prevStage>=1&&stageOutputs[prevStage]){
    curS=prevStage;
    setStepper(prevStage,'done');
    renderOut(prevStage,stageOutputs[prevStage],false);
  }else{
    // Show error for current stage, let user retry in step-by-step
    curS=stage;
    setStepper(stage,'err');
    showErr('Stage '+stage+' failed during express mode. You can retry or go back.',stage);
  }
}
```

- [ ] **Step 4: Modify `startAnalysis()` to route based on `analysisMode`**

Find the end of `startAnalysis()` where it calls `await runStage(1)` (around line 2085). Replace that line:

```javascript
// OLD:
await runStage(1);

// NEW:
if(analysisMode==='express'){
  await runExpress();
}else{
  await runStage(1);
}
```

- [ ] **Step 5: Test express mode end-to-end**

1. Open the app locally
2. Upload a test PDF
3. Ensure "Express Analysis" is selected
4. Click "Begin FCV Analysis"
5. Verify:
   - Progress screen appears with Stage 1 active
   - Timer counts up
   - Messages rotate every 15 seconds
   - Stage 1 completes → summary appears → Stage 2 starts
   - Stage 2 completes → summary appears → Stage 3 starts
   - Stage 3 completes → progress screen hides → full recommendations render
6. Also verify step-by-step mode still works: select "Step-by-Step", begin analysis, confirm Stage 1 renders with refine box and "Continue to Stage 2" button

- [ ] **Step 6: Commit**

```bash
git add index.html
git commit -m "feat: implement runExpress() chain and onComplete callback in runStage()"
```

---

### Task 6: Implement Clickable Stepper and Post-Express Stage Navigation

**Files:**
- Modify: `index.html` — JS section (new functions + modify `setStepper()`)

- [ ] **Step 1: Add `enableClickableStepper()` function**

```javascript
function enableClickableStepper(){
  const wrap=document.getElementById('stepper-wrap');
  wrap.classList.add('stepper-clickable');
  // Add hint text
  let hint=document.getElementById('stepper-hint');
  if(!hint){
    hint=document.createElement('div');
    hint.id='stepper-hint';
    hint.className='stepper-hint';
    hint.textContent='Click any stage above to review its output';
    wrap.after(hint);
  }
  // Add click handlers to step elements
  for(let i=1;i<=3;i++){
    const step=document.getElementById('step-'+i);
    step.onclick=function(){navigateToStage(i);};
  }
}

function disableClickableStepper(){
  const wrap=document.getElementById('stepper-wrap');
  wrap.classList.remove('stepper-clickable');
  const hint=document.getElementById('stepper-hint');
  if(hint)hint.remove();
  for(let i=1;i<=3;i++){
    document.getElementById('step-'+i).onclick=null;
  }
}
```

- [ ] **Step 2: Add `navigateToStage()` function**

```javascript
function navigateToStage(stage){
  if(busy)return;
  if(!stageOutputs[stage])return;
  curS=stage;
  // Update stepper: all stages done, current highlighted
  for(let i=1;i<=3;i++){
    const el=document.getElementById('step-'+i);
    if(stageOutputs[i]){
      el.className=i===stage?'step done current':'step done';
    }else{
      el.className='step';
    }
  }
  // Render stored output
  clearUI();
  renderOut(stage,stageOutputs[stage],false);
  // Stage-specific post-render
  if(stage===2&&stage2UnderHood){
    buildUnderHoodPanels(stage2UnderHood);
    updateSidebar();
  }
  if(stage===3&&stageThreePriorities&&stageThreePriorities.length){
    initStage3UI();
  }
  // Add re-run banner for stages 1–2 if we came from express
  if(stage<3&&analysisMode==='express'){
    injectRerunBanner(stage);
  }
  // Add arrow navigation
  injectStageNavArrows(stage);
  updateSessionBar();
}
```

- [ ] **Step 3: Add `injectRerunBanner()` function**

```javascript
function injectRerunBanner(stage){
  const target=document.getElementById('stage-disp');
  if(!target)return;
  // Don't add if already present
  if(document.getElementById('rerun-banner'))return;
  const banner=document.createElement('div');
  banner.id='rerun-banner';
  banner.className='rerun-banner';
  banner.innerHTML='<div class="rerun-banner-icon">\u26A0\uFE0F</div>'+
    '<div class="rerun-banner-text"><strong>Want to refine this stage?</strong> You can add context or correct findings and re-run. Note: re-running will produce slightly different results due to the nature of AI analysis, and Stage 3 will need to be regenerated.</div>'+
    '<button class="rerun-btn" onclick="startRerun('+stage+')">Refine &amp; Re-run</button>';
  // Insert at top of stage display
  const outCard=target.querySelector('.out-card');
  if(outCard)outCard.before(banner);
  else target.prepend(banner);
  // Add read-only badge
  const badge=document.createElement('div');
  badge.className='read-only-badge';
  badge.textContent='Read-only \u00B7 From Express run';
  if(outCard)outCard.before(badge);
}

function startRerun(stage){
  // Switch to step-by-step mode from this stage
  analysisMode='stepbystep';
  localStorage.setItem('fcv_analysis_mode','stepbystep');
  disableClickableStepper();
  // Remove re-run banner
  const banner=document.getElementById('rerun-banner');
  if(banner)banner.remove();
  // Remove read-only badge
  document.querySelectorAll('.read-only-badge').forEach(b=>b.remove());
  // Restore history to this stage
  if(stageHists[stage])hist=stageHists[stage].slice();
  curS=stage;
  setStepper(stage,'done');
  // Invalidate subsequent stages
  for(let i=stage+1;i<=3;i++){
    delete stageOutputs[i];
    delete stageHists[i];
  }
  stageThreePriorities=[];
  fcvRating='';
  fcvResponsivenessRating='';
  // Re-render with refine box enabled
  renderOut(stage,stageOutputs[stage],false);
  if(stage===2&&stage2UnderHood){
    buildUnderHoodPanels(stage2UnderHood);
    updateSidebar();
  }
}
```

- [ ] **Step 4: Add `injectStageNavArrows()` function**

```javascript
function injectStageNavArrows(stage){
  const stageNames={1:'Context',2:'Assessment',3:'Recommendations'};
  // Remove existing arrows
  const existing=document.getElementById('stage-nav-arrows');
  if(existing)existing.remove();
  const nav=document.createElement('div');
  nav.id='stage-nav-arrows';
  nav.className='stage-nav-arrows';
  let leftBtn='';
  let rightBtn='';
  if(stage>1&&stageOutputs[stage-1]){
    leftBtn='<button class="stage-nav-btn" onclick="navigateToStage('+(stage-1)+')">← Stage '+(stage-1)+': '+stageNames[stage-1]+'</button>';
  }else{
    leftBtn='<div></div>';
  }
  if(stage<3&&stageOutputs[stage+1]){
    rightBtn='<button class="stage-nav-btn primary" onclick="navigateToStage('+(stage+1)+')">Stage '+(stage+1)+': '+stageNames[stage+1]+' →</button>';
  }else if(stage<3){
    rightBtn='<div></div>';
  }else{
    rightBtn='<div></div>';
  }
  nav.innerHTML=leftBtn+rightBtn;
  // Append after act-area or at end of main
  const actArea=document.getElementById('act-area');
  if(actArea)actArea.after(nav);
}
```

- [ ] **Step 5: Test clickable stepper navigation**

1. Run express mode to completion
2. Verify stepper has `stepper-clickable` class and "Click any stage" hint
3. Click Stage 1 → output renders with read-only badge + re-run banner + arrow nav
4. Click Stage 2 → output renders with Under the Hood panels + re-run banner
5. Click Stage 3 → recommendations render with priorities
6. Use arrow nav buttons to move between stages
7. Click "Refine & Re-run" on Stage 2 → verify refine box appears, re-run banner disappears, subsequent stages invalidated

- [ ] **Step 6: Commit**

```bash
git add index.html
git commit -m "feat: add clickable stepper, re-run banner, and stage navigation arrows"
```

---

### Task 7: Restore Back Buttons in Step-by-Step Mode

**Files:**
- Modify: `index.html` — `renderOut()` function (around line 2478)

- [ ] **Step 1: Verify back button visibility in `renderOut()` action bar**

Read the action bar section of `renderOut()` (around lines 2615–2635). Confirm that:
- For Stage 3: A "Go back to Stage 2" button exists with `onclick="goBack(3)"`
- For Stage 2: A "Go back to Stage 1" button exists with `onclick="goBack(2)"` (should have `stage > 1` guard)
- For Stage 1: No back button (correct)

If the back button for Stage 2 is missing or hidden, add it. The action bar for Stages 1–2 (around line 2625–2635) should include:

```javascript
// Inside renderOut(), in the action bar for stages 1-2:
if(stage>1){
  actHtml+='<button class="btn" onclick="goBack('+stage+')" style="...">'+
    '<svg ...></svg> Go back to Stage '+(stage-1)+
    '</button>';
}
```

Check the existing code. If the back button is already there but conditionally hidden, ensure the condition works. If it's missing, add it.

- [ ] **Step 2: Test back buttons in step-by-step mode**

1. Select "Step-by-Step" mode
2. Run through Stage 1, proceed to Stage 2
3. Verify "Go back to Stage 1" button is visible
4. Click it — Stage 1 output renders
5. Proceed back to Stage 2, then to Stage 3
6. Verify "Go back to Stage 2" button is visible on Stage 3
7. Click it — Stage 2 output renders with Under the Hood panels

- [ ] **Step 3: Commit (if any changes were needed)**

```bash
git add index.html
git commit -m "fix: ensure back buttons visible in step-by-step mode at all stages"
```

---

### Task 8: Extend Session Persistence for Express Mode

**Files:**
- Modify: `index.html` — `saveSession()` and `loadSession()` functions

- [ ] **Step 1: Add `analysisMode` to `saveSession()`**

Find `saveSession()` (around line 1759). In the JSON object being constructed, add `analysisMode`:

```javascript
// Find the object literal in saveSession(), add this field:
analysisMode: analysisMode,
```

Also bump the version:

```javascript
version: 2,
```

Add `stageOutputs` to the saved state so express sessions can be fully restored:

```javascript
stageOutputs: stageOutputs,
```

- [ ] **Step 2: Restore `analysisMode` and `stageOutputs` in `loadSession()`**

Find `loadSession()` (around line 1786). After restoring `hist`, `curS`, `docType`, add:

```javascript
// Restore analysis mode (default to 'stepbystep' for v1 sessions)
analysisMode=state.analysisMode||'stepbystep';
selectMode(analysisMode);

// Restore stage outputs if present
if(state.stageOutputs){
  stageOutputs=state.stageOutputs;
  // If all 3 stages complete, enable clickable stepper
  if(stageOutputs[1]&&stageOutputs[2]&&stageOutputs[3]){
    enableClickableStepper();
  }
}
```

- [ ] **Step 3: Add express resume on page refresh**

At the end of the page load / `DOMContentLoaded` handler, add a check for partial express state:

```javascript
// Check for interrupted express session
(function checkExpressResume(){
  const savedOutputs=localStorage.getItem('fcv_express_stageOutputs');
  const savedCurS=localStorage.getItem('fcv_express_curS');
  if(savedOutputs&&savedCurS){
    const lastComplete=parseInt(savedCurS,10);
    if(lastComplete>0&&lastComplete<3){
      // Show resume prompt
      const resume=confirm('An express analysis was interrupted after Stage '+lastComplete+'. Resume from Stage '+(lastComplete+1)+'?\n\nClick OK to resume, or Cancel to start over.');
      if(resume){
        stageOutputs=JSON.parse(savedOutputs);
        const savedHists=localStorage.getItem('fcv_express_stageHists');
        if(savedHists)stageHists=JSON.parse(savedHists);
        if(stageHists[lastComplete])hist=stageHists[lastComplete].slice();
        curS=lastComplete;
        analysisMode='express';
        // Can't fully resume express without files — switch to step-by-step from last completed stage
        localStorage.removeItem('fcv_express_stageOutputs');
        localStorage.removeItem('fcv_express_stageHists');
        localStorage.removeItem('fcv_express_curS');
        document.getElementById('upload-panel').style.display='none';
        document.getElementById('landing-hero').style.display='none';
        document.getElementById('stepper-wrap').style.display='';
        document.getElementById('main').style.display='';
        setStepper(lastComplete,'done');
        renderOut(lastComplete,stageOutputs[lastComplete],false);
        if(lastComplete===2&&stage2UnderHood){
          buildUnderHoodPanels(stage2UnderHood);
          updateSidebar();
        }
      }else{
        localStorage.removeItem('fcv_express_stageOutputs');
        localStorage.removeItem('fcv_express_stageHists');
        localStorage.removeItem('fcv_express_curS');
      }
    }
  }
})();
```

- [ ] **Step 4: Test session save/load**

1. Run express mode to completion
2. Click "Save Session" — verify JSON includes `analysisMode: "express"` and `stageOutputs`
3. Reload page, load the saved session — verify stage outputs restore and stepper is clickable
4. Test with a v1 session (no `analysisMode` field) — verify it defaults to step-by-step

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: extend session persistence for express mode (save/load/resume)"
```

---

### Task 9: Update CLAUDE.md Documentation

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add dual-mode documentation to CLAUDE.md**

In the Stage Pipeline section (Section 1.3), add a new subsection at the beginning describing the dual mode:

```markdown
### 1.3a Dual-Mode Workflow (v7.4)

Users choose between two modes on the landing page:

**Express Analysis (default):**
- All 3 stages run automatically via `runExpress()` which chains `runStage()` calls using an `onComplete` callback
- Progress screen shows stepper, stage summary cards, elapsed timer, and rotating messages (15s interval)
- On completion, full Stage 3 output renders; stepper becomes clickable for reviewing Stages 1–2
- Stage 1–2 views show read-only output with "Refine & Re-run" banner
- Re-running a stage switches to step-by-step mode and invalidates subsequent stages

**Step-by-Step (recommended):**
- Identical to pre-v7.4 behaviour — user reviews and refines at each stage before proceeding
- Back buttons visible at Stages 2 and 3

**Key functions:** `selectMode(mode)`, `runExpress()`, `showExpressProgress()`, `hideExpressProgress()`, `updateExpressStage(stage,status,summary)`, `enableClickableStepper()`, `navigateToStage(stage)`, `injectRerunBanner(stage)`, `startRerun(stage)`

**State:** `analysisMode` ('express'|'stepbystep') persisted to localStorage and session save files.

**Backend:** No changes. Express mode uses the same `/api/run-stage` route.
```

Also update the "Current version" line at the bottom of CLAUDE.md to reflect v7.4.

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add dual-mode workflow documentation to CLAUDE.md"
```

---

## Self-Review Checklist

**1. Spec coverage:**
- [x] Spec §1 (Problem Statement) → Addressed by the overall architecture
- [x] Spec §2 (Architectural Approach) → Task 5 (onComplete callback, no backend changes)
- [x] Spec §3 (Landing Page Mode Selection) → Task 2 (HTML + JS)
- [x] Spec §4 (Express Execution Flow) → Task 5 (runExpress chain)
- [x] Spec §5 (Progress Screen) → Tasks 3 (HTML) + 4 (JS)
- [x] Spec §6.1 (Completion Transition) → Task 5 (end of runExpress)
- [x] Spec §6.2 (Clickable Stepper) → Task 6 (enableClickableStepper)
- [x] Spec §6.3 (Read-Only + Re-Run) → Task 6 (injectRerunBanner, startRerun)
- [x] Spec §6.4 (Arrow Navigation) → Task 6 (injectStageNavArrows)
- [x] Spec §7.1 (Step-by-Step No Changes) → No modifications to step-by-step flow
- [x] Spec §7.2 (Back Buttons) → Task 7
- [x] Spec §8 (Session Persistence) → Task 8
- [x] Spec §9 (Error Handling) → Task 4 (showExpressError) + Task 5 (catch block, retryExpressStage, switchToStepByStep)
- [x] Spec §10.4 (CLAUDE.md) → Task 9

**2. Placeholder scan:** No TBDs, TODOs, or "add appropriate X" placeholders found.

**3. Type consistency:**
- `analysisMode` consistently typed as `'express'|'stepbystep'` throughout
- `selectMode(mode)` called with same string values everywhere
- `onComplete(stage, p)` callback signature consistent in runStage() and all runExpress() callbacks
- `stageOutputs[n]` and `stageHists[n]` indexed consistently with 1-based stage numbers
- `updateExpressStage(stage, status, summary)` called with consistent status values: `'active'|'done'|'error'`
- `navigateToStage(stage)` and `injectRerunBanner(stage)` use same 1-based stage numbering
