# FCV Screener — Explorer Redesign Implementation Spec
**For Claude Code to implement. Read this fully before touching any file.**

---

## 0. What this spec covers

This spec implements a redesign of the **Explorer output** — the deep-dive panel that appears inside each priority card when Stage 4 completes. The old design rendered collapsible A/B/C option cards (parsed by `parseExplorerText()` and rendered by `renderOptionsHtml()`). The new design replaces this entirely with **flowing narrative prose** that reads as a coherent, self-contained recommendation.

The redesign affects:
1. **`app.py`** — the `EXPLORER_PROMPT` (what the model generates)
2. **`index.html`** — `parseExplorerText()` and `renderOptionsHtml()` (how the output is parsed and rendered)
3. **`CLAUDE.md`** — update to reflect the new design and decisions

Nothing in Stages 1–3, the Stage 4 prompt, `extract_priorities()`, `clean_stage4_output()`, `extract_fcv_rating()`, `/api/run`, `/api/run-explorer`, or the prompt admin modal needs to change.

---

## 1. Design intent (read before coding)

The old Explorer gave the TTL 3–5 discrete "options" (A, B, C) in collapsible cards. This felt like a menu of choices rather than a recommendation. It also had a per-option "Ask about this" button, which fragmented the follow-up UX.

The new design presents the explorer output as a **single, flowing argument**:

- An **opening paragraph** that orients the TTL: "There are several ways to address this. The most important changes concern X and Y. Here is how to take them forward."
- **2–3 numbered action paragraphs** woven into the prose (not boxed), each with:
  - A bold heading with a small icon
  - An "Essential action" badge (red) if the action is crucial — or no badge for recommended but non-essential actions
  - Explanatory body paragraphs (2–4 sentences each)
  - A draft language / suggested wording block (for "where to add it in the PAD")
  - An implementation consideration block (practical caveats, sequencing, risks)
  - A document reference row at the bottom (which PAD annex/section to edit)
- **Connective prose** between actions (e.g. "Getting the right people on committees is the foundation — but it is not sufficient on its own. A second way to build on this is to…" / "Finally, …")
- A **closing synthesis paragraph** tying the actions together and restating the trust-building or FCV-sensitivity logic
- A **"Go Further" collapsible** section at the bottom with 1–2 optional above-and-beyond ideas, explicitly framed as optional and resource-dependent

The follow-up input bar at the bottom of each priority card (single bar, not per-option) is **unchanged** — it already exists and works.

---

## 2. Changes to `app.py` — the Explorer prompt

### 2a. Locate the existing `EXPLORER_PROMPT`

Find the string constant `EXPLORER_PROMPT` in `app.py`. It currently instructs the model to output:
```
SECTION 1: THE ISSUE
SECTION 2: OPTIONS TO CONSIDER
  OPTION A: [title]
  OPTION B: [title]
  OPTION C: [title]
  (each with: context, body, PAD/document change, TAGS line)
```

### 2b. Replace `EXPLORER_PROMPT` entirely

Replace the full `EXPLORER_PROMPT` string with the following. Keep the variable name identical — nothing else in `app.py` needs to change.

```python
EXPLORER_PROMPT = """You are an FCV (Fragility, Conflict, and Violence) specialist supporting a World Bank Task Team Leader (TTL). You have been given a specific priority recommendation from an FCV sensitivity assessment of a World Bank project. Your job is to write a detailed, actionable, and readable implementation guide for this priority that the TTL can act on directly.

## Output structure

Produce output in the following structure, using these exact section markers:

%%%EXPLORER_NARRATIVE_START%%%
[Full narrative — see requirements below]
%%%EXPLORER_NARRATIVE_END%%%

%%%GO_FURTHER_START%%%
[Go Further content — see requirements below]
%%%GO_FURTHER_END%%%

---

## Narrative section requirements (between %%%EXPLORER_NARRATIVE_START%%% and %%%EXPLORER_NARRATIVE_END%%%)

Write flowing, professional prose — NOT bullet points, NOT numbered lists, NOT option menus. The narrative should read as a coherent, standalone recommendation document that a busy TTL can pick up and act on.

### Structure of the narrative:

**1. Opening paragraph (required)**
Begin with a short orienting paragraph (3–5 sentences) that:
- Acknowledges there are several ways to address this priority
- Identifies which 2–3 changes matter most and why
- Sets up the actions that follow as a connected argument, not a menu

Example register: "There are several ways the team can address this gap, and they work best when pursued together. The two most important changes concern [X] and [Y] — both of which are design-stage decisions that are straightforward to implement but easy to miss. A third step ties these together in the results framework so that progress is tracked rather than assumed."

**2. Action paragraphs (2–3 maximum — do not exceed 3)**

For each action, produce the following in this exact order:

a) If this action is essential/crucial: include this exact marker on its own line before the heading:
   %%%CRUCIAL%%%

b) Action heading — a short, active, verb-led title. Format as:
   %%%ACTION_HEADING%%% [heading text here]

c) Body paragraphs — 2–4 paragraphs of substantive, specific prose:
   - Explain what the action involves in concrete terms
   - Reference the specific PAD annex or project document section where the change should be made (e.g. "Annex 2 (Component Design)", "Project Operations Manual — Section on Community Structures", "Annex 1 (Results Framework)")
   - Explain *why* this matters operationally for FCV sensitivity
   - Be specific: name the mechanism, the actor responsible, the timing, and the verification step

d) Draft language block — include this marker, then the suggested wording:
   %%%DRAFT_LANGUAGE%%%
   [Document location: e.g. "Annex 2, under community governance arrangements"]
   [Suggested wording: 1–3 sentences of actual PAD/operations manual language the TTL could insert]

e) Implementation consideration block — include this marker, then the note:
   %%%IMPLEMENTATION_NOTE%%%
   [1–2 sentences flagging a practical caveat, sequencing point, alternative approach, or relevant precedent from comparable projects]

f) Document references — include this marker, then list the specific documents:
   %%%DOC_REFS%%%
   [Comma-separated list of specific document locations, e.g.: "PAD — Annex 2 (Component Design)", "Project Operations Manual — Accountability Provisions", "PAD — Annex 1 (Results Framework)"]

**3. Connective prose between actions (required)**
Between each action paragraph, write 1–2 sentences of connective prose that:
- Signals the transition to the next action
- Makes the logical relationship between actions explicit
- Uses varied transitional language: "A second way to build on this is…", "With committees formed and operating transparently, the final step is to…", "Beyond the governance structures themselves, the team should also consider…"
- Avoid mechanical transitions like "Next," or "Additionally,"

**4. Closing synthesis paragraph (required)**
End the narrative with a 2–4 sentence paragraph that:
- Restates what the three actions achieve together
- Connects back to the FCV-sensitivity logic (trust-building, inclusion, institutional legitimacy, etc.)
- Notes that these changes are modest in cost but significant in signal
- Is written in the register of a supportive colleague, not a compliance checklist

### Tone and style:
- Write for a TTL who is operationally experienced but time-pressed
- Be direct and confident — these are recommendations, not options
- Use active voice and short sentences where possible
- Refer to "the team" rather than "you" for recommendations about project design; use "you" sparingly for direct personal guidance
- Do not use bullet points, numbered lists, or headers anywhere in the narrative
- Do not include meta-commentary ("This section addresses…", "As noted above…")

### Crucial vs recommended actions:
- Mark an action as %%%CRUCIAL%%% only if failing to take this action would meaningfully undermine FCV sensitivity — i.e. it addresses a high-severity gap that cannot be compensated for elsewhere
- Limit crucial flags to a maximum of 2 per priority
- If all actions are equally important, flag none as crucial — the prose should convey priority through ordering and emphasis instead

---

## Go Further section requirements (between %%%GO_FURTHER_START%%% and %%%GO_FURTHER_END%%%)

This section is for optional, above-and-beyond ideas that go beyond what is strictly necessary. It will be rendered as a collapsible at the bottom of the priority card with a clear "Optional" label.

Produce 1–2 ideas only. For each, use:

%%%GF_ITEM%%%
%%%GF_TITLE%%% [short title of the idea]
[2–3 paragraph explanation, written in the same prose register as the main narrative. Be specific about what this idea involves, what the preconditions are, and what value it would add if implemented. Make clear it is not a prerequisite.]

Do not include more than 2 Go Further items. Do not mark Go Further items as crucial.

---

## What NOT to do
- Do not produce OPTION A / OPTION B / OPTION C structure
- Do not produce bullet point lists
- Do not use headers like "Section 1" or "Section 2"
- Do not produce generic, non-specific advice (e.g. "consider stakeholder engagement")
- Do not reference the assessment stages or the tool itself
- Do not exceed 3 action paragraphs in the narrative
- Do not include more than 2 Go Further items

---

## Context you will receive

You will receive:
1. The priority title and FCV dimension
2. The gap identified (what is missing in the current project design)
3. Why it matters (the operational consequence)
4. The suggested directions from Stage 4 (the entry points)
5. The full Stage 1–3 conversation history (for project-specific grounding)

Use all of this to make the narrative as specific as possible to the actual project — reference the real project components, real geographic contexts, real stakeholder groups, and real document sections where known. Generic advice is not acceptable.
"""
```

---

## 3. Changes to `index.html` — parsing and rendering

### 3a. Replace `parseExplorerText()`

Find the existing `parseExplorerText()` function. Replace it entirely with:

```javascript
function parseExplorerText(raw) {
  // Extract main narrative
  const narrativeMatch = raw.match(/%%%EXPLORER_NARRATIVE_START%%%([\s\S]*?)%%%EXPLORER_NARRATIVE_END%%%/);
  const narrativeRaw = narrativeMatch ? narrativeMatch[1].trim() : raw;

  // Extract Go Further items
  const goFurtherMatch = raw.match(/%%%GO_FURTHER_START%%%([\s\S]*?)%%%GO_FURTHER_END%%%/);
  const goFurtherRaw = goFurtherMatch ? goFurtherMatch[1].trim() : '';

  // Parse action blocks out of narrative
  // Split on %%%CRUCIAL%%% or %%%ACTION_HEADING%%% markers
  const actions = [];
  const actionPattern = /(%%%CRUCIAL%%%\s*)?(%%%ACTION_HEADING%%%\s*([\s\S]*?)(?=%%%CRUCIAL%%%|%%%ACTION_HEADING%%%|%%%EXPLORER_NARRATIVE_END%%%|$))/g;

  // Split narrative into: opening prose, action blocks, connective prose, closing prose
  // We identify action blocks by the presence of %%%ACTION_HEADING%%%
  const segments = narrativeRaw.split(/(%%%CRUCIAL%%%[\s\S]*?(?=%%%CRUCIAL%%%|%%%ACTION_HEADING%%%(?![\s\S]*%%%ACTION_HEADING%%%)|$)|%%%ACTION_HEADING%%%[\s\S]*?(?=%%%CRUCIAL%%%|%%%ACTION_HEADING%%%|$))/);

  // Simpler approach: split on the action boundary markers
  const parts = narrativeRaw.split(/(%%%CRUCIAL%%%|%%%ACTION_HEADING%%%)/);

  // Parse linearly
  const parsed = { openingProse: '', actions: [], closingProse: '' };
  let i = 0;
  let inAction = false;
  let currentAction = null;
  let proseBuffer = '';

  // Linear parse of the raw narrative
  const lines = narrativeRaw.split('\n');
  let currentSection = 'opening';
  currentAction = null;

  for (let li = 0; li < lines.length; li++) {
    const line = lines[li];
    const trimmed = line.trim();

    if (trimmed === '%%%CRUCIAL%%%') {
      if (currentAction) { parsed.actions.push(currentAction); }
      else if (currentSection === 'opening') { parsed.openingProse = proseBuffer.trim(); }
      else if (currentSection === 'closing') { /* edge case */ }
      proseBuffer = '';
      currentAction = { crucial: true, heading: '', bodyParagraphs: '', draftLanguage: '', implementationNote: '', docRefs: '', connectorProse: '' };
      currentSection = 'action';
      continue;
    }

    if (trimmed.startsWith('%%%ACTION_HEADING%%%')) {
      const headingText = trimmed.replace('%%%ACTION_HEADING%%%', '').trim();
      if (currentAction && !currentAction.heading) {
        // We're in a crucial block that just got its heading
        currentAction.heading = headingText;
      } else {
        // New action block starting (not preceded by crucial marker)
        if (currentAction) { parsed.actions.push(currentAction); }
        else if (currentSection === 'opening') { parsed.openingProse = proseBuffer.trim(); }
        proseBuffer = '';
        currentAction = { crucial: false, heading: headingText, bodyParagraphs: '', draftLanguage: '', implementationNote: '', docRefs: '', connectorProse: '' };
        currentSection = 'action';
      }
      continue;
    }

    if (trimmed.startsWith('%%%DRAFT_LANGUAGE%%%')) {
      if (currentAction) { currentAction.draftLanguage = ''; }
      currentSection = 'draft';
      continue;
    }

    if (trimmed.startsWith('%%%IMPLEMENTATION_NOTE%%%')) {
      if (currentAction) { currentAction.implementationNote = ''; }
      currentSection = 'impl';
      continue;
    }

    if (trimmed.startsWith('%%%DOC_REFS%%%')) {
      if (currentAction) { currentAction.docRefs = ''; }
      currentSection = 'docrefs';
      continue;
    }

    // Detect connector prose: a non-empty paragraph after the doc refs of one action
    // and before the next action heading — store on the NEXT action as connectorProse
    if (currentSection === 'docrefs' && trimmed && !trimmed.startsWith('%%%')) {
      // Check if this looks like a new connector paragraph (not a doc ref continuation)
      if (currentAction && currentAction.docRefs && !trimmed.includes('PAD') && !trimmed.includes('Annex') && !trimmed.includes('Manual') && trimmed.length > 60) {
        // Likely connector prose — store it for the closing or next action
        currentSection = 'connector';
        proseBuffer = trimmed;
        continue;
      }
    }

    // Append to the right buffer
    if (currentSection === 'opening') {
      proseBuffer += (proseBuffer ? '\n' : '') + line;
    } else if (currentSection === 'action' && currentAction) {
      currentAction.bodyParagraphs += (currentAction.bodyParagraphs ? '\n' : '') + line;
    } else if (currentSection === 'draft' && currentAction) {
      currentAction.draftLanguage += (currentAction.draftLanguage ? '\n' : '') + line;
    } else if (currentSection === 'impl' && currentAction) {
      currentAction.implementationNote += (currentAction.implementationNote ? '\n' : '') + line;
    } else if (currentSection === 'docrefs' && currentAction) {
      currentAction.docRefs += (currentAction.docRefs ? '\n' : '') + line;
    } else if (currentSection === 'connector') {
      proseBuffer += (proseBuffer ? '\n' : '') + line;
    }
  }

  // Flush last action
  if (currentAction) {
    parsed.actions.push(currentAction);
  }

  // Anything remaining in proseBuffer after all actions = closing prose
  if (currentSection === 'connector' || currentSection === 'closing') {
    parsed.closingProse = proseBuffer.trim();
  }

  // Parse Go Further items
  const gfItems = [];
  if (goFurtherRaw) {
    const gfBlocks = goFurtherRaw.split('%%%GF_ITEM%%%').filter(b => b.trim());
    for (const block of gfBlocks) {
      const titleMatch = block.match(/%%%GF_TITLE%%%\s*(.+)/);
      if (titleMatch) {
        const title = titleMatch[1].trim();
        const body = block.replace(/%%%GF_TITLE%%%\s*.+/, '').trim();
        gfItems.push({ title, body });
      }
    }
  }

  parsed.goFurtherItems = gfItems;
  return parsed;
}
```

### 3b. Replace `renderOptionsHtml()` with `renderExplorerNarrativeHtml()`

Find the existing `renderOptionsHtml()` function. **Rename it** to `renderExplorerNarrativeHtml` and replace the entire body with the following. Also find every call site where `renderOptionsHtml(...)` is called and replace with `renderExplorerNarrativeHtml(...)`.

```javascript
function renderExplorerNarrativeHtml(parsed, priorityIdx) {
  const esc = s => (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

  // ── Icon SVGs ──
  const iconPeople = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`;
  const iconEye   = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
  const iconChart = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`;
  const iconDoc   = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`;
  const iconInfo  = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;
  const iconBolt  = `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`;
  const icons = [iconPeople, iconEye, iconChart];

  // ── Helper: render a paragraph block as HTML ──
  function paraHtml(text) {
    if (!text) return '';
    return text.trim().split(/\n\n+/).map(p => p.trim()).filter(Boolean)
      .map(p => `<p>${esc(p)}</p>`).join('');
  }

  // ── Helper: render doc refs as pills ──
  function docRefsHtml(refs) {
    if (!refs) return '';
    const pills = refs.split(',').map(r => r.trim()).filter(Boolean)
      .map(r => `<span class="fcv-doc-pill">📄 ${esc(r)}</span>`).join('');
    return `<div class="fcv-doc-ref-row"><span class="fcv-doc-ref-label">Where:</span>${pills}</div>`;
  }

  // ── Build action paragraphs HTML ──
  let actionsHtml = '';
  (parsed.actions || []).forEach((action, i) => {
    const isCrucial = action.crucial;
    const borderColor = isCrucial ? '#1A7A4A' : '#009FDA';
    const iconHtml = icons[i % icons.length];
    const iconBg = isCrucial ? '#1A7A4A' : '#009FDA';

    const crucialBadge = isCrucial ? `
      <div class="fcv-crucial-flag">
        ${iconBolt}
        Essential action
      </div>` : '';

    const draftBlock = action.draftLanguage ? `
      <div class="fcv-inset-note fcv-draft">
        <div class="fcv-inset-label">${iconDoc} Suggested language</div>
        ${paraHtml(action.draftLanguage)}
      </div>` : '';

    const implBlock = action.implementationNote ? `
      <div class="fcv-inset-note fcv-consider">
        <div class="fcv-inset-label">${iconInfo} Implementation consideration</div>
        ${paraHtml(action.implementationNote)}
      </div>` : '';

    actionsHtml += `
      <div class="fcv-action-para" style="border-left-color:${borderColor}">
        ${crucialBadge}
        <div class="fcv-action-heading">
          <div class="fcv-action-icon" style="background:${iconBg}">${iconHtml}</div>
          <span>${esc(action.heading)}</span>
        </div>
        <div class="fcv-action-body">
          ${paraHtml(action.bodyParagraphs)}
          ${draftBlock}
          ${implBlock}
          ${docRefsHtml(action.docRefs)}
        </div>
      </div>`;

    // Connector prose after this action (if any — look ahead in parsed)
    if (action.connectorProse) {
      actionsHtml += `<p class="fcv-connector">${esc(action.connectorProse)}</p>`;
    }
  });

  // ── Go Further collapsible ──
  let goFurtherHtml = '';
  if (parsed.goFurtherItems && parsed.goFurtherItems.length > 0) {
    const gfId = `gf-${priorityIdx}-${Math.random().toString(36).slice(2,6)}`;
    const letters = ['A','B','C'];
    const itemsHtml = parsed.goFurtherItems.map((item, gi) => `
      <div class="fcv-gf-item">
        <div class="fcv-gf-item-heading">
          <div class="fcv-gf-letter">${letters[gi] || (gi+1)}</div>
          <div class="fcv-gf-item-title">${esc(item.title)}</div>
        </div>
        <div class="fcv-gf-item-body">${paraHtml(item.body)}</div>
      </div>`).join('');

    goFurtherHtml = `
      <button class="fcv-gf-toggle" onclick="this.classList.toggle('open');document.getElementById('${gfId}').classList.toggle('open');this.querySelector('.fcv-gf-arrow').textContent=document.getElementById('${gfId}').classList.contains('open')?'▴':'▾';">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
        <span class="fcv-gf-label">Want to go further?</span>
        <span class="fcv-gf-badge">Optional</span>
        <span class="fcv-gf-arrow">▾</span>
      </button>
      <div class="fcv-gf-body" id="${gfId}">
        <p class="fcv-gf-intro">The actions above address the most significant gaps at minimal cost. If the team has additional appetite, political capital, and budget, the ideas below represent a step up in ambition. They are not prerequisites — do the essentials first.</p>
        ${itemsHtml}
      </div>`;
  }

  // ── Closing prose ──
  const closingHtml = parsed.closingProse
    ? `<p class="fcv-closing">${esc(parsed.closingProse)}</p>` : '';

  return `
    <div class="fcv-explorer-narrative">
      <div class="fcv-opening">${paraHtml(parsed.openingProse)}</div>
      ${actionsHtml}
      ${closingHtml}
    </div>
    ${goFurtherHtml}`;
}
```

### 3c. Add CSS for the new components

Find the existing CSS block in `index.html` (inside `<style>` tags). Add the following new rules. Place them near the existing explorer CSS rules (search for `.exp-option` to find the right area). Do not remove existing CSS — existing rules for `.exp-option`, `.exp-option-hdr`, `.exp-tags`, etc. can stay (they are unused but harmless).

```css
/* ── Explorer narrative (new design) ── */
.fcv-explorer-narrative {
  font-size: 14px;
  line-height: 1.88;
  color: var(--text, #1a2a3a);
}
.fcv-explorer-narrative p {
  margin-bottom: 1em;
}
.fcv-explorer-narrative p:last-child {
  margin-bottom: 0;
}
.fcv-opening {
  margin-bottom: 1.2em;
}
.fcv-connector {
  font-size: 14px;
  line-height: 1.85;
  color: var(--text, #1a2a3a);
  margin: 0.8em 0;
}
.fcv-closing {
  font-size: 13.5px;
  color: var(--muted, #5a6a7e);
  font-style: italic;
  margin-top: 1.2em;
  padding-top: 1em;
  border-top: 1px dashed var(--border, #d9e2ec);
  line-height: 1.7;
}

/* Action paragraphs */
.fcv-action-para {
  margin: 1.3em 0;
  padding-left: 18px;
  border-left: 3px solid #1A7A4A;
  position: relative;
}
.fcv-action-body p {
  margin-bottom: 0.75em;
  font-size: 14px;
  line-height: 1.85;
}
.fcv-action-body p:last-child {
  margin-bottom: 0;
}
.fcv-crucial-flag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #b91c1c;
  background: #fff5f5;
  border: 1px solid #fecaca;
  border-radius: 4px;
  padding: 2px 7px;
  margin-bottom: 7px;
}
.fcv-action-heading {
  font-size: 14.5px;
  font-weight: 700;
  color: var(--navy, #002244);
  margin-bottom: 8px;
  display: flex;
  align-items: flex-start;
  gap: 9px;
  line-height: 1.35;
}
.fcv-action-icon {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}

/* Inset notes (draft language / implementation consideration) */
.fcv-inset-note {
  border-radius: 0 6px 6px 0;
  padding: 10px 15px;
  margin: 10px 0 8px;
  font-size: 13px;
  line-height: 1.7;
}
.fcv-inset-note p {
  margin-bottom: 0.5em;
}
.fcv-inset-note p:last-child {
  margin-bottom: 0;
}
.fcv-draft {
  background: #f0f9f4;
  border-left: 3px solid rgba(26, 122, 74, 0.35);
  color: #1a3a25;
}
.fcv-consider {
  background: #f0f8ff;
  border-left: 3px solid rgba(0, 159, 218, 0.35);
  color: #1a3040;
}
.fcv-inset-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 6px;
}
.fcv-draft .fcv-inset-label { color: #1A7A4A; }
.fcv-consider .fcv-inset-label { color: #009FDA; }

/* Document reference row */
.fcv-doc-ref-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px dashed var(--border, #d9e2ec);
}
.fcv-doc-ref-label {
  font-size: 10.5px;
  color: var(--muted, #5a6a7e);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.fcv-doc-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--muted, #5a6a7e);
  background: #f1f5f9;
  border: 1px solid var(--border, #d9e2ec);
  border-radius: 4px;
  padding: 1px 7px;
}

/* Go Further collapsible */
.fcv-gf-toggle {
  width: 100%;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  padding: 12px 0 0;
  display: flex;
  align-items: center;
  gap: 9px;
  font-family: inherit;
  border-top: 1px solid var(--border, #d9e2ec);
  margin-top: 16px;
  transition: opacity 0.14s;
}
.fcv-gf-toggle:hover { opacity: 0.8; }
.fcv-gf-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--muted, #5a6a7e);
  flex: 1;
}
.fcv-gf-badge {
  font-size: 10px;
  padding: 2px 9px;
  background: #f5f0ff;
  border: 1px solid rgba(91, 33, 182, 0.2);
  border-radius: 10px;
  color: #5b21b6;
  font-weight: 700;
}
.fcv-gf-arrow {
  font-size: 11px;
  color: var(--muted, #5a6a7e);
  transition: transform 0.18s;
}
.fcv-gf-toggle.open .fcv-gf-arrow { transform: rotate(180deg); }
.fcv-gf-body {
  display: none;
  padding: 14px 0 4px;
}
.fcv-gf-body.open { display: block; }
.fcv-gf-intro {
  font-size: 13.5px;
  color: #374151;
  margin-bottom: 16px;
  line-height: 1.8;
  border-left: 3px solid rgba(91, 33, 182, 0.25);
  padding-left: 13px;
  font-style: italic;
}
.fcv-gf-item {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px dashed rgba(91, 33, 182, 0.15);
}
.fcv-gf-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}
.fcv-gf-item-heading {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  margin-bottom: 8px;
}
.fcv-gf-letter {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #7c3aed;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}
.fcv-gf-item-title {
  font-size: 14px;
  font-weight: 700;
  color: #5b21b6;
  line-height: 1.35;
}
.fcv-gf-item-body {
  padding-left: 31px;
  font-size: 13.5px;
  line-height: 1.78;
}
.fcv-gf-item-body p {
  margin-bottom: 0.6em;
}
.fcv-gf-item-body p:last-child {
  margin-bottom: 0;
}
```

### 3d. Update the call site where explorer output is injected

Find the place in `index.html` where the explorer response is rendered into the priority card — where `parseExplorerText()` and `renderOptionsHtml()` are called together after the explorer stream completes. The pattern will look something like:

```javascript
const parsed = parseExplorerText(explorerRaw);
const html = renderOptionsHtml(parsed, idx);
document.getElementById('explorer-options-' + idx).innerHTML = html;
```

Update this to:

```javascript
const parsed = parseExplorerText(explorerRaw);
const html = renderExplorerNarrativeHtml(parsed, idx);
document.getElementById('explorer-options-' + idx).innerHTML = html;
```

The container element `#explorer-options-{idx}` does not need to change — it is still the injection point inside the priority card's "How to act" zone.

---

## 4. Changes to `CLAUDE.md`

Update the following sections in `CLAUDE.md`. If the file does not exist in the repo, create it at the root (alongside `app.py`).

### Section to update: "Current version" line
Change:
```
**Current version:** FCV Screener 4.0 (with Explorer panel + specificity mandate)
```
To:
```
**Current version:** FCV Screener 5.0 (with Explorer narrative redesign)
```

### Section to update: Explorer prompt description
Find the section describing `EXPLORER_PROMPT` (under "Prompt Architecture" or similar). Replace the description with:

```markdown
### Explorer prompt (`DEFAULT_PROMPTS["explorer"]`)

**Purpose:** Generates the deep-dive implementation guide for a single priority when the TTL opens an Explorer card.

**Input context:** Receives the priority title, FCV dimension, the_gap, why_it_matters, suggested_directions fields from Stage 4, plus the full Stage 1–3 conversation history for project-specific grounding.

**Output structure (new as of v5.0):**
The prompt now produces **narrative prose**, not option menus. The output uses structural markers that the frontend parses:

- `%%%EXPLORER_NARRATIVE_START%%%` / `%%%EXPLORER_NARRATIVE_END%%%` — wraps the main recommendation narrative
- `%%%CRUCIAL%%%` — flags an action as essential (rendered as red badge in UI)
- `%%%ACTION_HEADING%%% [text]` — marks the start of a new action block
- `%%%DRAFT_LANGUAGE%%%` — introduces suggested PAD wording (rendered as green inset block)
- `%%%IMPLEMENTATION_NOTE%%%` — introduces a practical caveat (rendered as blue inset block)
- `%%%DOC_REFS%%%` — comma-separated list of document locations (rendered as pills)
- `%%%GO_FURTHER_START%%%` / `%%%GO_FURTHER_END%%%` — wraps the optional Go Further section
- `%%%GF_ITEM%%%` / `%%%GF_TITLE%%% [text]` — marks each Go Further idea

**Design decisions (v5.0):**
- Max 3 action blocks per narrative — fewer is fine if 1–2 are genuinely high priority
- Max 2 crucial flags — use sparingly
- Max 2 Go Further items
- No bullet points or option menus in output
- Actions must reference specific PAD sections (Annex 1, 2, Operations Manual, etc.)
- Connective prose between actions is required to maintain narrative flow
```

### Section to update: `parseExplorerText()` and `renderOptionsHtml()` descriptions
Find where these are described. Replace with:

```markdown
### `parseExplorerText(raw)` → `index.html`

Parses the Explorer prompt output into a structured object. Reads the `%%%MARKER%%%` delimiters and extracts:
- `openingProse` — introductory paragraph
- `actions[]` — array of `{crucial, heading, bodyParagraphs, draftLanguage, implementationNote, docRefs, connectorProse}`
- `closingProse` — synthesis paragraph
- `goFurtherItems[]` — array of `{title, body}`

### `renderExplorerNarrativeHtml(parsed, priorityIdx)` → `index.html`

Formerly `renderOptionsHtml()`. Takes the parsed object and renders the full Explorer card HTML including:
- Opening prose paragraph
- Action paragraphs (indented with left border, crucial badge if flagged, heading, body, draft language inset, implementation note inset, doc ref pills)
- Connective prose between actions
- Closing synthesis paragraph
- Go Further collapsible (hidden by default, purple theme, "Optional" badge)
```

### Add new section: "Design decisions log" entry

Add the following entry to the design decisions section:

```markdown
### v5.0 — Explorer narrative redesign (March 2026)

**What changed:** The Explorer output moved from a 3-option (A/B/C) collapsible card structure to flowing narrative prose with embedded action paragraphs.

**Why:** The old A/B/C structure felt like a menu of choices rather than a recommendation. TTLs were not sure which option to pick, and the per-option "Ask about this" button fragmented the follow-up UX. The new design reads as a coherent, self-contained recommendation that can stand alone as a document.

**Key design rules now in effect:**
- 2–3 action blocks maximum per narrative (1–2 is fine)
- Crucial badge (red) for actions that materially undermine FCV sensitivity if skipped — max 2 per priority
- Each action must include: body prose, draft language block, implementation consideration, and specific document references
- Connective prose between actions is required
- Go Further section is collapsible and explicitly framed as optional/resource-dependent
- Single follow-up input bar per priority card (unchanged from v4.0) — no per-option ask buttons
```

---

## 5. Generalisation notes (important)

The mockup used "water governance / ethnic committee composition" as an example. The implementation must be fully generalised. Specifically:

- **Icons:** The three action icons (people, eye, chart) rotate across actions by index — do not hardcode icons to specific action types
- **Border colours:** Crucial actions use green (`#1A7A4A`), non-crucial use blue (`#009FDA`) — this is purely positional/flag-based, not content-based
- **Draft language block:** Renders if `draftLanguage` is non-empty — some priorities may not generate a draft block; the UI handles this gracefully (block simply doesn't render)
- **Doc refs:** May reference any combination of PAD annexes, Operations Manual sections, ESMP, Procurement Plan, etc. — rendered as generic pills
- **Go Further:** May have 0, 1, or 2 items — if 0 items, the toggle is not rendered at all
- **Number of actions:** 1, 2, or 3 actions are all valid — the parser and renderer handle any count gracefully. Do not hard-code for exactly 3.

---

## 6. Testing checklist (for Claude Code to run after implementing)

1. `python3 -c "import app"` — no syntax errors
2. Start the app and run a Stage 4 analysis — priority cards render as before
3. Open the Explorer for any priority — narrative prose renders (not A/B/C cards)
4. Confirm: crucial badge appears for essential actions, absent for non-essential
5. Confirm: draft language block renders in green inset
6. Confirm: implementation note renders in blue inset
7. Confirm: doc ref pills render in the ref row
8. Confirm: Go Further toggle works (hidden by default, expands on click)
9. Confirm: follow-up input bar still works (unchanged)
10. Confirm: no console errors from `renderExplorerNarrativeHtml` or `parseExplorerText`
11. Test with a priority that generates only 1 or 2 actions — renders cleanly without empty space
12. Test with a priority that generates no Go Further items — toggle not shown

---

## 7. Files to change summary

| File | What changes |
|------|-------------|
| `app.py` | Replace `EXPLORER_PROMPT` string entirely |
| `index.html` | Replace `parseExplorerText()`, rename/replace `renderOptionsHtml()` → `renderExplorerNarrativeHtml()`, update call site, add CSS |
| `CLAUDE.md` | Update version, Explorer prompt description, function descriptions, add design decision log entry |

**Do not change:** `app.py` routes, Stage 1–3 prompts, Stage 4 prompt, `extract_priorities()`, `extract_fcv_rating()`, `clean_stage4_output()`, Stages 1–3 frontend, the follow-up input bar, the prompt admin modal, `background_docs.py`, `requirements.txt`, `Procfile`.
