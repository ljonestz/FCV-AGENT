# GPN & CPF Integration (v8.2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Embed Good Practice Notes on Peace & Inclusion Lenses and FCV-Sensitive Programming into the analytical backbone, and add Country Partnership Framework (CPF) upload support with per-priority CPF alignment in Stage 3 recommendations.

**Architecture:** Enrich the existing `FCV_OPERATIONAL_MANUAL` constant with non-duplicative GPN content (no redundancy with OST); add a new `CPF_INTEGRATION_GUIDE` constant; add a `cpf_alignment` field to Stage 3 JSON and the priority card UI; update 4 source-attribution locations to mention GPNs.

**Tech Stack:** Python (Flask, `background_docs.py`), vanilla JavaScript (`index.html`), no new dependencies.

---

## File Map

| File | What changes |
|---|---|
| `background_docs.py` | (1) Append 2 new subsections to `FCV_OPERATIONAL_MANUAL`; (2) Add `CPF_INTEGRATION_GUIDE` constant after `FCV_INSTRUMENT_CALIBRATION` |
| `app.py` | (1) Import `CPF_INTEGRATION_GUIDE`; (2) Add `cpf_alignment` to `_REQUIRED_PRIORITY_FIELDS`; (3) Stage 2 prompt: add Peace & Inclusion Lens sentence; (4) Stage 3 prompt: add CPF alignment paragraph + 4 P's framing + `cpf_alignment` JSON field + source attribution; (5) Inject `CPF_INTEGRATION_GUIDE` in design-review Stage 3 and express Stage 3 |
| `index.html` | (1) Update contextual zone hint text (2 locations); (2) Add CPF alignment zone in `showPriority()`; (3) Add CPF alignment to `downloadReport()`; (4) Update 4 source attribution locations |
| `CLAUDE.md` | Update constants list, JSON schema, version to v8.2 |

---

## Task 1: Enrich `FCV_OPERATIONAL_MANUAL` with GPN content

**Files:**
- Modify: `background_docs.py:319-321` (append before closing `"""`)

- [ ] **Step 1: Read the current end of `FCV_OPERATIONAL_MANUAL`**

Confirm lines 319–321 read:

```python
### Strengthening Social Cohesion (Box 2)
Operations can strengthen social cohesion by: addressing regional/inter-group inequities; having positive impacts on groups vulnerable to mobilisation (ex-combatants, unemployed youth); bolstering state legitimacy through local service delivery; addressing grievances (e.g. education in native language); promoting inclusion of marginalised groups; improving inter-group dialogue.
"""
```

- [ ] **Step 2: Replace the closing `"""` with the enriched ending**

Replace the last 3 lines of `FCV_OPERATIONAL_MANUAL` (the Box 2 paragraph + closing `"""`) with:

```python
### Strengthening Social Cohesion (Box 2)
Operations can strengthen social cohesion by: addressing regional/inter-group inequities; having positive impacts on groups vulnerable to mobilisation (ex-combatants, unemployed youth); bolstering state legitimacy through local service delivery; addressing grievances (e.g. education in native language); promoting inclusion of marginalised groups; improving inter-group dialogue.

---

### Peace & Inclusion Lens Dimensions
Source: Good Practice Note on Peace and Inclusion Lenses (December 2022)

The following dimensions supplement the 12 OST recommendations. They add operational depth for project-level FCV sensitivity screening — drawing on accumulated experience applying conflict filters and peace lenses across WBG portfolios. Use these as a lens when generating thematic findings in Stage 2, particularly for dimensions not fully captured by the 12 recs above.

**1. Geographic targeting against RRA-identified divides**
Where an RRA (or equivalent diagnostic) identifies subnational fault lines — regional, ethnic, urban/rural — the project's geographic footprint should be assessed against those divides. Projects that concentrate benefits in historically favoured areas without justification risk entrenching exclusion and fuelling grievance. Assess: Does the project's targeting map align with or cut across the RRA-identified divides? Are historically marginalised areas explicitly included? Does the project design account for differential access and absorption capacity across these zones?

**2. Social cohesion and reconciliation**
Beyond the Box 2 items above, assess explicitly: Does the project create opportunities for inter-group interaction that could improve relations? Does it risk entrenching parallel community structures (e.g. a new dispute mechanism displacing trusted traditional institutions)? Could implementation inadvertently reinforce group hierarchies? Projects that work through or alongside existing sources of resilience — traditional institutions, community dispute resolution, local leaders — are more likely to bolster rather than undermine cohesion.

**3. Project-cycle-specific application**
Peace and inclusion considerations have the greatest impact when applied at the earliest stages of project design (concept and appraisal), not retrofitted at MTR or restructuring. For each priority recommendation, flag whether it should be embedded at: Concept Note stage (design parameters), PAD appraisal (instrument commitments, ESCP, SEP), MTR (course corrections, indicator revisions), or Restructuring (scope changes, component redesign).

**4. Stakeholder engagement with conflict actors and non-beneficiaries**
Standard ESF stakeholder engagement focuses on affected communities and beneficiaries. In conflict-affected settings, additionally assess: Are non-beneficiaries identified, and is the risk of grievance from exclusion mitigated? Are conflict actors (including non-state armed groups, ethnic armed organisations) identified and, where feasible and appropriate, engaged during consultation? Are local languages used in consultations? Are feedback mechanisms accessible to groups facing active insecurity or mobility constraints?

**5. Unintended consequences — structured screening**
Before finalising any priority recommendation, check explicitly for both negative and positive unintended consequences:
- **Negative:** Could the project inadvertently increase horizontal inequality (by concentrating resources in one area or group)? Undermine state legitimacy (by working through actors seen as illegitimate, or undermining popular state functions)? Exacerbate grievances (e.g. related to natural resource exploitation, cultural imposition, or land access)? Weaken existing resilience (by displacing community structures or traditional institutions)?
- **Positive:** Could the project — even without a formal FCV objective — bolster cohesion (through cross-group collaboration), strengthen state legitimacy (by visibly delivering public goods), address grievances (e.g. inclusive curricula, equitable service delivery), or reduce vulnerability to mobilisation (e.g. through employment, particularly of youth and ex-combatants)?

---

### Strategic DRR Framing
Source: Good Practice Note on FCV Sensitive Program and Portfolio Analysis (July 2022)

The following contextual framing supplements the OST recommendations. It provides a strategic lens for interpreting project-level findings — particularly for structuring recommendations in Stage 3. Use it to situate project-level gaps within the broader landscape of FCV drivers, risks, and resilience factors.

**Drivers-Risks-Resilience (DRR) mapping**
Individual project findings should be interpreted in relation to the country's FCV landscape: the key drivers of fragility and conflict (e.g. land disputes, ethnic exclusion, weak institutions, criminal violence), the key risks to the project from FCV (e.g. insecurity disrupting implementation, political volatility undermining reform), and the key resilience factors the project could leverage or strengthen (e.g. community institutions, diaspora networks, local economic networks, state legitimacy in some regions). Frame Stage 3 recommendations by asking: does this recommendation help address a DRR? Does it protect the project from a DRR? Does it leverage a resilience factor?

**4 P's recommendation structure**
Where applicable, frame recommendations around the 4 P's of the FCV Strategy implementation model:
- **Policies** — regulatory or reform recommendations (e.g. conflict-sensitive prior actions, governance reforms)
- **Programming** — project design and targeting recommendations (e.g. component adjustments, targeting criteria, safeguard frameworks)
- **Partnerships** — HDP nexus, UN agency, NGO, and community-based actor recommendations
- **Personnel** — staffing, capacity building, security, and talent recommendations (e.g. FCV-specialist TTL, in-country FCV focal point, contractor security protocols)
This is a framing lens — it does not require a separate JSON field. Use it to shape narrative framing and the `guidance` field within actions.

**Strategic vs. operational distinction**
Distinguish between: (a) recommendations that are strategic — requiring portfolio-level decisions, CPF alignment, or government policy engagement; and (b) recommendations that are operational — addressable within the project's current scope, instruments, and timeline. Flag strategic recommendations in the `implementation_note` field (e.g. "This is a strategic consideration that goes beyond this project's scope — flag for CPF dialogue").

**Positive and negative unintended consequences — project-level**
When assessing a project, consider both directions:
- Could the project inadvertently worsen fragility? (Increase inequality, undermine legitimacy, exacerbate grievances, weaken resilience — see structured screening above)
- Could the project — without an explicit FCV objective — contribute positively? (Bolster cohesion, strengthen institutions, address root causes, reduce vulnerability) If so, flag this as a responsiveness opportunity even if the project is primarily coded as FCV Sensitive.
"""
```

- [ ] **Step 3: Verify the file is syntactically valid**

```bash
cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT"
python -c "import background_docs; print('OK')"
```
Expected output: `OK`

- [ ] **Step 4: Commit**

```bash
git add background_docs.py
git commit -m "feat: enrich FCV_OPERATIONAL_MANUAL with Peace & Inclusion Lens dims and DRR framing"
```

---

## Task 2: Add `CPF_INTEGRATION_GUIDE` constant to `background_docs.py`

**Files:**
- Modify: `background_docs.py` (append after the closing `"""` of `FCV_INSTRUMENT_CALIBRATION` at line 1577)

- [ ] **Step 1: Confirm the insertion point**

The end of `background_docs.py` (around line 1577) should end with:

```python
...Trust fund governance...
Do not treat trust fund or ASA operations as exempt from FCV assessment simply because they are smaller or advisory in nature.
"""
```

Followed by a blank line and the `WB_INSTRUMENT_GUIDE`, `FCV_GLOSSARY`, `WB_PROCESS_GUIDE` dictionaries. Find the exact line number:

```bash
cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT"
grep -n "FCV_INSTRUMENT_CALIBRATION\s*=\|^WB_INSTRUMENT_GUIDE\|^FCV_GLOSSARY\|^WB_PROCESS_GUIDE" background_docs.py
```

- [ ] **Step 2: Add the new constant after `FCV_INSTRUMENT_CALIBRATION`'s closing `"""`**

Insert the following block immediately after the closing `"""` of `FCV_INSTRUMENT_CALIBRATION` (currently around line 1577), before `WB_INSTRUMENT_GUIDE`:

```python

# ─────────────────────────────────────────────────────────────────────────────
# 11. CPF_INTEGRATION_GUIDE — How to use Country Partnership Framework content
# Last verified: 2026-04
# Source: WBG CPF methodology; v8.2 design spec
# Purpose: Tells Stage 3 LLM how to use CPF content when uploaded; injected
#          into Stage 3 system prompt unconditionally (the constant itself
#          handles the "if CPF was uploaded" logic)
# ─────────────────────────────────────────────────────────────────────────────

CPF_INTEGRATION_GUIDE = """## Country Partnership Framework (CPF) Integration Guide

### What is a CPF?
The Country Partnership Framework (CPF) is the World Bank Group's primary country-level strategic engagement document, typically covering a 5–6 year period. It defines the overarching goals, outcomes, and priority areas for all WBG activities in a country — across IDA/IBRD, IFC, and MIGA. Every World Bank project operates under the strategic umbrella of the current CPF. CPFs are structured around a small number of high-level outcomes (typically 3–5), each anchored on specific WBG platforms or sectoral priorities.

### When CPF content is available in Stage 1
If the user has uploaded a CPF among the contextual documents, Stage 1 will have extracted its key outcomes, sectoral priorities, and any FCV-related commitments. In Stage 3, use this extracted content to:
1. Identify the CPF's stated outcomes and the FCV-specific commitments or differentiated approach described in the CPF
2. For each priority recommendation, assess whether implementing that recommendation would strengthen a specific CPF outcome — either by making the project more effective at contributing to the outcome, or by reducing FCV risks that could undermine the outcome
3. Populate the `cpf_alignment` JSON field with a 1–2 sentence statement linking the recommendation to the relevant CPF outcome. Be specific: name the outcome by number or title as stated in the CPF.

### How to reference CPF content
- Cite the CPF by its formal title and period (e.g., "Niger CPF FY26–FY31") when mentioning it in narrative text
- Reference specific CPF outcomes by their number or name as stated in the CPF document
- Do NOT fabricate CPF content — only reference outcomes and language that was actually extracted from an uploaded CPF in Stage 1
- If a recommendation does not clearly strengthen any CPF outcome, set `cpf_alignment` to `null` — do not force a weak or speculative connection
- If no CPF was uploaded (i.e., no CPF appears in the Stage 1 contextual documents list), set `cpf_alignment` to `null` for all priorities

### Tone for CPF alignment statements
CPF alignment statements should be concise and forward-looking — framing the recommendation as an opportunity to strengthen country-level outcomes, not a compliance requirement. For example:
- "This recommendation strengthens CPF Outcome 1 (Healthier, Better Educated and Skilled Population) by ensuring that education service delivery reaches conflict-affected communities in Diffa and Tillabéri — areas explicitly flagged as priority zones in the CPF's differentiated approach."
- "Addressing the SEA/SH gap directly supports CPF Outcome 3 (Improved Agricultural Productivity and Food Security) by ensuring that female smallholders and female agricultural extension workers can participate safely in project activities — a prerequisite for achieving the CPF's gender-sensitive agricultural targets."
"""
```

- [ ] **Step 3: Verify syntax**

```bash
cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT"
python -c "import background_docs; print(background_docs.CPF_INTEGRATION_GUIDE[:80]); print('OK')"
```
Expected: prints start of the string and `OK`

- [ ] **Step 4: Commit**

```bash
git add background_docs.py
git commit -m "feat: add CPF_INTEGRATION_GUIDE constant to background_docs"
```

---

## Task 3: Update `app.py` — imports and `_REQUIRED_PRIORITY_FIELDS`

**Files:**
- Modify: `app.py:13-19` (import block)
- Modify: `app.py:71-76` (`_REQUIRED_PRIORITY_FIELDS`)

- [ ] **Step 1: Update the import block**

Current (lines 13–19):
```python
from background_docs import (
    FCV_GUIDE, FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK,
    PLAYBOOK_DIAGNOSTICS, PLAYBOOK_PREPARATION, PLAYBOOK_IMPLEMENTATION,
    PLAYBOOK_CLOSING, STAGE_GUIDANCE_MAP,
    WB_INSTRUMENT_GUIDE, FCV_GLOSSARY, WB_PROCESS_GUIDE, FCS_LIST,
    FCV_INSTRUMENT_CALIBRATION
)
```

Replace with:
```python
from background_docs import (
    FCV_GUIDE, FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK,
    PLAYBOOK_DIAGNOSTICS, PLAYBOOK_PREPARATION, PLAYBOOK_IMPLEMENTATION,
    PLAYBOOK_CLOSING, STAGE_GUIDANCE_MAP,
    WB_INSTRUMENT_GUIDE, FCV_GLOSSARY, WB_PROCESS_GUIDE, FCS_LIST,
    FCV_INSTRUMENT_CALIBRATION, CPF_INTEGRATION_GUIDE
)
```

- [ ] **Step 2: Add `cpf_alignment` to `_REQUIRED_PRIORITY_FIELDS`**

Current (lines 71–76):
```python
_REQUIRED_PRIORITY_FIELDS = [
    'title', 'fcv_dimension', 'tag', 'refresh_shift', 'risk_level',
    'the_gap', 'why_it_matters', 'actions',
    'who_acts', 'when', 'resources',
    'pad_sections', 'implementation_note'
]
```

Replace with:
```python
_REQUIRED_PRIORITY_FIELDS = [
    'title', 'fcv_dimension', 'tag', 'refresh_shift', 'risk_level',
    'the_gap', 'why_it_matters', 'actions',
    'who_acts', 'when', 'resources',
    'pad_sections', 'implementation_note', 'cpf_alignment'
]
```

- [ ] **Step 3: Verify the app imports cleanly**

```bash
cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT"
python -c "import app; print('OK')"
```
Expected: `OK` (Flask will not start but import will succeed)

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: import CPF_INTEGRATION_GUIDE; add cpf_alignment to priority fields"
```

---

## Task 4: Update Stage 2 prompt in `app.py`

**Files:**
- Modify: `app.py` — `DEFAULT_PROMPTS["2"]` (the Stage 2 prompt string, starting at line 415)

The Stage 2 prompt currently ends with the `## 3 Key Elements` section (line 469–471):

```
## 3 Key Elements
Evaluate: (1) Flexible Operational Design, (2) Tailored Implementation & Partnerships, (3) Strengthened Implementation Support
```

followed immediately by `# S/R Definitions — CRITICAL`.

- [ ] **Step 1: Add Peace & Inclusion Lens instruction after `## 3 Key Elements`**

Find the line (approximately 470–471):
```
## 3 Key Elements
Evaluate: (1) Flexible Operational Design, (2) Tailored Implementation & Partnerships, (3) Strengthened Implementation Support
```

Replace with:
```
## 3 Key Elements
Evaluate: (1) Flexible Operational Design, (2) Tailored Implementation & Partnerships, (3) Strengthened Implementation Support

## Peace & Inclusion Lens — Supplementary Screening
When generating thematic findings, also apply the Peace & Inclusion Lens dimensions from the enriched FCV Operational Manual (injected below): geographic targeting against RRA-identified subnational divides, social cohesion and reconciliation dynamics, project-cycle-specific application considerations, stakeholder inclusion of conflict actors and non-beneficiaries, and the structured positive/negative unintended consequences screening. Do not expose these dimensions as separate framework labels in the TTL-facing output — integrate them into the thematic narrative as analytical depth.
```

- [ ] **Step 2: Verify the app still imports**

```bash
cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT"
python -c "import app; print(app.DEFAULT_PROMPTS['2'][:200]); print('OK')"
```
Expected: first 200 chars of Stage 2 prompt + `OK`

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add Peace & Inclusion Lens instruction to Stage 2 prompt"
```

---

## Task 5: Update Stage 3 prompt in `app.py`

**Files:**
- Modify: `app.py` — `DEFAULT_PROMPTS["3"]` (Stage 3 prompt starting at line 822)

Three additions to the Stage 3 prompt:

### 5a — CPF alignment paragraph and `cpf_alignment` JSON field

- [ ] **Step 1: Find the `GEOGRAPHIC VALIDATION` block** (around line 999)

Locate this text:
```
GEOGRAPHIC VALIDATION: Before finalising each priority, check: does the `the_gap` field name at least one specific location, group, or institution drawn from the uploaded documents or web research? If not, revise it. If no specific geography is available in your sources, name the administrative level at which the project operates (e.g., county, district, commune) and note that sub-national detail is missing.
```

- [ ] **Step 2: Add CPF alignment instruction immediately after `GEOGRAPHIC VALIDATION`**

Insert the following paragraph after the `GEOGRAPHIC VALIDATION` block and before `Strict prohibitions:`:

```
CPF ALIGNMENT: If a Country Partnership Framework (CPF) was uploaded by the user among the contextual documents in Stage 1, it will appear in the Stage 1 output under contextual sources. For each priority recommendation, identify whether implementing that recommendation would strengthen a specific CPF outcome. Populate the `cpf_alignment` JSON field with a 1–2 sentence statement naming the specific CPF outcome (by number or title as stated in the CPF) and explaining how this recommendation supports it. If no CPF was uploaded, or if no clear linkage exists for a given priority, set `cpf_alignment` to `null` — do not fabricate connections. Refer to the CPF Integration Guide (injected below) for tone and citation guidance.
```

- [ ] **Step 3: Find the `## PRIORITY ACTIONS` framing section** (around line 963–982)

Locate the line:
```
ACTIONS: Provide 2-4 specific actions to address this gap.
```

- [ ] **Step 4: Add 4 P's framing guidance after the `ACTIONS` field description**

After the block ending with `Each action = one thing to change in the document.` (around line 981), find the sentence:
```
Each action = one thing to change in the document.
```
And add a new paragraph immediately after it:

```
4 P's FRAMING: Where applicable, shape the narrative framing of actions around the 4 P's of WBG FCV Strategy implementation — Policies (regulatory or reform recommendations), Programming (project design and targeting), Partnerships (HDP nexus, UN agencies, NGOs, community actors), Personnel (staffing, capacity, security). This is a framing lens that shapes the content of `guidance` fields and narrative prose — it does not require a separate JSON field or label in the output.
```

- [ ] **Step 5: Add `cpf_alignment` to the JSON quality check (around line 1063)**

Find this existing quality check line:
```
- Each priority JSON object has all 13 fields: title, fcv_dimension, tag, refresh_shift, risk_level, the_gap, why_it_matters, actions, who_acts, when, resources, pad_sections, implementation_note
```

Replace with:
```
- Each priority JSON object has all 14 fields: title, fcv_dimension, tag, refresh_shift, risk_level, the_gap, why_it_matters, actions, who_acts, when, resources, pad_sections, implementation_note, cpf_alignment
```

- [ ] **Step 6: Add `cpf_alignment` to the JSON schema example (around lines 1083–1113)**

Find the priority object template in the JSON block (around line 1084). The closing of each priority object currently ends with:
```json
      "implementation_note": "1-2 sentences on timing, cost, sequencing, or key dependency"
```

Add `cpf_alignment` as the last field:
```json
      "implementation_note": "1-2 sentences on timing, cost, sequencing, or key dependency",
      "cpf_alignment": "This recommendation strengthens CPF Outcome 1 (Healthier, Better Educated and Skilled Population) by..." 
```

Note: the example value uses `null` when no CPF is uploaded. Add a note in the JSON schema comment:
After `"cpf_alignment"` example, add on the next line before `}}}}`:
```
      // Set to null if no CPF uploaded or no clear linkage for this priority
```
Wait — JSON doesn't support comments. Instead update the IMPORTANT note at line 1114 to include:
```
The `cpf_alignment` field must be either a string (1-2 sentences) or JSON null — never the string "null" or "Not identified".
```

- [ ] **Step 7: Update source attribution in the Stage 3 prompt preamble**

The Stage 3 prompt begins (line 822):
```python
"3": '''# Role and Context
You are a senior FCV specialist providing collegial technical input to a World Bank Task Team Leader (TTL).
```

The prompt has a `# CRITICAL INSTRUCTION` block around line 883 mentioning the analytical basis. Find the `# WBG OPERATIONAL LENS FOR FCV` section (around line 899). This section describes the analytical framework for generating priorities.

Add a line at the very top of the prompt (after the `# Role and Context` heading and the first paragraph), before `## Stage Awareness`:

```
This analysis is grounded in the WBG FCV Strategy Refresh, FCV Operational Manual (OST), FCV Operational Playbook, and Good Practice Notes on Peace & Inclusion Lenses and FCV-Sensitive Programming. When a Country Partnership Framework (CPF) was uploaded, recommendations are also linked to relevant CPF outcomes via the `cpf_alignment` field.

---
```

- [ ] **Step 8: Verify imports**

```bash
cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT"
python -c "import app; print(len(app.DEFAULT_PROMPTS['3'])); print('OK')"
```
Expected: prints a number (length of Stage 3 prompt) + `OK`

- [ ] **Step 9: Commit**

```bash
git add app.py
git commit -m "feat: update Stage 3 prompt — CPF alignment, 4 P's framing, source attribution, cpf_alignment JSON field"
```

---

## Task 6: Inject `CPF_INTEGRATION_GUIDE` into Stage 3 in `app.py`

**Files:**
- Modify: `app.py` — two Stage 3 injection locations (design review ~line 3716; express ~line 3685)

There are two places where Stage 3's background docs are assembled and appended to the prompt string. Both need `CPF_INTEGRATION_GUIDE` appended.

### 6a — Design review Stage 3 (step-by-step mode, `run-stage` route)

- [ ] **Step 1: Find the design review Stage 3 injection block**

Around line 3716:
```python
                    stage3_prompt = (
                        stage3_prompt +
                        "\n\n--- WBG FCV Strategy Refresh Framework (4 Shifts) ---\n" +
                        FCV_REFRESH_FRAMEWORK
                    )
```

Replace with:
```python
                    stage3_prompt = (
                        stage3_prompt +
                        "\n\n--- WBG FCV Strategy Refresh Framework (4 Shifts) ---\n" +
                        FCV_REFRESH_FRAMEWORK +
                        "\n\n--- CPF Integration Guide (use when CPF was uploaded as a contextual document) ---\n" +
                        CPF_INTEGRATION_GUIDE
                    )
```

### 6b — Express Stage 3 (express mode, `run-express` route)

- [ ] **Step 2: Find the express Stage 3 injection block**

Around line 3680 (express, design path):
```python
                    stage3_prompt = (
                        stage3_prompt +
                        "\n\n--- WBG FCV Strategy Refresh Framework (4 Shifts) ---\n" +
                        FCV_REFRESH_FRAMEWORK
                    )
```

Replace with the same pattern:
```python
                    stage3_prompt = (
                        stage3_prompt +
                        "\n\n--- WBG FCV Strategy Refresh Framework (4 Shifts) ---\n" +
                        FCV_REFRESH_FRAMEWORK +
                        "\n\n--- CPF Integration Guide (use when CPF was uploaded as a contextual document) ---\n" +
                        CPF_INTEGRATION_GUIDE
                    )
```

- [ ] **Step 3: Verify the app imports cleanly**

```bash
cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT"
python -c "import app; print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: inject CPF_INTEGRATION_GUIDE into Stage 3 (design review + express)"
```

---

## Task 7: Update contextual upload zone hint text in `index.html`

**Files:**
- Modify: `index.html:1926` (zone hint)
- Modify: `index.html:2056` (tooltip text)

- [ ] **Step 1: Update zone hint (line ~1926)**

Find:
```html
        <p class="zone-hint" id="zone-hint-context">Upload 1–3 documents with FCV context for the country or region — e.g., RRA, country risk assessment, conflict analysis, technical studies, PPSD, or stakeholder analysis. If none uploaded, the tool will search trusted online sources to supplement. The more context provided, the more specific the assessment.</p>
```

Replace with:
```html
        <p class="zone-hint" id="zone-hint-context">Upload 1–3 documents with FCV context for the country or region — e.g., RRA, Country Partnership Framework (CPF), country risk assessment, conflict analysis, technical studies, PPSD, or stakeholder analysis. If none uploaded, the tool will search trusted online sources to supplement. The more context provided, the more specific the assessment.</p>
```

- [ ] **Step 2: Update tooltip text (line ~2056)**

Find (approximately):
```javascript
: 'Upload your primary project document (PCN, PID, PAD, AF, Restructuring Paper, or ISR). For a stronger assessment, also upload supporting documents such as the RRA, technical studies, PPSD, or stakeholder analysis as contextual documents below.
```

Replace `such as the RRA, technical studies, PPSD, or stakeholder analysis` with `such as the RRA, Country Partnership Framework (CPF), technical studies, PPSD, or stakeholder analysis`.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add CPF to contextual upload zone hint text"
```

---

## Task 8: Add CPF alignment zone to `showPriority()` in `index.html`

**Files:**
- Modify: `index.html:4370-4378` (between Zone 2 "Why it matters" and Zone 3 "How to act")

- [ ] **Step 1: Find the insertion point**

Around lines 4371–4378:
```javascript
        <!-- Zone 2: Why it matters -->
        <div class="pc-zone zone-why">
          <div class="pc-zone-title">
            <div class="pc-zone-icon"><svg ...></svg></div>
            Why it matters
          </div>
          <div class="pc-zone-body">${esc((pr.why_it_matters||'') + (pr.why_fcv_matters ? ' ' + pr.why_fcv_matters : ''))}</div>
        </div>
        <!-- Zone 3: How to act (from JSON — always available) -->
```

- [ ] **Step 2: Add CPF alignment zone between Zone 2 and Zone 3**

Replace the comment `<!-- Zone 3: How to act (from JSON — always available) -->` with:

```javascript
        <!-- Zone: CPF Alignment (conditional — only shown when cpf_alignment is non-null) -->
        ${pr.cpf_alignment ? `<div class="pc-zone zone-cpf">
          <div class="pc-zone-title">
            <div class="pc-zone-icon"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg></div>
            CPF Alignment
          </div>
          <div class="pc-zone-body">${esc(pr.cpf_alignment)}</div>
        </div>` : ''}
        <!-- Zone 3: How to act (from JSON — always available) -->
```

- [ ] **Step 3: Add `.zone-cpf` CSS style**

Find the existing `.zone-why` or `.zone-gap` CSS style in the `<style>` block and add after it:

```css
.zone-cpf { border-left: 3px solid rgba(0, 159, 218, 0.35); background: rgba(0, 159, 218, 0.04); }
```

Search for where `.zone-why` or `.pc-zone` styles are defined:
```bash
grep -n "zone-why\|zone-gap\|zone-act\|\.pc-zone" index.html | head -10
```
Then add `.zone-cpf` nearby.

- [ ] **Step 4: Verify the zone only renders when non-null**

Check the conditional: `${pr.cpf_alignment ? ... : ''}` — this correctly renders nothing when `cpf_alignment` is `null`, `undefined`, or an empty string.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: add CPF alignment zone to priority cards in showPriority()"
```

---

## Task 9: Add CPF alignment to `downloadReport()` in `index.html`

**Files:**
- Modify: `index.html` — `downloadReport()` function (around line 3855)

- [ ] **Step 1: Find the `Why It Matters` line in `downloadReport()`**

Around line 3855:
```javascript
        if(pr.why_it_matters) body += `<p><strong>Why It Matters:</strong><br>${esc(pr.why_it_matters)}</p>`;
        if(pr.actions && pr.actions.length > 0){
```

- [ ] **Step 2: Add CPF alignment after Why It Matters**

Replace:
```javascript
        if(pr.why_it_matters) body += `<p><strong>Why It Matters:</strong><br>${esc(pr.why_it_matters)}</p>`;
        if(pr.actions && pr.actions.length > 0){
```

With:
```javascript
        if(pr.why_it_matters) body += `<p><strong>Why It Matters:</strong><br>${esc(pr.why_it_matters)}</p>`;
        if(pr.cpf_alignment) body += `<p><strong>CPF Alignment:</strong><br>${esc(pr.cpf_alignment)}</p>`;
        if(pr.actions && pr.actions.length > 0){
```

- [ ] **Step 3: Add methodology note to downloaded report**

Find in `downloadReport()` the report header section (around line 3838):
```javascript
    let body = `<h1>FCV Recommendations Note</h1>
<p style="color:#666;font-size:9pt"><em>Generated by WBG FCV Project Screener · ${dateStr}</em></p>
<hr>
```

Replace with:
```javascript
    let body = `<h1>FCV Recommendations Note</h1>
<p style="color:#666;font-size:9pt"><em>Generated by WBG FCV Project Screener · ${dateStr}</em></p>
<p style="color:#888;font-size:8.5pt;font-style:italic">Analytical framework: WBG FCV Strategy Refresh, FCV Operational Manual (OST), FCV Operational Playbook, and Good Practice Notes on Peace &amp; Inclusion Lenses and FCV-Sensitive Programming. AI-assisted output — verify before operational use.</p>
<hr>
```

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add CPF alignment and methodology note to downloadReport()"
```

---

## Task 10: Update 4 source attribution locations in `index.html`

**Files:**
- Modify: `index.html` — lines 1716, 1751, 1812, 1833 (source attribution text)

- [ ] **Step 1: Update onboarding modal body text (line ~1716)**

Find:
```html
        <p style="font-size:14px;line-height:1.65;color:var(--text)">This tool uses an AI language model (LLM) to screen draft WBG project documents — such as PCNs and PADs — for FCV dynamics. It generates structured recommendations on how to strengthen FCV sensitivity and responsiveness, drawing on insights and framing from the OST Manual on FCV Sensitivity and Responsiveness, the WBG FCV Strategy, and the FCV Playbook — alongside the uploaded documents and the AI's broader knowledge of the country and sector context.</p>
```

Replace with:
```html
        <p style="font-size:14px;line-height:1.65;color:var(--text)">This tool uses an AI language model (LLM) to screen draft WBG project documents — such as PCNs and PADs — for FCV dynamics. It generates structured recommendations on how to strengthen FCV sensitivity and responsiveness, drawing on the WBG FCV Strategy Refresh, the OST Manual on FCV Sensitivity and Responsiveness, the FCV Operational Playbook, and Good Practice Notes on Peace &amp; Inclusion Lenses and FCV-Sensitive Programming — alongside the uploaded documents and the AI's broader knowledge of the country and sector context.</p>
```

- [ ] **Step 2: Update onboarding limitations text (line ~1751)**

Find:
```html
          <li>The AI draws on the OST Manual, FCV Strategy, and FCV Playbook, supplemented by its general knowledge of the country context, which may be <strong>outdated or incomplete</strong>. Always verify against current, authoritative sources.</li>
```

Replace with:
```html
          <li>The AI draws on the WBG FCV Strategy Refresh, OST Manual, FCV Playbook, and Good Practice Notes on Peace &amp; Inclusion Lenses and FCV-Sensitive Programming, supplemented by its general knowledge of the country context, which may be <strong>outdated or incomplete</strong>. Always verify against current, authoritative sources.</li>
```

- [ ] **Step 3: Update pre-loaded sources banner (line ~1812)**

Find:
```html
      <span style="font-size:12.5px;color:rgba(255,255,255,.72);line-height:1.5;"><strong style="color:rgba(255,255,255,.9)">Pre-loaded:</strong> OST Manual on FCV Sensitivity and Responsiveness, WBG FCV Strategy, and FCV Playbook — no upload needed. Country-specific risk documents (e.g. RRA, risk summaries) should be uploaded separately per project.</span>
```

Replace with:
```html
      <span style="font-size:12.5px;color:rgba(255,255,255,.72);line-height:1.5;"><strong style="color:rgba(255,255,255,.9)">Pre-loaded:</strong> WBG FCV Strategy Refresh, OST Manual, FCV Playbook, and Good Practice Notes on Peace &amp; Inclusion Lenses and FCV-Sensitive Programming — no upload needed. Country-specific risk documents (e.g. RRA, CPF, risk summaries) should be uploaded separately per project.</span>
```

- [ ] **Step 4: Update Express progress screen text (line ~1833)**

Find:
```html
    <p>Assessed against 12 operational standards and 25 key questions from the OST Manual — with insights from the FCV Playbook and alignment with core priorities from the FCV Strategy.</p>
```

Replace with:
```html
    <p>Assessed against 12 operational standards and 25 key questions from the OST Manual — with Peace &amp; Inclusion Lens dimensions, insights from the FCV Playbook, and alignment with the WBG FCV Strategy and Good Practice Notes.</p>
```

- [ ] **Step 5: Update EP_MESSAGES rotating text (lines ~3681–3691)**

Find:
```javascript
    {icon:'📖',text:'Your project is assessed against 12 operational standards and 25 key questions from the OST Manual.'},
```

Replace with:
```javascript
    {icon:'📖',text:'Your project is assessed against 12 operational standards and 25 key questions from the OST Manual, supplemented by Good Practice Notes on Peace & Inclusion Lenses and FCV-Sensitive Programming.'},
```

Find:
```javascript
    {icon:'📚',text:'We\'re drawing on the FCV Playbook for insights on relevant practices and operational tools.'},
```

Replace with:
```javascript
    {icon:'📚',text:'We\'re drawing on the FCV Playbook, Good Practice Notes on Peace & Inclusion Lenses, and FCV-Sensitive Programming for insights on relevant practices and operational tools.'},
```

- [ ] **Step 6: Commit**

```bash
git add index.html
git commit -m "feat: update source attribution in 4 UI locations to include Good Practice Notes"
```

---

## Task 11: Update `CLAUDE.md` to v8.2

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update the constants list in section 1.2**

Find in section 1.2 (Core Files):
```
                    #   PLAYBOOK_CLOSING, STAGE_GUIDANCE_MAP, FCS_LIST
                    #   + WB_INSTRUMENT_GUIDE, FCV_GLOSSARY, WB_PROCESS_GUIDE (helpers)
```

Replace with:
```
                    #   PLAYBOOK_CLOSING, STAGE_GUIDANCE_MAP, FCS_LIST
                    #   + WB_INSTRUMENT_GUIDE, FCV_GLOSSARY, WB_PROCESS_GUIDE (helpers)
                    #   + CPF_INTEGRATION_GUIDE (v8.2: CPF upload support)
```

- [ ] **Step 2: Update Stage 3 JSON fields in section 1.3**

Find in the Stage 3 description:
```
│  JSON top-level: fcv_rating, fcv_responsiveness_rating, sensitivity_summary,
│    responsiveness_summary, risk_exposure {risks_to, risks_from}, priorities[]
│  Each priority: title, fcv_dimension, tag, refresh_shift, risk_level, the_gap,
│    why_it_matters, actions[] (document_element + guidance + suggested_language),
│    who_acts, when, resources, pad_sections, implementation_note
```

Replace the last line with:
```
│    why_it_matters, actions[] (document_element + guidance + suggested_language),
│    who_acts, when, resources, pad_sections, implementation_note,
│    cpf_alignment (null if no CPF uploaded)
```

- [ ] **Step 3: Update the Overview to mention Good Practice Notes**

Find in the Overview:
```
The tool explicitly distinguishes two concepts:
```

Before that, find the sentence mentioning the analytical backbone. Look for:
```
The 4 FCV Strategy Shifts
```

In the paragraph above that, add a sentence. Find:
```
This is a **World Bank FCV (Fragility, Conflict, and Violence) Project Screener**
```

The paragraph ends somewhere around `...generate targeted, actionable recommendations.`

Add after that paragraph:

```
The analytical backbone draws on: the WBG FCV Strategy Refresh, FCV Operational Manual (OST), FCV Operational Playbook, and Good Practice Notes on Peace & Inclusion Lenses and FCV-Sensitive Programming (v8.2). When a Country Partnership Framework (CPF) is uploaded as a contextual document, Stage 3 recommendations include a `cpf_alignment` field linking priorities to CPF outcomes.
```

- [ ] **Step 4: Update version and date**

Find:
```
**Last updated:** 2026-04-12
**Current version:** FCV Project Screener v8.0
```

Replace with:
```
**Last updated:** 2026-04-14
**Current version:** FCV Project Screener v8.2
```

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md to v8.2 — CPF_INTEGRATION_GUIDE, cpf_alignment field, GPN attribution"
```

---

## Task 12: End-to-end smoke test

- [ ] **Step 1: Start the app locally**

```bash
cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT"
python app.py
```
Expected: Flask starts on `http://localhost:5000`

- [ ] **Step 2: Test without CPF upload**

Run a full Express analysis without uploading a CPF. After Stage 3 completes:
- Open browser console (F12)
- Run: `stageThreePriorities[0].cpf_alignment`
- Expected: `null`
- Verify: CPF alignment zone does NOT appear on any priority card

- [ ] **Step 3: Test with CPF upload**

Run a full Express analysis and upload the Niger CPF (`app_feedback/relevant_fcv_documents/CPF niger.pdf`) as a contextual document. After Stage 3 completes:
- Open browser console: `stageThreePriorities[0].cpf_alignment`
- Expected: a non-null string referencing CPF outcomes
- Verify: CPF alignment zone appears on at least one priority card with blue-tinted styling

- [ ] **Step 4: Test download**

Click Download on a Stage 3 result that has CPF alignment populated. Open the `.docx`:
- Verify: "CPF Alignment:" appears as a labelled field under "Why It Matters" for priorities with non-null alignment
- Verify: methodology note appears at the top listing OST Manual, FCV Playbook, Good Practice Notes

- [ ] **Step 5: Check source attribution locations**

Open the app and verify:
1. Onboarding modal (click the info/help icon) — text mentions "Good Practice Notes on Peace & Inclusion Lenses and FCV-Sensitive Programming"
2. Pre-loaded banner on landing page — mentions Good Practice Notes
3. Express progress screen description — mentions Good Practice Notes
4. Rotating EP_MESSAGES — at least one message mentions Good Practice Notes

- [ ] **Step 6: Check Under the Hood Panel 4 subtitle**

After running Stage 2, open the "Where did this analysis come from?" Under the Hood panel. The subtitle currently says `'25 diagnostic questions from the OST Manual used to probe the project'` — this is generated from `EP_MESSAGES` constants in `index.html` around line 3070. If the subtitle for Panel 4 (Evidence trail) needs updating to mention Good Practice Notes, update line ~3073:

Find:
```javascript
        { key: 'evidence_trail', title: 'Where did this analysis come from?', subtitle: '...' },
```

Check the current subtitle and if it references only OST Manual, update to include Good Practice Notes.

- [ ] **Step 7: Final commit if any fixes**

```bash
git add -A
git commit -m "fix: smoke test corrections for v8.2 GPN and CPF integration"
```

---

## Self-Review

**Spec coverage check:**
- [x] Enrich `FCV_OPERATIONAL_MANUAL` → Task 1
- [x] Add `CPF_INTEGRATION_GUIDE` constant → Task 2
- [x] Import `CPF_INTEGRATION_GUIDE` in `app.py` → Task 3
- [x] Add `cpf_alignment` to `_REQUIRED_PRIORITY_FIELDS` → Task 3
- [x] Stage 2 prompt: Peace & Inclusion Lens sentence → Task 4
- [x] Stage 3 prompt: CPF alignment paragraph + 4 P's framing + `cpf_alignment` JSON field + source attribution → Task 5
- [x] Inject `CPF_INTEGRATION_GUIDE` into Stage 3 (both modes) → Task 6
- [x] Contextual upload zone hint text (2 locations) → Task 7
- [x] CPF alignment zone in `showPriority()` → Task 8
- [x] CPF alignment in `downloadReport()` → Task 9
- [x] Source attribution in 4 UI locations → Task 10
- [x] `CLAUDE.md` update → Task 11

**Type consistency:** `cpf_alignment` is defined as a priority field in `_REQUIRED_PRIORITY_FIELDS` (Task 3), referenced in the Stage 3 JSON schema (Task 5), rendered as `pr.cpf_alignment` in `showPriority()` (Task 8), and in `downloadReport()` (Task 9) — consistent throughout.

**No placeholders:** All steps include exact strings, line references, and commands.
