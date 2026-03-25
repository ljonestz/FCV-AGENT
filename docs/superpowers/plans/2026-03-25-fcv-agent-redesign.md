# FCV Agent 3-Stage Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the FCV Project Screener from a 4-stage to a 3-stage pipeline, integrating the full OST Manual (12 recs, 25 questions), FCV Operational Playbook (stage-aware recommendations), and FCV Refresh (4 strategic shifts), with TTL-first output and "Under the Hood" depth for FCV CCs.

**Architecture:** Flask backend (app.py) + vanilla JS frontend (index.html) + knowledge base (background_docs.py). All prompts in DEFAULT_PROMPTS dict. SSE streaming for all LLM calls. localStorage for session persistence. No test framework — testing is manual via the running app.

**Tech Stack:** Python 3 / Flask 3.0.3 / Anthropic SDK / vanilla JavaScript / HTML+CSS

**Spec:** `docs/superpowers/specs/2026-03-25-fcv-agent-redesign-design.md`

**Source materials for content distillation:**
- OST Manual: `C:\Users\wb559324\OneDrive - WBG\Claude_Outputs\OST Manual\FCV Operational Manual for FCV CCs - June 2025.docx`
- FCV Playbook (4 docs): `C:\Users\wb559324\OneDrive - WBG\Claude_Outputs\FCV Playbook\`
- FCV Refresh Strategy: `C:\Users\wb559324\AppData\Local\Temp\FCV-strategy-update and next steps-2026-01-20-internal briefing.pptx`

---

## File Map

### Files to modify
| File | Responsibility | Est. changes |
|---|---|---|
| `background_docs.py` | Knowledge base constants — currently 50 lines with 2 constants; will expand to ~800-1000 lines with 8 constants | Major expansion |
| `app.py` | Flask backend — routes, prompts, parsing functions. Currently 1787 lines | Major rewrite of prompts (lines 102-719), moderate changes to routes (lines 1430-1779), new parsing functions |
| `index.html` | Frontend UI — HTML + CSS + JS. Currently 3629 lines | Moderate changes to stepper, new Stage 2 UI, enhanced Stage 3 UI, "Go Deeper" tabs |

### Files to create
| File | Responsibility |
|---|---|
| None | All changes go into existing files (consistent with current single-file architecture) |

### Files unchanged
| File | Reason |
|---|---|
| `requirements.txt` | No new dependencies |
| `Procfile` | No deployment changes |
| `.gitignore` | No new file types |
| `prompts.json` | Session-scoped, auto-cleared |

---

## Task Dependency Graph

```
Task 1 (Knowledge Base)
  ├─→ Task 2 (Backend Parsers) ─→ Task 5 (Backend Routes)
  ├─→ Task 3 (Stage 1 Prompt)
  ├─→ Task 4 (Stage 2 Prompt) ──→ Task 5
  └─→ Task 4b (Stage 3 + Deeper + Followon Prompts) ──→ Task 5
                                       │
Task 6 (Frontend Stepper + Stage 1 UI) │  ← independent
                                       │
Task 7 (Frontend Stage 2 UI) ──────────┤  ← depends on Task 5
Task 8 (Frontend Stage 3 UI) ──────────┤  ← depends on Task 5
Task 9 (Frontend Go Deeper Tabs) ──────┤  ← depends on Task 8
Task 10 (Frontend Sidebar + Download) ─┤  ← depends on Tasks 7, 8
Task 11 (Terminology + Migration) ─────┘  ← depends on all above
Task 12 (Integration Testing) ────────────← depends on all above
```

**Parallelizable:** Tasks 3, 4, 4b can run in parallel once Task 1 completes. Tasks 6 can run any time. Tasks 7, 8 can run in parallel once Task 5 completes.

---

## Task 1: Expand Knowledge Base (`background_docs.py`)

**Files:**
- Modify: `background_docs.py` (currently lines 1-50)
- Read (source): OST Manual docx, FCV Playbook (4 docx files), FCV Refresh Strategy pptx

**Context:** Currently contains 2 constants (`FCV_GUIDE` ~14k chars, `FCV_OPERATIONAL_MANUAL` ~8k chars). Must expand to 8 constants totalling ~80k chars (~20k tokens). All content must be **distilled** from source documents — structured, token-efficient, no narrative padding.

- [ ] **Step 1: Read all source materials**

Read the full contents of:
- `C:\Users\wb559324\OneDrive - WBG\Claude_Outputs\OST Manual\FCV Operational Manual for FCV CCs - June 2025.docx`
- `C:\Users\wb559324\OneDrive - WBG\Claude_Outputs\FCV Playbook\OperationalPlaybook_DiagnosticsPageText.docx`
- `C:\Users\wb559324\OneDrive - WBG\Claude_Outputs\FCV Playbook\OperationalPlaybook_PreperationPageText_WorkingFile.docx`
- `C:\Users\wb559324\OneDrive - WBG\Claude_Outputs\FCV Playbook\OperationalPlaybook_ImplementationPageText_WorkingFile.docx`
- `C:\Users\wb559324\OneDrive - WBG\Claude_Outputs\FCV Playbook\OperationalPlaybook_ProjectClosing_WorkingFile_CLEAN.docx`
- FCV Refresh Strategy pptx (extract via python-pptx as done in brainstorming session)

Keep notes on key content for each constant.

- [ ] **Step 2: Update `FCV_GUIDE` constant**

Update the existing `FCV_GUIDE` string in `background_docs.py` (line 3). Changes:
- Replace all references to old FCV Strategy pillars (preventing conflict, remaining engaged, transition, spillovers) with FCV Refresh 4 shifts (Anticipate, Differentiate, Jobs & private sector, Enhanced toolkit)
- Update S/R definitions to align with spec Section 8.3
- Keep existing screening questions structure (Sections I-III) — these are still valid
- Update terminology: "Strong/Partial/Weak" → "Strongly addressed/Partially addressed/Weakly addressed/Not addressed"

Target: ~3,000 tokens (~12,000 chars)

- [ ] **Step 3: Expand `FCV_OPERATIONAL_MANUAL` constant**

Expand the existing `FCV_OPERATIONAL_MANUAL` string (line 5-50). Currently has 6 recommendations + 7 PCN questions + operational flexibilities list. Must expand to include:
- All 12 recommendations (current has 1-6; add 7-12 from OST Manual):
  - Rec 7: Strengthen in-country M&E capacity and systems
  - Rec 8: Budget more purposefully for M&E in FCV settings
  - Rec 9: Use M&E to enhance citizen-state communications
  - Rec 10: Monitor, learn, and adapt more frequently
  - Rec 11: Consider pros/cons of impact evaluations in FCV
  - Rec 12: Put an FCV twist in ICRs
- All 25 key questions (extract from OST Manual — currently only has 7 PCN-stage questions)
- 3 key elements (extract from OST Manual)
- Map each recommendation to its most relevant FCV Refresh shift(s)

Format: Structured markdown with clear sections. Each recommendation gets: number, title, 1-2 sentence description, relevant shift(s).

Target: ~5,000 tokens (~20,000 chars)

- [ ] **Step 4: Write `FCV_REFRESH_FRAMEWORK` constant (new)**

Create new constant distilled from the FCV Refresh Strategy briefing pptx. Must include:
- The 4 strategic shifts with descriptions:
  - Shift A: Anticipate (new classification, AI-enabled Fragility Index, early warning)
  - Shift B: Differentiate (crisis/transition/prevention contexts, lasting impact potential)
  - Shift C: Jobs & private sector (foundations, enabling, financing)
  - Shift D: Enhanced toolkit (OP7.30, TPIs, sensitivity tag, partnerships, talent)
- FCV country classification scheme
- Definitions of FCV-sensitive vs. FCV-responsive operations
- How shifts map to project-level assessment (from spec Section 8.1)

Target: ~1,500 tokens (~6,000 chars)

- [ ] **Step 5: Write `PLAYBOOK_DIAGNOSTICS` constant (new)**

Distil from `OperationalPlaybook_DiagnosticsPageText.docx`. Must include:
- RRA methodology and purpose (what an RRA covers, how to use it for project design)
- Key diagnostic questions for FCV context analysis
- Data sources: WBG internal (FCV Data Collection, Horn of Africa dashboard, JDC) + external (UN briefs, ICG, IOM)
- Compound risk framework
- Forced displacement data resources
- Country Private Sector Diagnostic (CPSD) relevance
- Peace and Inclusion Lenses methodology

Format: Structured markdown. Strip narrative padding, contact details, URLs.

Target: ~2,000 tokens (~8,000 chars)

- [ ] **Step 6: Write `PLAYBOOK_PREPARATION` constant (new)**

Distil from `OperationalPlaybook_PreperationPageText_WorkingFile.docx`. Must include:
- Operational flexibilities available in FCV (CERC, HEIS, condensed procedures, phased disbursement, alternative arrangements)
- Policy references (OP 7.30, OP 7.60, OP 8.00, Para 12 IPF)
- FCV-sensitive project design elements (Do No Harm, conflict-sensitive targeting, inclusive engagement, adaptive management)
- M&E framework design for FCV settings
- FM and procurement adaptations for FCV
- Risk management (fiduciary, ESF, security/access)
- Stakeholder engagement and social accountability

Format: Structured by topic, with specific mechanisms named. Each mechanism gets: name, what it is, when to use it.

Target: ~3,000 tokens (~12,000 chars)

- [ ] **Step 7: Write `PLAYBOOK_IMPLEMENTATION` constant (new)**

Distil from `OperationalPlaybook_ImplementationPageText_WorkingFile.docx`. Must include:
- What's different about implementing in FCV (key considerations)
- Private sector engagement (IFC tools)
- Security sector, non-state actors, inaccessible contexts
- M&E during implementation (TPM, GEMS, digital tools)
- Forced displacement, gender, polycrises, climate considerations
- Risk monitoring and adaptation
- Stakeholder engagement and reputation management
- Third-party implementation (UN, other partners)

Target: ~2,500 tokens (~10,000 chars)

- [ ] **Step 8: Write `PLAYBOOK_CLOSING` constant (new)**

Distil from `OperationalPlaybook_ProjectClosing_WorkingFile_CLEAN.docx`. Must include:
- ICR guidance for FCV contexts (each section: context, changes, outcomes, bank performance, M&E quality, risk, lessons)
- Impact evaluation considerations in FCV
- How to assess results when operating environment changed significantly
- Lessons learned framework for FCV

Target: ~1,500 tokens (~6,000 chars)

- [ ] **Step 9: Write `STAGE_GUIDANCE_MAP` constant (new)**

Create a structured Python dict (or formatted string) that maps document types to guidance:

```python
STAGE_GUIDANCE_MAP = {
    "PCN": {
        "playbook_phase": "Preparation",
        "timing_options": "Identification / Preparation",
        "framing": "Build into the design now. Flag at QER. Ensure ToC reflects FCV logic.",
        "key_flexibilities": "CERC, condensed procedures, phased disbursement",
        "pad_section_examples": "Project Description; Theory of Change; Results Framework; ESCP; Stakeholder Engagement Plan"
    },
    "PID": {
        "playbook_phase": "Preparation",
        "timing_options": "Identification / Preparation",
        "framing": "Shape the concept. Flag early for design integration.",
        "key_flexibilities": "CERC, condensed procedures",
        "pad_section_examples": "Project Description; Theory of Change; Results Framework"
    },
    "PAD": {
        "playbook_phase": "Preparation",
        "timing_options": "Preparation / Appraisal",
        "framing": "Revise specific PAD sections. Add to ESCP commitments. Strengthen before Board.",
        "key_flexibilities": "CERC, HEIS, TPM, alternative implementation arrangements",
        "pad_section_examples": "Annex 1; Annex 5; ESCP; GRM; Results Framework; Implementation Arrangements"
    },
    "AF": {
        "playbook_phase": "Implementation",
        "timing_options": "Implementation / Restructuring",
        "framing": "Add as AF condition. Revise results framework. Strengthen implementation arrangements.",
        "key_flexibilities": "HEIS, TPM, portfolio adjustment, PIU flexibilities",
        "pad_section_examples": "AF Paper; Revised Results Framework; Updated ESCP"
    },
    "Restructuring": {
        "playbook_phase": "Implementation",
        "timing_options": "Implementation / Restructuring",
        "framing": "Include in restructuring package. Adjust indicators and arrangements.",
        "key_flexibilities": "HEIS, TPM, indicator adjustment, component reallocation",
        "pad_section_examples": "Restructuring Paper; Revised Results Framework"
    },
    "ISR": {
        "playbook_phase": "Implementation",
        "timing_options": "Implementation",
        "framing": "Flag in next ISR. Recommend adjustments for next restructuring opportunity.",
        "key_flexibilities": "TPM, GEMS, risk monitoring, adaptive management",
        "pad_section_examples": "ISR Ratings; ISR Action Items; Implementation Progress"
    }
}
```

Target: ~800 tokens (~3,200 chars)

- [ ] **Step 10: Update imports in `app.py`**

Update line 7 of `app.py`:

```python
# Current:
from background_docs import FCV_GUIDE, FCV_OPERATIONAL_MANUAL

# Change to:
from background_docs import (
    FCV_GUIDE, FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK,
    PLAYBOOK_DIAGNOSTICS, PLAYBOOK_PREPARATION, PLAYBOOK_IMPLEMENTATION,
    PLAYBOOK_CLOSING, STAGE_GUIDANCE_MAP
)
```

- [ ] **Step 11: Commit**

```bash
git add background_docs.py app.py
git commit -m "feat: expand knowledge base with OST Manual, Playbook, and FCV Refresh content"
```

---

## Task 2: Backend Parsing Functions

**Files:**
- Modify: `app.py` (lines 42-51 for field lists, lines 720-860 for parsing functions)

**Context:** Need to add `extract_under_hood()` and `extract_stage2_ratings()` for Stage 2, and update `extract_priorities()` for new Stage 3 JSON fields. Also update field validation lists.

- [ ] **Step 1: Update `_REQUIRED_TOP_FIELDS` and `_REQUIRED_PRIORITY_FIELDS`**

In `app.py`, update the validation lists (around lines 42-51):

```python
# Current _REQUIRED_TOP_FIELDS (line 42-45):
_REQUIRED_TOP_FIELDS = [
    'fcv_rating', 'fcv_responsiveness_rating',
    'sensitivity_summary', 'responsiveness_summary',
    'risk_to_project', 'risk_from_project', 'priorities'
]

# Change to:
_REQUIRED_TOP_FIELDS = [
    'fcv_rating', 'fcv_responsiveness_rating',
    'sensitivity_summary', 'responsiveness_summary',
    'risk_exposure', 'priorities'
]

# Current _REQUIRED_PRIORITY_FIELDS (line 47-51):
_REQUIRED_PRIORITY_FIELDS = [
    'title', 'dimension', 'tag', 'risk_level',
    'the_gap', 'why_it_matters', 'recommendation',
    'who_acts', 'when', 'resources'
]

# Change to:
_REQUIRED_PRIORITY_FIELDS = [
    'title', 'fcv_dimension', 'tag', 'refresh_shift', 'risk_level',
    'the_gap', 'why_it_matters', 'recommendation',
    'who_acts', 'when', 'resources',
    'pad_sections', 'suggested_language', 'implementation_note'
]
```

- [ ] **Step 2: Write `extract_stage2_ratings()` function**

Add new function after the existing helper functions (around line 860):

```python
def extract_stage2_ratings(stage2_output):
    """Extract sensitivity and responsiveness ratings from Stage 2 output.

    Looks for %%%STAGE2_RATINGS_START%%%...%%%STAGE2_RATINGS_END%%% block
    containing JSON: {"sensitivity_rating": "...", "responsiveness_rating": "..."}

    Returns dict with ratings or error.
    """
    pattern = r'%%%STAGE2_RATINGS_START%%%(.*?)%%%STAGE2_RATINGS_END%%%'
    match = re.search(pattern, stage2_output, re.DOTALL)
    if not match:
        return {'error': True, 'message': 'No ratings block found in Stage 2 output'}

    try:
        ratings = json.loads(match.group(1).strip())
        return {
            'error': False,
            'sensitivity_rating': ratings.get('sensitivity_rating', 'Unknown'),
            'responsiveness_rating': ratings.get('responsiveness_rating', 'Unknown')
        }
    except json.JSONDecodeError as e:
        return {'error': True, 'message': f'Failed to parse ratings JSON: {str(e)}'}
```

- [ ] **Step 3: Write `extract_under_hood()` function**

Add new function after `extract_stage2_ratings()`:

```python
def extract_under_hood(stage2_output):
    """Extract 'Under the Hood' analytical panels from Stage 2 output.

    Looks for %%%UNDER_HOOD_START%%%...%%%UNDER_HOOD_END%%% block, then
    extracts 4 sub-blocks: recs_table, dnh_checklist, questions_map, evidence_trail.

    Returns dict with panel contents and cleaned display text.
    """
    # Extract the full Under the Hood block
    hood_pattern = r'%%%UNDER_HOOD_START%%%(.*?)%%%UNDER_HOOD_END%%%'
    hood_match = re.search(hood_pattern, stage2_output, re.DOTALL)

    if not hood_match:
        return {
            'error': True,
            'message': 'No Under the Hood block found in Stage 2 output',
            'display_text': stage2_output,
            'recs_table': '',
            'dnh_checklist': '',
            'questions_map': '',
            'evidence_trail': ''
        }

    hood_text = hood_match.group(1)

    # Extract sub-blocks
    def extract_block(text, start_tag, end_tag):
        pattern = rf'{start_tag}(.*?){end_tag}'
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ''

    recs_table = extract_block(hood_text, '%%%RECS_TABLE_START%%%', '%%%RECS_TABLE_END%%%')
    dnh_checklist = extract_block(hood_text, '%%%DNH_CHECKLIST_START%%%', '%%%DNH_CHECKLIST_END%%%')
    questions_map = extract_block(hood_text, '%%%QUESTIONS_MAP_START%%%', '%%%QUESTIONS_MAP_END%%%')
    evidence_trail = extract_block(hood_text, '%%%EVIDENCE_TRAIL_START%%%', '%%%EVIDENCE_TRAIL_END%%%')

    # Strip ratings block and Under the Hood block from display text
    display_text = stage2_output
    display_text = re.sub(r'%%%STAGE2_RATINGS_START%%%.*?%%%STAGE2_RATINGS_END%%%', '', display_text, flags=re.DOTALL)
    display_text = re.sub(r'%%%UNDER_HOOD_START%%%.*?%%%UNDER_HOOD_END%%%', '', display_text, flags=re.DOTALL)
    display_text = display_text.strip()

    return {
        'error': False,
        'display_text': display_text,
        'recs_table': recs_table,
        'dnh_checklist': dnh_checklist,
        'questions_map': questions_map,
        'evidence_trail': evidence_trail
    }
```

- [ ] **Step 4: Update `extract_priorities()` for new field names and validation**

In `extract_priorities()` (around line 786-860), update:

1. Change validation to use `_REQUIRED_TOP_FIELDS` (which now expects `risk_exposure` as nested object instead of flat `risk_to_project`/`risk_from_project`)
2. Change priority field validation to use updated `_REQUIRED_PRIORITY_FIELDS` (now expects `fcv_dimension` instead of `dimension`, plus `refresh_shift`, `pad_sections`, `suggested_language`, `implementation_note`)
3. Update the return dict to use `risk_exposure` as nested object
4. Update error messages from "Stage 4" to "Stage 3"

Key changes in the function body:
- Where it currently reads `data.get('risk_to_project')` / `data.get('risk_from_project')`, change to `data.get('risk_exposure', {})` and extract `.get('risks_to')` / `.get('risks_from')` from the nested object
- Where it validates `priority.get('dimension')`, change to `priority.get('fcv_dimension')`
- Add `refresh_shift` to the fields checked per priority

- [ ] **Step 5: Write `clean_stage2_output()` function**

Add alongside existing `clean_stage4_output()`:

```python
def clean_stage2_output(text):
    """Strip delimiter blocks from Stage 2 output for display.
    Removes ratings block and Under the Hood block.
    """
    text = re.sub(r'%%%STAGE2_RATINGS_START%%%.*?%%%STAGE2_RATINGS_END%%%', '', text, flags=re.DOTALL)
    text = re.sub(r'%%%UNDER_HOOD_START%%%.*?%%%UNDER_HOOD_END%%%', '', text, flags=re.DOTALL)
    return text.strip()
```

- [ ] **Step 6: Commit**

Note: `clean_stage4_output()` rename to `clean_stage3_output()` is deferred to Task 5 (Backend Routes) where the call site is also updated, to avoid a breaking intermediate state.

```bash
git add app.py
git commit -m "feat: add Stage 2 parsing functions and update priority field validation"
```

---

## Task 3: Rewrite Stage 1 Prompt

**Files:**
- Modify: `app.py` (DEFAULT_PROMPTS["1"], lines 103-171)

**Context:** Stage 1 prompt is ~70 lines. Needs moderate updates: add Playbook Diagnostics guidance, FCV Refresh classification context, and project stage badge instruction. Core Part A/Part B structure and citation tiers stay the same.

- [ ] **Step 1: Read the current Stage 1 prompt**

Read `app.py` lines 103-171 to understand the exact current prompt text.

- [ ] **Step 2: Rewrite Stage 1 prompt**

Update `DEFAULT_PROMPTS["1"]` with these changes (keep existing structure, add new elements):

**Add to the system context section (near top):**
```
{FCV_REFRESH_FRAMEWORK}
{PLAYBOOK_DIAGNOSTICS}
```

**Add to Part A extraction instructions:**
```
In addition to the existing extraction categories, specifically flag:
- Whether the project references or uses a Risk and Resilience Assessment (RRA)
- Compound risk indicators (where multiple fragility drivers interact)
- Forced displacement considerations (refugee/IDP populations, host communities)
- Private sector diagnostic alignment (CPSD references, private sector components)
```

**Add to Part B contextual enrichment instructions:**
```
Frame contextual gaps against the FCV Refresh classification:
- Note if the country is on the FCS (Fragile and Conflict-affected Situations) list
- If FCS, note eligibility for FCV Envelope financing (PRA, RECA, TAA)
- Assess which FCV Refresh shift(s) are most relevant to this project context
```

**Keep unchanged:** Three-tier citation priority, DOC_TYPE classification line at end, large document handling instructions.

- [ ] **Step 3: Verify prompt includes `{PLAYBOOK_DIAGNOSTICS}` and `{FCV_REFRESH_FRAMEWORK}` references**

The prompt text should reference these constants. In the `run_stage()` route handler, where it builds the system message for Stage 1, ensure these constants are injected. Currently (around line 1470-1500), the Stage 1 system message is built by concatenating the prompt + FCV_GUIDE + FCV_OPERATIONAL_MANUAL. Add:

```python
if stage_num == 1:
    system_msg = prompt + "\n\n" + FCV_GUIDE + "\n\n" + FCV_OPERATIONAL_MANUAL + "\n\n" + PLAYBOOK_DIAGNOSTICS + "\n\n" + FCV_REFRESH_FRAMEWORK
```

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: enhance Stage 1 prompt with Playbook diagnostics and FCV Refresh context"
```

---

## Task 4: Write Stage 2 Prompt (merged assessment)

**Files:**
- Modify: `app.py` (DEFAULT_PROMPTS["2"], lines 173-382)

**Context:** This is the most complex prompt rewrite. Current Stage 2 (~210 lines) assesses 6 dimensions with risks TO/FROM. New Stage 2 must: use all 12 OST recs + 25 questions internally, produce a TTL-facing summary + "Under the Hood" delimited panels, emit ratings JSON, frame responsiveness around 4 shifts, include DNH traffic-light.

- [ ] **Step 1: Read the current Stage 2 prompt**

Read `app.py` lines 173-382 to understand the exact current prompt text.

- [ ] **Step 2: Write new Stage 2 prompt**

Replace `DEFAULT_PROMPTS["2"]` entirely. Follow the skeleton from spec Section 10.2. The prompt must:

**Role section:**
```
You are an expert FCV analyst conducting a comprehensive FCV assessment for the World Bank Group. You have deep expertise in the WBG FCV Strategy, the Operational Screening Tool (OST), and the FCV Refresh (January 2026).
```

**Internal framework instructions (invisible to TTL):**
- Assess against ALL 12 OST recommendations (reference `{FCV_OPERATIONAL_MANUAL}`)
- Answer ALL 25 key questions where evidence permits
- Evaluate the 3 key elements
- Map findings to the 4 FCV Refresh shifts

**TTL-facing output instructions (400-500 words):**
- Structure thematically, NOT recommendation-by-recommendation
- FCV Sensitivity findings (what's addressed, what's missing)
- Do No Harm traffic-light count against 8 canonical principles (list them in prompt)
- FCV Responsiveness findings — assess against each shift (A, B, C, D)
- Key gaps (3-5 most critical, prioritised, with evidence)
- Status terminology: ONLY use "Strongly addressed / Partially addressed / Weakly addressed / Not addressed"

**Ratings block instruction:**
```
After the TTL-facing summary, emit a ratings JSON block:
%%%STAGE2_RATINGS_START%%%
{"sensitivity_rating": "[one of: Extremely Low | Very Low | Low | Adequate | Well Embedded | Very Well Embedded]", "responsiveness_rating": "[same scale]"}
%%%STAGE2_RATINGS_END%%%
```

**Under the Hood block instruction:**
```
After the ratings block, emit detailed analytical panels between delimiters:
%%%UNDER_HOOD_START%%%

%%%RECS_TABLE_START%%%
| # | Recommendation | Status | Evidence | Gaps | Relevant Shift(s) |
|---|---|---|---|---|---|
[One row per recommendation, all 12]
%%%RECS_TABLE_END%%%

%%%DNH_CHECKLIST_START%%%
| Principle | Status | Evidence/Gap |
|---|---|---|
[One row per principle, all 8]
%%%DNH_CHECKLIST_END%%%

%%%QUESTIONS_MAP_START%%%
| # | Key Question | Answerable? | Finding | Source |
|---|---|---|---|---|
[One row per question, all 25]
%%%QUESTIONS_MAP_END%%%

%%%EVIDENCE_TRAIL_START%%%
| Source | Type | Used For |
|---|---|---|
[One row per source document/reference used]
%%%EVIDENCE_TRAIL_END%%%

%%%UNDER_HOOD_END%%%
```

**S/R classification instructions:**
- Same strict [S+R] definition as current (4 overlap zones only)
- Frame [R] against FCV Refresh shifts, not old pillars

- [ ] **Step 3: Update system message construction for Stage 2**

In `run_stage()`, where Stage 2 system message is built, inject the right constants:

```python
if stage_num == 2:
    system_msg = prompt + "\n\n" + FCV_OPERATIONAL_MANUAL + "\n\n" + FCV_REFRESH_FRAMEWORK + "\n\n" + FCV_GUIDE
```

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: write new Stage 2 merged assessment prompt with Under the Hood panels"
```

---

## Task 4b: Write Stage 3, Go Deeper, and Follow-on Prompts

**Files:**
- Modify: `app.py` (DEFAULT_PROMPTS["3"], DEFAULT_PROMPTS["deeper"], DEFAULT_PROMPTS["deeper_playbook"], DEFAULT_PROMPTS["followon"])

**Context:** Stage 3 replaces current Stage 4 (lines 497-592). Go Deeper replaces Explorer (lines 593-717). New deeper_playbook prompt needed. Follow-on (line 718+) gets minor updates.

- [ ] **Step 1: Read current Stage 3 and Stage 4 prompts**

Read `app.py` lines 383-592 to understand the current Stage 3 (gaps) and Stage 4 (recommendations) prompts.

- [ ] **Step 2: Write new Stage 3 prompt (recommendations note)**

Replace `DEFAULT_PROMPTS["4"]` content, assign to new key `"3"`. Remove old `DEFAULT_PROMPTS["3"]` (gaps prompt — now merged into Stage 2). Follow spec Section 10.3 skeleton.

Key additions beyond current Stage 4:
- Stage-awareness injection point: `{doc_type}`, `{timing_emphasis}`, `{playbook_guidance}`
- New `refresh_shift` field in JSON schema per priority
- Updated `who_acts` vocabulary: `TTL; PIU; Government; FCV CC; FM Team; ESF Team; Technical Team; M&E Team` (semicolon-separated, multi-value)
- Updated `when` values: `Identification | Preparation | Appraisal | Implementation | Restructuring`
- Updated `resources` values with parenthetical definitions
- `fcv_dimension` (not `dimension`) in JSON schema
- `risk_exposure` as nested `{"risks_to": "...", "risks_from": "..."}` in JSON schema
- Reference FCV Refresh shifts in `why_it_matters` for [R] and [S+R] priorities

- [ ] **Step 3: Write `deeper` prompt (alternative approaches)**

Rename key from `"explorer"` to `"deeper"`. Content is largely the same as current Explorer prompt (lines 593-717) with these updates:
- Reference FCV Refresh shifts where relevant
- Updated who_acts vocabulary
- Same `%%%GO_FURTHER_START/END%%%` and `%%%GF_ITEM/TITLE%%%` output format

- [ ] **Step 4: Write `deeper_playbook` prompt (new)**

Add new key `DEFAULT_PROMPTS["deeper_playbook"]`. Follow spec Section 10.5:

```
# Role
You are an FCV operational specialist helping a World Bank Task Team apply WBG guidance to strengthen a specific priority action.

# Context
You are given a specific priority from an FCV screening analysis, along with the relevant operational playbook guidance for this project's lifecycle stage.

{playbook_content}

# Task
For the given priority, identify and explain:
1. Relevant operational flexibilities (name the mechanism: CERC, HEIS, TPM, GEMS, etc.) and how they apply to this specific priority
2. Applicable policy references (OP 7.30, OP 8.00, Para 12 IPF, etc.) with brief explanation of relevance
3. Implementation guidance specific to this priority's FCV dimension and country context
4. Named WBG resources or teams that can support implementation

# Output format
Structured prose, 300-500 words. Use clear thematic headings. NOT bullet lists.
Reference specific Playbook guidance where possible.
Be specific to the priority — do not give generic FCV advice.
```

- [ ] **Step 5: Update Follow-on prompt**

Update `DEFAULT_PROMPTS["followon"]` with two changes:
1. Replace any old FCV Strategy pillar references with FCV Refresh 4 shifts
2. When drafting peer review notes, reference the expanded assessment (12 recs, not just 6) and use updated terminology ("Strongly addressed" etc.)

- [ ] **Step 6: Remove old prompt keys, update dict structure**

The final `DEFAULT_PROMPTS` dict should have exactly these keys:
```python
DEFAULT_PROMPTS = {
    "1": "...",              # Stage 1
    "2": "...",              # Stage 2 (merged assessment)
    "3": "...",              # Stage 3 (recommendations — was "4")
    "deeper": "...",         # Go Deeper alternatives (was "explorer")
    "deeper_playbook": "...",# Go Deeper playbook refs (new)
    "followon": "...",       # Follow-on (updated)
}
```

Delete old keys `"3"` (gaps prompt) and `"4"` (old recommendations prompt, content moved to new `"3"`).

- [ ] **Step 7: Update `get_prompt_for_stage()` and `get_stage_name()`**

Update `get_stage_name()` (line 1113-1118):
```python
def get_stage_name(stage):
    names = {
        "1": "Context & Extraction",
        "2": "FCV Assessment",
        "3": "Recommendations Note",
        "deeper": "Go Deeper",
        "deeper_playbook": "Playbook References",
        "followon": "Follow-on"
    }
    return names.get(str(stage), f"Stage {stage}")
```

- [ ] **Step 8: Commit**

```bash
git add app.py
git commit -m "feat: rewrite Stage 3 prompt, add Go Deeper prompts, update prompt dict structure"
```

---

## Task 5: Update Backend Routes

**Files:**
- Modify: `app.py` (routes at lines 1430-1779)

**Context:** Must update `/api/run-stage` for 3-stage pipeline (Stage 2 now parses Under the Hood, Stage 3 injects Playbook), rename `/api/run-explorer` to `/api/run-deeper` with 3 tab types, update admin routes for new prompt keys.

- [ ] **Step 1: Read current `run_stage()` route**

Read `app.py` lines 1430-1656 to understand the full run_stage handler.

- [ ] **Step 2: Update `run_stage()` for 3-stage pipeline**

Key changes in the route handler:

**Stage 1:** Add PLAYBOOK_DIAGNOSTICS and FCV_REFRESH_FRAMEWORK to system message construction.

**Stage 2 (was stages 2+3):**
- System message includes FCV_OPERATIONAL_MANUAL + FCV_REFRESH_FRAMEWORK + FCV_GUIDE
- After streaming completes, call `extract_under_hood()` and `extract_stage2_ratings()`
- Include parsed data in SSE done event:
```python
if stage_num == 2:
    ratings = extract_stage2_ratings(full_output)
    under_hood = extract_under_hood(full_output)
    done_data = {
        'done': True,
        'output': full_output,
        'display_text': under_hood.get('display_text', full_output),  # Stripped of delimiters for rendering
        'sensitivity_rating': ratings.get('sensitivity_rating', ''),
        'responsiveness_rating': ratings.get('responsiveness_rating', ''),
        'under_hood': {
            'recs_table': under_hood.get('recs_table', ''),
            'dnh_checklist': under_hood.get('dnh_checklist', ''),
            'questions_map': under_hood.get('questions_map', ''),
            'evidence_trail': under_hood.get('evidence_trail', '')
        },
        'parse_error': under_hood.get('error', False) or ratings.get('error', False),
        'parse_error_message': under_hood.get('message', '') or ratings.get('message', '')
    }
```

**Stage 3 (was stage 4):**
- Implement stage-awareness injection using STAGE_GUIDANCE_MAP:
```python
if stage_num == 3:
    doc_type = request_data.get('doc_type', 'Unknown')
    stage_config = STAGE_GUIDANCE_MAP.get(doc_type, STAGE_GUIDANCE_MAP.get('PCN'))
    playbook = PLAYBOOK_PREPARATION
    if stage_config.get('playbook_phase') == 'Implementation':
        playbook = PLAYBOOK_IMPLEMENTATION
    if doc_type == 'ISR':
        playbook = PLAYBOOK_IMPLEMENTATION + "\n\n" + PLAYBOOK_CLOSING

    system_msg = prompt.format(
        doc_type=doc_type,
        timing_emphasis=stage_config.get('timing_options', 'Preparation'),
        playbook_guidance=playbook
    ) + "\n\n" + FCV_REFRESH_FRAMEWORK
```
- After streaming, call `extract_priorities()` as before (now expects updated field names)
- Done event includes priorities + ratings + summaries (same structure as current, with new fields)

**Remove:** Any references to old stage 3 (gaps) or stage 4 numbering. The route should only accept stages 1, 2, 3.

- [ ] **Step 3: Create `/api/run-deeper` route (replaces `/api/run-explorer`)**

Rename the route and add tab handling:

```python
@app.route('/api/run-deeper', methods=['POST'])
def run_deeper():
    data = request.get_json()
    tab = data.get('tab', 'alternatives')
    priority_title = data.get('priority_title', '')
    priority_body = data.get('priority_body', '')
    history = data.get('history', [])
    doc_type = data.get('doc_type', 'Unknown')

    # NOTE: 'analytical_trail' tab is handled entirely client-side (no API call).
    # The frontend filters stage2_under_hood data in localStorage directly.

    if tab == 'playbook_refs':
        # LLM call with deeper_playbook prompt
        prompt = get_prompt_for_stage('deeper_playbook')
        # Select playbook content based on doc_type
        stage_config = STAGE_GUIDANCE_MAP.get(doc_type, STAGE_GUIDANCE_MAP.get('PCN'))
        playbook = PLAYBOOK_PREPARATION
        if stage_config.get('playbook_phase') == 'Implementation':
            playbook = PLAYBOOK_IMPLEMENTATION
        if doc_type == 'ISR':
            playbook += "\n\n" + PLAYBOOK_CLOSING
        prompt_with_playbook = prompt.replace('{playbook_content}', playbook)
        # Stream response via SSE — copy the SSE streaming pattern from the existing
        # run_explorer() function (lines 1658-1734 in current app.py):
        # 1. Create Anthropic client via get_client()
        # 2. Build messages array with priority context as user message
        # 3. Use client.messages.stream() with system=prompt_with_playbook
        # 4. Yield SSE chunks via Response(stream_with_context(generate()), mimetype='text/event-stream')
        # 5. On completion, yield done event with {done: True, output: full_text}

    else:  # tab == 'alternatives'
        # Same as current Explorer — use "deeper" prompt
        prompt = get_prompt_for_stage('deeper')
        # Stream response via SSE — same pattern as above and current run_explorer():
        # 1. Create Anthropic client
        # 2. Build messages with priority title/body as user message + history for context
        # 3. Stream with system=prompt
        # 4. Yield SSE chunks, then done event
```

- [ ] **Step 4: Remove old `/api/run-explorer` route**

Delete the `run_explorer()` function and route (lines 1658-1734).

- [ ] **Step 5: Rename `clean_stage4_output()` → `clean_stage3_output()`**

Rename the function (line 720) and update the call site in `run_stage()` where it is invoked for the recommendations stage (now stage 3). The internal logic stays the same.

- [ ] **Step 6: Update admin routes for new prompt keys**

Update `get_prompts()`, `set_prompts()`, `get_default_prompts()`, `reset_prompts()` to use new keys: `"1"`, `"2"`, `"3"`, `"deeper"`, `"deeper_playbook"`, `"followon"`.

- [ ] **Step 7: Commit**

```bash
git add app.py
git commit -m "feat: update routes for 3-stage pipeline, add /api/run-deeper with tab support"
```

---

## Task 6: Frontend — Stepper + Stage 1 UI

**Files:**
- Modify: `index.html` (HTML stepper at lines 1520-1526, CSS at lines 161-191, JS `setStepper()` at line 2544)

**Context:** Change from 5 steps (Upload + 4 stages) to 4 steps (Upload + 3 stages). Stage 1 UI gets project stage badge and FCS indicator. Minimal changes.

- [ ] **Step 1: Update HTML stepper**

Change the stepper at lines 1520-1526:

```html
<!-- Current: 5 steps (step-0 through step-4) -->
<!-- New: 4 steps (step-0 through step-3) -->
<div class="stepper-wrap" id="stepper-wrap" style="display:none">
  <div class="stepper">
    <div class="step done" id="step-0"><span class="step-num">0</span><span class="step-label">Upload</span></div>
    <div class="step" id="step-1"><span class="step-num">1</span><span class="step-label">Context</span></div>
    <div class="step" id="step-2"><span class="step-num">2</span><span class="step-label">Assessment</span></div>
    <div class="step" id="step-3"><span class="step-num">3</span><span class="step-label">Recommendations</span></div>
  </div>
</div>
```

- [ ] **Step 2: Update `setStepper()` function**

Update at line 2544 to loop through steps 1-3 instead of 1-4:

```javascript
function setStepper(active, status) {
    document.getElementById('step-0').className = 'step done';
    for (let i = 1; i <= 3; i++) {  // Changed from 4 to 3
        const el = document.getElementById('step-' + i);
        if (!el) continue;
        if (i < active) el.className = 'step done';
        else if (i === active) el.className = status === 'err' ? 'step err' : 'step active';
        else el.className = 'step';
    }
}
```

- [ ] **Step 3: Add project stage badge and FCS indicator to Stage 1 output**

In `renderOut()` (line 2268), when rendering Stage 1 output, add badges after the main output:

```javascript
// After Stage 1 output rendering, append badges
if (stage === 1 && result.doc_type) {
    let badgeHtml = `<div class="doc-type-badge-inline">
        <span class="badge badge-info">${escHtml(result.doc_type)} stage detected</span>
    </div>`;
    // Append after the output text
}
// FCS indicator: Stage 1 Part B web research will mention FCS status if applicable.
// The LLM is instructed to flag FCS countries in Part B output (see Stage 1 prompt).
// Detection is done via simple text match on the Stage 1 output:
if (stage === 1) {
    const outputText = result.output || '';
    const fcsMatch = /\bFCS\b|Fragile and Conflict-affected Situations list|FCV Envelope|PRA\/RECA\/TAA/i.test(outputText);
    if (fcsMatch) {
        const fcsBadge = `<div class="doc-type-badge-inline">
            <span class="badge badge-fcs">FCS country context noted</span>
        </div>`;
        // Append after doc_type badge
    }
}
```

**Note on FCS detection:** Rather than maintaining a hardcoded FCS country list (which changes annually), FCS status is detected from the LLM's Stage 1 Part B output, which is instructed by the prompt to flag FCS classification and PRA/RECA/TAA eligibility. The regex above catches common FCS-related terms in the output. This is a heuristic — a future improvement could add a dedicated LLM extraction call or reference the official FCS list API.

Add CSS for the inline badge:

```css
.doc-type-badge-inline {
    margin-top: 12px;
    padding: 8px 0;
}
.badge-info {
    background: #e8f4fd;
    color: #0050A0;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 500;
}
.badge-fcs {
    background: #fef3cd;
    color: #856404;
}
```

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: update stepper for 3-stage pipeline, add project stage badge"
```

---

## Task 7: Frontend — Stage 2 UI (new)

**Files:**
- Modify: `index.html` (JS `renderOut()` around line 2268, new CSS classes)

**Context:** Stage 2 now shows a thematic summary (main area) + ratings sidebar + 4 expandable "Under the Hood" panels. Need to parse the done event, render the summary, populate sidebar gauges, and build expandable panels.

- [ ] **Step 1: Update `renderOut()` for Stage 2**

In the `renderOut()` function, add Stage 2 handling. When `stage === 2`:

1. Use `result.display_text` (or fall back to raw output if parse_error) for main content
2. Show sidebar with gauges (same `sidebarHtml()` call, populated from `result.sensitivity_rating` and `result.responsiveness_rating`)
3. Build "Under the Hood" expandable panels from `result.under_hood`
4. If `result.parse_error`, show yellow warning banner and render raw text

```javascript
if (stage === 2) {
    // Show sidebar with gauges
    document.getElementById('fcv-sidebar').style.display = 'block';
    updateSidebar(result.sensitivity_rating, result.responsiveness_rating);

    // Build Under the Hood panels
    let hoodHtml = '';
    if (result.under_hood && !result.parse_error) {
        hoodHtml = buildUnderHoodPanels(result.under_hood);
    } else if (result.parse_error) {
        hoodHtml = `<div class="warn-banner">Assessment detail could not be parsed into panels. Full output shown below.</div>`;
        hoodHtml += `<details class="under-hood-fallback"><summary>Full assessment detail</summary><div class="out-body">${md(result.output)}</div></details>`;
    }

    // Store under_hood in localStorage for Go Deeper analytical trail
    if (result.under_hood) {
        localStorage.setItem('stage2_under_hood', JSON.stringify(result.under_hood));
    }

    // Render main summary + panels
    outputEl.innerHTML = `<div class="out-body">${md(displayText)}</div>${hoodHtml}`;
}
```

- [ ] **Step 2: Write `buildUnderHoodPanels()` function**

```javascript
function buildUnderHoodPanels(underHood) {
    const panels = [
        { key: 'recs_table', title: 'Full 12-Recommendation Assessment' },
        { key: 'dnh_checklist', title: 'Do No Harm Checklist (8 Principles)' },
        { key: 'questions_map', title: '25 Key Questions Assessment' },
        { key: 'evidence_trail', title: 'Evidence Trail' }
    ];

    return `<div class="under-hood-section">
        <h3 class="under-hood-header">Under the Hood — Detailed Assessment</h3>
        ${panels.map(p => {
            const content = underHood[p.key] || 'No data available.';
            return `<details class="under-hood-panel">
                <summary>${p.title}</summary>
                <div class="under-hood-content out-body">${md(content)}</div>
            </details>`;
        }).join('')}
    </div>`;
}
```

- [ ] **Step 3: Add CSS for Under the Hood panels**

```css
.under-hood-section { margin-top: 24px; }
.under-hood-header {
    font-size: 16px; font-weight: 600; color: #333;
    margin-bottom: 12px; padding-bottom: 8px;
    border-bottom: 2px solid #e0e0e0;
}
.under-hood-panel {
    margin-bottom: 8px; border: 1px solid #e0e0e0;
    border-radius: 8px; overflow: hidden;
}
.under-hood-panel summary {
    padding: 12px 16px; cursor: pointer; font-weight: 500;
    background: #f8f9fa; font-size: 14px;
}
.under-hood-panel[open] summary { border-bottom: 1px solid #e0e0e0; }
.under-hood-content { padding: 16px; font-size: 14px; }
.under-hood-content table { width: 100%; border-collapse: collapse; font-size: 13px; }
.under-hood-content th, .under-hood-content td { padding: 8px; border: 1px solid #ddd; text-align: left; }
.under-hood-content th { background: #f0f0f0; font-weight: 600; }
.warn-banner {
    background: #fff3cd; color: #856404; padding: 12px 16px;
    border-radius: 8px; margin-bottom: 16px; font-size: 14px;
}
```

- [ ] **Step 4: Update sidebar to work with Stage 2**

The sidebar (`sidebarHtml()` at line 2810, `updateSidebar()` at line 2852) currently only shows at Stage 4. Modify to show at Stage 2:

- In `renderOut()`, show `#fcv-sidebar` when `stage >= 2` (not just stage 4)
- `updateSidebar()` should accept ratings as parameters (currently reads from global `stageFourPriorities`)

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: build Stage 2 UI with Under the Hood panels and sidebar gauges"
```

---

## Task 8: Frontend — Stage 3 UI (enhanced recommendations)

**Files:**
- Modify: `index.html` (JS `initStage4UI()` → rename to `initStage3UI()`, `showPriority()`, `renderPriorityStepper()`, `renderPrioritiesIntro()`)

**Context:** Stage 3 UI is mostly the same as current Stage 4 UI. Need to: rename functions from "stage4" to "stage3", add `refresh_shift` badge to priority cards, update `who_acts` rendering for semicolon-separated multi-value, update `when` and `resources` rendering with new values, add project stage badge, rename section header to "Priority actions for the Task Team".

- [ ] **Step 1: Rename Stage 4 functions to Stage 3**

Global find-and-replace in `index.html`:
- `initStage4UI` → `initStage3UI`
- `stageFourPriorities` → `stageThreePriorities`
- `stage === 4` → `stage === 3` (in renderOut and other stage checks)
- References to "Stage 4" in comments → "Stage 3"
- `stage4_timestamp` → `stage3_timestamp` in localStorage keys

- [ ] **Step 2: Add `refresh_shift` badge to priority cards**

In `showPriority()` (line 2951), where it renders the priority card header chips (`.pc-hdr-chips`), add a shift badge:

```javascript
// After the existing S/R tag badge and risk badge:
const shiftBadge = p.refresh_shift
    ? `<span class="shift-badge" title="${escAttr(p.refresh_shift)}">${escHtml(p.refresh_shift.replace('Shift ', ''))}</span>`
    : '';
```

Add CSS:
```css
.shift-badge {
    background: #e8f5e9; color: #2e7d32; padding: 2px 8px;
    border-radius: 10px; font-size: 11px; font-weight: 500;
    border: 1px solid #c8e6c9;
}
```

- [ ] **Step 3: Update `who_acts` rendering for multi-value**

In `showPriority()`, where it renders `who_acts`, split on semicolons and render as multiple chips:

```javascript
// Current: single text display
// New: split and render as chips
const whoChips = (p.who_acts || '').split(';').map(w => w.trim()).filter(Boolean)
    .map(w => `<span class="who-chip">${escHtml(w)}</span>`).join(' ');
```

Add CSS:
```css
.who-chip {
    background: #f0f0f0; color: #333; padding: 2px 8px;
    border-radius: 10px; font-size: 12px; margin-right: 4px;
    display: inline-block;
}
```

- [ ] **Step 4: Update section header**

In `renderPrioritiesIntro()` (line 2911), change the header text from "Strategic Priorities" (or whatever the current text is) to "Priority actions for the Task Team".

- [ ] **Step 5: Add project stage badge to Stage 3 output**

In `renderOut()` when stage === 3, inject a badge at the top of the output:

```javascript
const stageBadge = docType
    ? `<div class="stage-awareness-badge">Recommendations tailored for <strong>${escHtml(docType)}</strong> stage</div>`
    : '';
```

CSS:
```css
.stage-awareness-badge {
    background: #e3f2fd; color: #1565c0; padding: 8px 16px;
    border-radius: 8px; font-size: 13px; margin-bottom: 16px;
    border-left: 4px solid #1565c0;
}
```

- [ ] **Step 6: Update `resources` rendering with tooltip definitions**

In `showPriority()`, add a `title` attribute to the resources display:

```javascript
const resourceTitles = {
    'Minimal': 'Existing budget — no additional allocation needed',
    'Moderate': 'Dedicated allocation — requires budget line',
    'Significant': 'Requires restructuring or additional financing'
};
// Extract base level (strip parenthetical)
const baseResource = (p.resources || '').split('(')[0].trim();
const tooltip = resourceTitles[baseResource] || '';
```

- [ ] **Step 7: Commit**

```bash
git add index.html
git commit -m "feat: enhance Stage 3 UI with shift badges, multi-value who_acts, stage awareness"
```

---

## Task 9: Frontend — Go Deeper Tabs

**Files:**
- Modify: `index.html` (JS `handleBeyondToggle()`, `loadExplorerForPriority()`, new tab functions)

**Context:** Replace current single-panel Explorer with 3-tab "Go Deeper" section. Tab 1 (alternatives) = current Explorer behaviour. Tab 2 (analytical trail) = instant from localStorage. Tab 3 (playbook refs) = new LLM call.

- [ ] **Step 1: Update `showPriority()` to render 3-tab Go Deeper**

In `showPriority()` (line 2951), replace the current `<details class="zone-act-beyond">` block with:

```javascript
const goDeeper = `
<details class="go-deeper" id="deeper-details-${idx}" ontoggle="handleDeeperToggle(this, ${idx})">
    <summary>Go Deeper (optional)</summary>
    <div class="deeper-content">
        <div class="deeper-tabs">
            <button class="deeper-tab active" onclick="switchDeeperTab(${idx}, 'alternatives', this)">Alternative approaches</button>
            <button class="deeper-tab" onclick="switchDeeperTab(${idx}, 'trail', this)">Analytical trail</button>
            <button class="deeper-tab" onclick="switchDeeperTab(${idx}, 'playbook', this)">Playbook references</button>
        </div>
        <div class="deeper-tab-content" id="deeper-content-${idx}">
            <div class="beyond-loading" id="deeper-loading-${idx}" style="display:none">
                <div class="spinner"></div>
                <span id="deeper-timer-${idx}">Loading...</span>
                <button onclick="cancelDeeper()">Cancel</button>
            </div>
            <div id="deeper-result-${idx}"></div>
        </div>
    </div>
</details>`;
```

- [ ] **Step 2: Write `switchDeeperTab()` function**

```javascript
let currentDeeperTab = {};  // Track active tab per priority

function switchDeeperTab(idx, tab, btnEl) {
    // Update active tab button
    const tabs = btnEl.parentElement.querySelectorAll('.deeper-tab');
    tabs.forEach(t => t.classList.remove('active'));
    btnEl.classList.add('active');

    currentDeeperTab[idx] = tab;

    // Check cache
    const cacheKey = `deeper_${idx}_${tab}`;
    const cached = localStorage.getItem(cacheKey);
    const resultEl = document.getElementById(`deeper-result-${idx}`);

    if (cached) {
        resultEl.innerHTML = renderDeeperContent(tab, cached);
        return;
    }

    if (tab === 'trail') {
        // Instant — client-side filter of stage2_under_hood from localStorage (no API call)
        loadAnalyticalTrail(idx);
    } else {
        // LLM call needed — show loading
        loadDeeperTab(idx, tab);
    }
}
```

- [ ] **Step 3: Write `loadAnalyticalTrail()` function (client-side only — no API call)**

Per spec: analytical trail is a frontend-only data filter. No backend round-trip.

```javascript
function loadAnalyticalTrail(idx) {
    const resultEl = document.getElementById(`deeper-result-${idx}`);
    const underHood = JSON.parse(localStorage.getItem('stage2_under_hood') || '{}');
    const dimension = stageThreePriorities[idx]?.fcv_dimension || '';

    if (!underHood.recs_table && !underHood.questions_map) {
        resultEl.innerHTML = '<p>No analytical trail data available. Complete Stage 2 first.</p>';
        return;
    }

    // Filter recs table rows by dimension (column-aware: split on | and check dimension column)
    let result = '';

    if (underHood.recs_table) {
        const lines = underHood.recs_table.trim().split('\n');
        const header = lines.slice(0, 2); // Header row + separator
        const dataRows = lines.slice(2).filter(line => {
            // Parse markdown table row — dimension is typically in a specific column
            // Match on any cell containing the dimension name as a whole word
            const cells = line.split('|').map(c => c.trim());
            return cells.some(cell => {
                const regex = new RegExp('\\b' + dimension.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b', 'i');
                return regex.test(cell);
            });
        });
        if (dataRows.length) {
            result += '### Relevant Recommendations\\n\\n' + header.concat(dataRows).join('\\n') + '\\n\\n';
        }
    }

    if (underHood.questions_map) {
        const lines = underHood.questions_map.trim().split('\n');
        const header = lines.slice(0, 2);
        const dataRows = lines.slice(2).filter(line => {
            const cells = line.split('|').map(c => c.trim());
            return cells.some(cell => {
                const regex = new RegExp('\\b' + dimension.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b', 'i');
                return regex.test(cell);
            });
        });
        if (dataRows.length) {
            result += '### Relevant Key Questions\\n\\n' + header.concat(dataRows).join('\\n') + '\\n\\n';
        }
    }

    if (underHood.evidence_trail) {
        result += '### Evidence Trail\\n\\n' + underHood.evidence_trail;
    }

    const content = result || 'No detailed analytical data available for the ' + dimension + ' dimension.';
    localStorage.setItem(`deeper_${idx}_trail`, content);
    resultEl.innerHTML = renderDeeperContent('trail', content);
}
```

- [ ] **Step 4: Write `loadDeeperTab()` function for SSE tabs**

```javascript
let deeperAbortController = null;

async function loadDeeperTab(idx, tab) {
    const loadingEl = document.getElementById(`deeper-loading-${idx}`);
    const resultEl = document.getElementById(`deeper-result-${idx}`);
    loadingEl.style.display = 'flex';
    resultEl.innerHTML = '';

    const priority = stageThreePriorities[idx];
    const promptKey = tab === 'alternatives' ? 'deeper' : 'deeper_playbook';

    deeperAbortController = new AbortController();
    let accumulated = '';
    const startTime = Date.now();
    const timerEl = document.getElementById(`deeper-timer-${idx}`);
    const timerHandle = setInterval(() => {
        const elapsed = Math.round((Date.now() - startTime) / 1000);
        timerEl.textContent = `Loading... ${elapsed}s`;
    }, 500);

    try {
        const resp = await fetch('/api/run-deeper', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                tab: tab === 'playbook' ? 'playbook_refs' : 'alternatives',
                priority_title: priority.title,
                priority_body: JSON.stringify(priority),
                history: conversationHistory,
                doc_type: docType || 'Unknown'
            }),
            signal: deeperAbortController.signal
        });

        // SSE streaming — mirrors loadExplorerForPriority() at index.html line 3103
        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let sseBuffer = '';

        while (true) {
            const { done: streamDone, value } = await reader.read();
            if (streamDone) break;
            sseBuffer += decoder.decode(value, { stream: true });

            // SSE events are separated by double newlines
            const events = sseBuffer.split('\n\n');
            sseBuffer = events.pop(); // Keep incomplete event in buffer

            for (const event of events) {
                if (!event.trim()) continue;
                for (const line of event.split('\n')) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.chunk) {
                                accumulated += data.chunk;
                                // Progressive rendering in result area
                                resultEl.innerHTML = `<div class="out-body">${md(accumulated)}</div>`;
                            }
                            if (data.done) {
                                // Final output — use data.output if available
                                if (data.output) accumulated = data.output;
                            }
                        } catch (e) { /* ignore malformed SSE lines */ }
                    }
                }
            }
        }

        clearInterval(timerHandle);
        loadingEl.style.display = 'none';

        // Cache result
        const cacheKey = `deeper_${idx}_${tab}`;
        localStorage.setItem(cacheKey, accumulated);

        // Render
        if (tab === 'alternatives') {
            const parsed = parseExplorerText(accumulated);
            resultEl.innerHTML = renderAboveAndBeyondHtml(parsed);
        } else {
            resultEl.innerHTML = renderDeeperContent('playbook', accumulated);
        }
    } catch (e) {
        clearInterval(timerHandle);
        loadingEl.style.display = 'none';
        if (e.name !== 'AbortError') {
            resultEl.innerHTML = '<p class="err-msg">Failed to load content.</p>';
        }
    }
}
```

- [ ] **Step 5: Write `renderDeeperContent()` helper**

```javascript
function renderDeeperContent(tab, content) {
    if (tab === 'trail') {
        return `<div class="deeper-trail out-body">${md(content)}</div>`;
    } else if (tab === 'playbook') {
        return `<div class="deeper-playbook out-body">${md(content)}</div>`;
    } else {
        // alternatives — parse and render as beyond-items
        const parsed = parseExplorerText(content);
        return renderAboveAndBeyondHtml(parsed);
    }
}
```

- [ ] **Step 6: Write `handleDeeperToggle()` (replaces `handleBeyondToggle()`)**

```javascript
function handleDeeperToggle(detailsEl, idx) {
    if (detailsEl.open && !currentDeeperTab[idx]) {
        // First open — default to alternatives tab
        currentDeeperTab[idx] = 'alternatives';
        const cacheKey = `deeper_${idx}_alternatives`;
        const cached = localStorage.getItem(cacheKey);
        if (cached) {
            const resultEl = document.getElementById(`deeper-result-${idx}`);
            resultEl.innerHTML = renderDeeperContent('alternatives', cached);
        } else {
            loadDeeperTab(idx, 'alternatives');
        }
    }
}
```

- [ ] **Step 7: Add CSS for Go Deeper tabs**

```css
.go-deeper { margin-top: 16px; border: 1px solid #e0e0e0; border-radius: 8px; }
.go-deeper summary { padding: 12px 16px; cursor: pointer; font-weight: 500; font-size: 14px; }
.deeper-content { padding: 16px; }
.deeper-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.deeper-tab {
    padding: 6px 16px; border-radius: 20px; border: 1px solid #ccc;
    background: #fff; cursor: pointer; font-size: 13px; font-weight: 500;
    transition: all 0.15s;
}
.deeper-tab.active { background: #0050A0; color: #fff; border-color: #0050A0; }
.deeper-tab:hover:not(.active) { background: #f0f0f0; }
.deeper-tab-content { min-height: 100px; }
.deeper-trail, .deeper-playbook { font-size: 14px; line-height: 1.6; }
```

- [ ] **Step 8: Remove old Explorer functions**

Remove or mark as deprecated:
- `loadExplorerForPriority()` (line 3103)
- `cancelExplorer()` (line 3176)
- `handleBeyondToggle()` (line 3180)
- Old `explorerAbortController` global
- Old `explorerCache` global
- Old localStorage keys `explorer_priority_${idx}`

Replace with new functions and globals.

- [ ] **Step 9: Commit**

```bash
git add index.html
git commit -m "feat: replace Explorer with Go Deeper 3-tab interface"
```

---

## Task 10: Frontend — Sidebar, Download, and Misc

**Files:**
- Modify: `index.html` (sidebar, download, S/R cards)

**Context:** Sidebar gauges need to work from Stage 2 onwards (not just Stage 4). Download needs to include new fields. S/R summary cards and risk exposure rendering stay the same but are now populated from Stage 3.

- [ ] **Step 1: Update `updateSidebar()` to accept parameters**

Currently `updateSidebar()` reads from global `stageFourPriorities`. Update to accept ratings as parameters and work from Stage 2:

```javascript
function updateSidebar(sensitivityRating, responsivenessRating, priorities) {
    // If called from Stage 2 (just ratings, no priorities yet)
    if (sensitivityRating) {
        animateGauge('fcv-arc-fill', 'fcv-shield-path', 'fcv-rating-label', 'fcv-need-label', sensitivityRating);
        animateGauge('fcv-resp-arc-fill', 'fcv-resp-leaf-path', 'fcv-resp-rating-label', 'fcv-resp-need-label', responsivenessRating);
    }
    // If called from Stage 3 (also has priorities)
    if (priorities && priorities.length) {
        renderPriorityOverview(priorities);
    }
}
```

- [ ] **Step 2: Update `downloadReport()` for new fields**

In `downloadReport()` (line 2554), add new fields to the Word export:
- `refresh_shift` per priority
- `who_acts` as multiple chips (split on semicolon)
- `when` with new values
- `resources` with parenthetical definitions

These should already be in the JSON — just ensure the download template renders them.

- [ ] **Step 3: Clear Go Deeper caches on Stage 3 re-run**

When Stage 3 is re-run, clear all `deeper_*` localStorage keys:

```javascript
// In runStage(), before starting Stage 3:
if (stage === 3) {
    // Clear Go Deeper caches
    for (let i = 0; i < 10; i++) {
        localStorage.removeItem(`deeper_${i}_alternatives`);
        localStorage.removeItem(`deeper_${i}_trail`);
        localStorage.removeItem(`deeper_${i}_playbook`);
    }
    currentDeeperTab = {};
}
```

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: update sidebar for Stage 2, download for new fields, cache management"
```

---

## Task 11: Terminology Updates + Migration

**Files:**
- Modify: `index.html` (CSS class names, JS text strings, HTML labels)
- Modify: `app.py` (error messages, stage name references)

**Context:** Global terminology sweep + legacy session detection.

- [ ] **Step 1: Frontend terminology sweep**

Search and replace throughout `index.html`:

| Search | Replace | Context |
|---|---|---|
| `"Strong"` (as status label) | `"Strongly addressed"` | Status labels in tables |
| `"Partial"` (as status label) | `"Partially addressed"` | Status labels in tables |
| `"Weak"` (as status label) | `"Weakly addressed"` | Status labels in tables |
| `"Above and beyond"` | `"Go Deeper"` | Explorer section text |
| `"Go above and beyond"` | `"Go Deeper"` | Explorer section summary text |
| `"Explorer"` (user-facing) | `"Go Deeper"` | UI labels (not variable names) |
| `"Rec. Note"` / `"Recommendations Note"` (in stepper) | `"Recommendations"` | Stepper label |
| `"FCV Risks"` (in stepper) | `"Context"` | Stepper label |
| `"Screening"` (in stepper) | `"Assessment"` | Stepper label |
| `"Gaps"` (in stepper) | (removed — merged into Assessment) | Stepper label |

- [ ] **Step 2: Backend error message updates**

In `app.py`, search for any references to "Stage 4" in error messages and update to "Stage 3":
- `extract_priorities()` error messages
- `run_stage()` error handling
- Any comment references

- [ ] **Step 3: Add legacy session detection**

In `loadSession()` function in `index.html`, add detection for old-format sessions:

```javascript
function loadSession(input) {
    // ... existing code to parse session file ...

    // Check for legacy format
    if (sessionData.conversationHistory) {
        const hasOldStage4 = sessionData.conversationHistory.some(
            msg => msg.stage === '4' || msg.stage === 4
        );
        const hasNoUnderHood = !localStorage.getItem('stage2_under_hood');

        if (hasOldStage4 || (sessionData.stageOutputs && sessionData.stageOutputs[4])) {
            // Show legacy banner
            showLegacyBanner();
            return;
        }
    }

    // ... rest of existing load logic ...
}

function showLegacyBanner() {
    const banner = document.createElement('div');
    banner.className = 'warn-banner';
    banner.innerHTML = 'This session was created with an earlier version of the screener. To use the new assessment framework, please start a new session. Your old session data is preserved.';
    banner.style.margin = '16px';
    document.getElementById('main').prepend(banner);
}
```

- [ ] **Step 4: Update prompt admin modal tabs**

In the HTML for the prompt modal (line 1363), update tabs:

```html
<!-- Current: ptab-1, ptab-2, ptab-3, ptab-4, ptab-explorer -->
<!-- New: ptab-1, ptab-2, ptab-3, ptab-deeper, ptab-deeper-playbook, ptab-followon -->
<div id="prompt-tabs">
    <button class="ptab" onclick="showPromptTab('1')">Stage 1</button>
    <button class="ptab" onclick="showPromptTab('2')">Stage 2</button>
    <button class="ptab" onclick="showPromptTab('3')">Stage 3</button>
    <button class="ptab" onclick="showPromptTab('deeper')">Go Deeper</button>
    <button class="ptab" onclick="showPromptTab('deeper_playbook')">Playbook Refs</button>
    <button class="ptab" onclick="showPromptTab('followon')">Follow-on</button>
</div>
```

- [ ] **Step 5: Commit**

```bash
git add index.html app.py
git commit -m "feat: terminology updates, legacy session detection, prompt modal tabs"
```

---

## Task 12: Integration Testing

**Files:**
- No file modifications — manual testing

**Context:** No automated test framework exists. Testing is manual: run the app locally, upload documents, verify all 3 stages work correctly.

- [ ] **Step 1: Start the app locally**

```bash
cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT"
export ANTHROPIC_API_KEY="your-key"
python app.py
```

Open http://localhost:5000 in browser.

- [ ] **Step 2: Test Stage 1 (Context & Extraction)**

Upload a test project document (e.g., the Guinea example from colleague's testing). Verify:
- Web research runs and dropdown appears
- Part A and Part B render correctly
- Project stage badge appears (e.g., "PCN stage detected")
- FCS indicator appears if applicable
- DOC_TYPE is correctly detected and stripped from display

- [ ] **Step 3: Test Stage 2 (FCV Assessment)**

Click to proceed to Stage 2. Verify:
- Assessment summary renders (~400-500 words, thematic)
- DNH traffic-light appears inline
- Sidebar gauges show sensitivity + responsiveness ratings
- "Under the Hood" panels expand correctly:
  - 12-rec table renders with all columns
  - DNH checklist renders with traffic-light status
  - 25 key questions map renders
  - Evidence trail renders
- If parse error occurs, warning banner shows and raw text displays

- [ ] **Step 4: Test Stage 3 (Recommendations Note)**

Click to proceed to Stage 3. Verify:
- Stage awareness badge appears (e.g., "Recommendations tailored for PCN stage")
- Narrative memo renders correctly
- S/R summary cards render
- Priority cards render with:
  - `refresh_shift` badge visible
  - `who_acts` as multiple chips
  - `resources` with tooltip
  - All zone-act sections (recommendation, PAD sections, suggested language, implementation note)
- Section header says "Priority actions for the Task Team"

- [ ] **Step 5: Test Go Deeper tabs**

For one priority, expand "Go Deeper". Verify:
- 3 pill tabs appear: Alternative approaches, Analytical trail, Playbook references
- **Alternatives tab:** Loads via SSE, renders 2-3 option cards (same as old Explorer)
- **Analytical trail tab:** Loads instantly from cached Stage 2 data, shows filtered recs/questions
- **Playbook references tab:** Loads via SSE, renders structured prose about operational flexibilities
- All tabs cache correctly (re-opening shows cached content without re-fetching)
- Cancel button works for in-flight requests

- [ ] **Step 6: Test Follow-on card**

At the bottom of Stage 3, verify the follow-on card:
- 4 pre-fill chips work
- Submit sends message and streams response
- Response renders below the card

- [ ] **Step 7: Test Download**

Click download. Verify Word document includes:
- All narrative sections
- All priority cards with new fields (refresh_shift, expanded who_acts, etc.)
- Go Deeper content if already loaded

- [ ] **Step 8: Test session save/load**

Save the session, refresh the page, load it back. Verify it renders correctly.

- [ ] **Step 9: Test legacy session detection**

Load an old session file (from before the redesign). Verify the legacy banner appears.

- [ ] **Step 10: Test prompt admin modal**

Open admin panel, verify 6 tabs (Stage 1, 2, 3, Go Deeper, Playbook Refs, Follow-on). Edit a prompt, save, verify it persists.

- [ ] **Step 11: Verify token budgets**

Check the Flask server logs during each stage. Verify:
- Stage 1: No timeout or truncation issues
- Stage 2: Output includes all delimiter blocks (ratings + Under the Hood)
- Stage 3: JSON block parses correctly with all new fields

- [ ] **Step 12: Final commit if any fixes needed**

```bash
git add -A
git commit -m "fix: integration testing fixes"
```

---

## Task 13: Frontend — Pass `doc_type` to Stage 3 and Go Deeper Requests

**Files:**
- Modify: `index.html` (JS `runStage()`, `loadDeeperTab()`)

**Context:** Stage 1 detects `doc_type` via `%%%DOC_TYPE%%%` and the frontend stores it in the `docType` global variable. This must be included in POST request bodies for Stage 3 and Go Deeper so the backend can do stage-aware Playbook injection.

- [ ] **Step 1: Include `doc_type` in Stage 3 request body**

In `runStage()` (line 1958), where the fetch body is constructed, add `doc_type`:

```javascript
body: JSON.stringify({
    stage: stage,
    documents: ...,
    history: conversationHistory,
    user_message: ...,
    prompt_override: ...,
    doc_type: docType || 'Unknown',  // ADD THIS
    uploaded_doc_names: ...
})
```

- [ ] **Step 2: Include `doc_type` in Go Deeper requests**

Already included in `loadDeeperTab()` from Task 9 — verify it is present in the fetch body.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: pass doc_type to Stage 3 and Go Deeper requests"
```

---

## Task 14: Clear `prompts.json` and Update `how-it-works` Page

**Files:**
- Modify: `app.py` (add prompts.json clearing on startup if old format detected)
- Modify: `index.html` or static how-it-works page (if it exists)

- [ ] **Step 1: Clear old `prompts.json` on startup**

In `app.py`, add a startup check after the `app = Flask(...)` line:

```python
# Clear stale prompts.json if it references old stage keys
if os.path.exists(PROMPTS_FILE):
    try:
        with open(PROMPTS_FILE) as f:
            old_prompts = json.load(f)
        if '4' in old_prompts or 'explorer' in old_prompts:
            os.remove(PROMPTS_FILE)
    except (json.JSONDecodeError, IOError):
        pass
```

- [ ] **Step 2: Update how-it-works page (if applicable)**

Check if `GET /how-it-works` serves a static page describing the pipeline. If it does, update references from 4 stages to 3 stages, update stage names, and update descriptions.

If it serves a simple template that dynamically renders, update the content to reflect the new pipeline.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "chore: clear old prompts.json, update how-it-works page"
```

---

## Task 15: Update `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md` (project root)

**Context:** The project CLAUDE.md has an explicit instruction: "After every substantial change to this app... update this CLAUDE.md file to reflect the change before committing." This is a major redesign requiring comprehensive updates.

- [ ] **Step 1: Read current CLAUDE.md**

Read the full `CLAUDE.md` to understand all sections that need updating.

- [ ] **Step 2: Update Section 1.3 (Stage pipeline)**

Replace the 4-stage pipeline description with the new 3-stage pipeline:
- Stage 1 → Context & Extraction (enhanced with Playbook diagnostics, FCV Refresh)
- Stage 2 → FCV Assessment (merged screening + gaps, Under the Hood panels)
- Stage 3 → Recommendations Note (stage-aware, enhanced priority cards, Go Deeper)
- Update EXPLORER section → GO DEEPER section (3 tabs: alternatives, analytical trail, playbook refs)
- Update FOLLOW-ON section (minor — Refresh framing)

- [ ] **Step 3: Update Section 3 (Prompt Architecture)**

- Update prompt locations and keys (6 prompts: 1, 2, 3, deeper, deeper_playbook, followon)
- Update Stage 2 description (merged assessment, Under the Hood delimiters)
- Update Stage 3 description (was Stage 4, now Stage 3, new fields)
- Update Explorer description → Go Deeper description

- [ ] **Step 4: Update Section 4 (Frontend Architecture)**

- Update UI panels section (3 stages, not 4)
- Update key JavaScript functions (renamed: initStage3UI, stageThreePriorities, etc.)
- Update CSS classes (new: .under-hood-*, .go-deeper, .deeper-tab, .shift-badge, etc.)
- Update removed items list
- Update terminology references

- [ ] **Step 5: Update Section 5 (Backend Routes)**

- Update route table (run-deeper replaces run-explorer, 3 stages not 4)
- Update priority parsing section (new fields, new function names)
- Update SSE done event payloads

- [ ] **Step 6: Update Section 6 (Key Implementation Details)**

- Add Under the Hood extraction details
- Add stage-awareness injection details
- Update Stage 4 references → Stage 3
- Add Go Deeper tab behaviour details

- [ ] **Step 7: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for 3-stage pipeline redesign"
```

---

## Summary

| Task | Description | Est. complexity | Dependencies |
|---|---|---|---|
| 1 | Knowledge Base expansion | High (content distillation) | None |
| 2 | Backend parsers | Medium | Task 1 |
| 3 | Stage 1 prompt | Low-Medium | Task 1 |
| 4 | Stage 2 prompt | High | Task 1 |
| 4b | Stage 3 + Deeper + Followon prompts | High | Task 1 |
| 5 | Backend routes | Medium-High | Tasks 2, 3, 4, 4b |
| 6 | Frontend stepper + Stage 1 | Low | None |
| 7 | Frontend Stage 2 | Medium | Task 5 |
| 8 | Frontend Stage 3 | Medium | Task 5 |
| 9 | Frontend Go Deeper tabs | Medium-High | Task 8 |
| 10 | Frontend sidebar + download | Medium | Tasks 7, 8 |
| 11 | Terminology + migration | Low-Medium | All above |
| 12 | Integration testing | Medium | All above |
| 13 | Pass doc_type to requests | Low | Tasks 5, 9 |
| 14 | Clear prompts.json + how-it-works | Low | Task 5 |
| 15 | Update CLAUDE.md | Medium | All above |

**Note on Task 8 (Stage 4→3 rename):** This is a high-risk find-and-replace across a 3600-line file. The implementer should search for ALL of these patterns: `stage4`, `Stage 4`, `stageFour`, `stage-4`, `stage === 4`, `stage == 4`, `stage == '4'`, `stageOutputs[4]`, `explorer_priority_`, and rename/update each occurrence carefully.

**Note on Tasks 6/7/8:** These all modify `renderOut()` in `index.html`. To avoid merge conflicts, implement them sequentially (6 → 7 → 8), not in parallel.

**Total estimated tasks:** 15 tasks, ~75 discrete steps.
