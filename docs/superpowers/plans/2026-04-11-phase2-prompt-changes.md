# Phase 2: Prompt Changes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the Phase 1 knowledge base into the Stage 1/2/3 prompts to fix instrument awareness, temporal anchoring, PDO scope bounding, simplicity recognition, concept recognition, and logical consistency — the core issues from practitioner feedback.

**Architecture:** Prompt text changes in `DEFAULT_PROMPTS` dict in `app.py`, plus backend injection logic updates to pass instrument slices, glossary, and temporal context to the right stages. New delimiter blocks for temporal context extraction. New parsing functions for instrument type and temporal markers.

**Tech Stack:** Python (app.py prompts, routes, parsing), Flask backend

**Spec:** `docs/superpowers/specs/2026-04-11-colleague-feedback-response-design.md` — Workstream 1 (sections 4.1–4.6) + Workstream 0 (section 3.3 injection strategy)

**This is Plan 2 of 4:**
- Phase 1: Knowledge Base (complete)
- Phase 2: Prompt Changes (this plan)
- Phase 3: Frontend UX
- Phase 4: Implementation Review Pipeline

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `app.py` | Modify | Update DEFAULT_PROMPTS stages 1/2/3; add instrument type + temporal context parsing; update injection logic in run-stage and run-express routes |

---

### Task 1: Add instrument type and temporal context extraction to Stage 1 prompt

**Files:**
- Modify: `app.py` — `DEFAULT_PROMPTS["1"]` (lines ~195-279)

The Stage 1 prompt currently ends with `%%%DOC_TYPE:...%%%`. We need to add extraction of instrument type and temporal context markers, plus instructions for abbreviation handling and concept recognition.

- [ ] **Step 1: Read the current Stage 1 prompt ending**

Read `app.py` lines 260-280 to see the current DOC_TYPE extraction and quality guidelines.

- [ ] **Step 2: Add instrument type, temporal context, and concept recognition instructions**

Find the `# Document Type` section near the end of the Stage 1 prompt (around line 276-279):
```
# Document Type
At the very end of your response, after all sections, output a single classifier line:
%%%DOC_TYPE: [exactly one of: PCN / PID / PAD / AF / Restructuring / ISR / Unknown]%%%
Identify what type of World Bank project document was uploaded as the primary project document.
```

Replace with:
```
# Abbreviation and Concept Recognition
If the document contains an Abbreviations/Acronyms section or table, parse it and use those definitions throughout your analysis. When encountering abbreviations in the document text (e.g., IE for Impact Evaluation, GIS for Geographic Information System), resolve them using the document's own definitions.

When assessing against FCV recommendations, recognise the concept and intent, not just specific terms. Each recommendation represents a principle that can be fulfilled through multiple approaches. For example:
- Geospatial monitoring includes: GEMS, GIS, geo-localization, satellite imagery, remote sensing, spatial analysis, geo-referenced mapping
- Independent verification includes: TPM, third-party monitoring, independent spot checks, remote verification
- Impact evaluation includes: IE, rigorous evaluation, experimental design, quasi-experimental methods, RCT
- Capacity building includes: crisis management capacity, institutional strengthening for resilience, recovery planning — not just M&E capacity
- Digital tools includes: geospatial platforms, mobile data collection, digital GRM, remote monitoring, SMS feedback — not limited to any single platform

# Instrument Type and Temporal Context Extraction
At the very end of your response, after all narrative sections, output these classifier blocks in order:

%%%DOC_TYPE: [exactly one of: PCN / PID / PAD / AF / Restructuring / ISR / Unknown]%%%
Identify what type of World Bank project document was uploaded as the primary project document.

%%%INSTRUMENT_TYPE: [exactly one of: IPF / PforR / DPO / TA / MPA / IPF-DDO / Unknown]%%%
Identify the World Bank financing instrument. Look for: "Investment Project Financing" or component-based design (IPF); "Program-for-Results" or DLI references (PforR); "Development Policy" or prior actions (DPO); "Technical Assistance" or ASA (TA); "Multiphase Programmatic Approach" or phase references (MPA); "Deferred Drawdown" or trigger mechanism (IPF-DDO). If the Data Sheet specifies the instrument, use that.

%%%TEMPORAL_CONTEXT_START%%%
approval_date: [Board approval date or preparation date if PCN/PID, in format YYYY-MM or "Unknown"]
closing_date: [Project closing date if available, in format YYYY-MM or "Unknown"]
safeguards_framework: [One of: ESF / OP-BP / ESSA / PSIA / Unknown — determined from the document's Data Sheet or text, NOT assumed]
other_temporal_markers: [Any restructuring dates, AF dates, or other significant temporal markers found in the document, or "None identified"]
%%%TEMPORAL_CONTEXT_END%%%

CRITICAL: Determine the safeguards framework from the DOCUMENT ITSELF (Data Sheet, text references to specific OPs or ESS standards), not from the approval date. If the document references OP/BP 4.01, 4.12, etc., the framework is OP-BP. If it references ESS1-ESS10, ESCP, ESRS, the framework is ESF. If it references ESSA, the framework is ESSA (PforR). If it references PSIA, the framework is PSIA (DPO). Do not assume based on date alone.
```

- [ ] **Step 3: Add PDO/ToC extraction instruction to Part A**

Find the `### Data Gaps in the Project Document` section in the Stage 1 prompt (around line 225-226). After it and before `### Playbook-Guided Extraction`, add:

```
### PDO, Theory of Change, and Scope Markers
Extract the following from the project document:
- The Project Development Objective (PDO) statement — quote it exactly as written
- The Theory of Change (ToC) summary — key causal chain from activities to outcomes
- Results Framework scope — what indicators are tracked, what geographic/thematic scope they cover
- Any explicit scope boundaries stated in the document (e.g., "this is a national project", "focused on X regions")
These will be used in subsequent stages to bound the assessment to the project's stated scope.
```

- [ ] **Step 4: Verify the prompt is syntactically valid (no unescaped braces etc.)**

Run: `cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT" && python -c "from app import DEFAULT_PROMPTS; p = DEFAULT_PROMPTS['1']; print(f'Stage 1 prompt: {len(p)} chars'); print('Last 200 chars:', p[-200:])"`

Expected: prompt loads without error, last 200 chars show the new temporal context block.

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat: add instrument type, temporal context, and concept recognition to Stage 1 prompt"
```

---

### Task 2: Add instrument type and temporal context parsing functions

**Files:**
- Modify: `app.py` — add new parsing functions after existing `extract_stage2_ratings()`

- [ ] **Step 1: Add extract_instrument_type() function**

Add after the `extract_stage2_ratings()` function (around line 148):

```python
def extract_instrument_type(stage1_output: str) -> str:
    """Extract instrument type from Stage 1 output.
    Looks for %%%INSTRUMENT_TYPE: ...%%% line.
    Falls back to 'Unknown' if not found.
    """
    m = re.search(r'%%%INSTRUMENT_TYPE:\s*([^%]+)%%%', stage1_output)
    if not m:
        return 'Unknown'
    result = m.group(1).strip()
    valid = {'IPF', 'PforR', 'DPO', 'TA', 'MPA', 'IPF-DDO', 'Unknown'}
    return result if result in valid else 'Unknown'


def extract_temporal_context(stage1_output: str) -> dict:
    """Extract temporal context from Stage 1 output.
    Looks for %%%TEMPORAL_CONTEXT_START%%%...%%%TEMPORAL_CONTEXT_END%%% block.
    Returns dict with approval_date, closing_date, safeguards_framework, other_temporal_markers.
    """
    pattern = r'%%%TEMPORAL_CONTEXT_START%%%(.*?)%%%TEMPORAL_CONTEXT_END%%%'
    m = re.search(pattern, stage1_output, re.DOTALL)
    if not m:
        return {
            'approval_date': 'Unknown',
            'closing_date': 'Unknown',
            'safeguards_framework': 'Unknown',
            'other_temporal_markers': 'None identified',
            'error': True
        }
    block = m.group(1).strip()
    ctx = {'error': False}
    for field in ['approval_date', 'closing_date', 'safeguards_framework', 'other_temporal_markers']:
        fm = re.search(rf'{field}:\s*(.+)', block)
        ctx[field] = fm.group(1).strip() if fm else 'Unknown'
    return ctx
```

- [ ] **Step 2: Update clean_stage1_output to strip new delimiter blocks from display**

The Stage 1 output currently has `%%%DOC_TYPE:...%%%` stripped by the frontend. We need to also strip the new blocks. Find where Stage 1 output is stored in the workflow_events function (around line 2077-2081 in the `if stage == 1:` post-processing block). After `full_text = ''.join(collected)`, add extraction logic.

Actually, Stage 1 doesn't have a clean function — the delimiter lines are stripped by the frontend. But we need to extract the instrument type and temporal context server-side for passing to subsequent stages. Add extraction after the streaming completes for Stage 1:

Find the Stage 1 post-processing block (around line 2077):
```python
                if stage == 1:
                    updated_messages = [
                        {"role": "user", "content": "[Stage 1 — project documents and FCV context analysed]"},
                        {"role": "assistant", "content": full_text}
                    ]
```

Before this block, add:
```python
                # Stage 1: extract instrument type and temporal context
                if stage == 1:
                    _instrument_type = extract_instrument_type(full_text)
                    _temporal_context = extract_temporal_context(full_text)
```

And add these to the done_data for Stage 1:
```python
                    done_data['instrument_type'] = _instrument_type
                    done_data['temporal_context'] = _temporal_context
```

- [ ] **Step 3: Verify**

Run: `cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT" && python -c "from app import extract_instrument_type, extract_temporal_context; print(extract_instrument_type('Some text %%%INSTRUMENT_TYPE: IPF%%% more text')); print(extract_temporal_context('%%%TEMPORAL_CONTEXT_START%%%\napproval_date: 2020-06\nclosing_date: 2025-12\nsafeguards_framework: ESF\nother_temporal_markers: None identified\n%%%TEMPORAL_CONTEXT_END%%%'))"`

Expected: `IPF` and a dict with the four fields.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add instrument type and temporal context parsing functions"
```

---

### Task 3: Update Stage 2 prompt with instrument awareness, scope bounding, simplicity, and consistency

**Files:**
- Modify: `app.py` — `DEFAULT_PROMPTS["2"]` (lines ~282-534)

This is the most significant prompt change. Six additions to the Stage 2 prompt.

- [ ] **Step 1: Add instrument awareness to the analytical framework**

Find the section after the 12 OST recommendations list (around line 312-316):
```
## 25 Key Questions
Answer each where evidence permits, noting which are answerable and which have evidence gaps.

## 3 Key Elements
Evaluate: (1) Flexible Operational Design, (2) Tailored Implementation & Partnerships, (3) Strengthened Implementation Support
```

Add BEFORE this section:
```
## Instrument Awareness — CRITICAL
{instrument_guidance}

When assessing this project, apply the instrument-specific knowledge above. For each of the 12 OST recommendations:
- If a recommendation is NOT APPLICABLE to this instrument type, mark it as "N/A — not applicable to [instrument]" in the Under the Hood table. N/A recommendations do NOT count toward or against the rating.
- Only assess recommendations that are relevant to this instrument's capabilities and scope.
- The rating denominator becomes: applicable recs addressed / applicable recs (NOT addressed / 12).

Apply the same logic to DNH principles — some manifest differently under different instruments (e.g., DPOs work through policy, not direct service delivery, so beneficiary-level DNH assessment is different).
```

- [ ] **Step 2: Add temporal anchoring guardrail**

Find the `# Important Guidelines` section at the end of the Stage 2 prompt (around line 524). Add BEFORE it:
```
# TEMPORAL ANCHORING — CRITICAL
{temporal_guardrail}
Assess this project by the standards, policies, and events available as of the preparation/approval period identified above. Do NOT penalise for:
- Events that occurred AFTER the document was prepared (coups, crises, policy changes)
- Policy frameworks that did not exist at the time of preparation (e.g., do not reference ESF for a project using OP/BP safeguards, or vice versa)
- Knowledge that was not reasonably available to the team at preparation time
Post-preparation developments may be noted as context but must NOT affect the assessment ratings.
```

- [ ] **Step 3: Add PDO/scope bounding**

Add after the temporal anchoring block:
```
# PDO AND SCOPE BOUNDING — CRITICAL
Evaluate FCV integration WITHIN the stated PDO, Theory of Change, and Results Framework scope as extracted in Stage 1. 
- If an OST recommendation falls outside the operation's stated scope, mark it as "Beyond scope" in the Under the Hood table rather than "Weakly addressed" or "Not addressed". Beyond-scope items do NOT count toward or against the rating.
- Do not penalise a national project for lacking regional-level activities.
- Do not penalise an IPF for lacking DPO-style policy conditionality.
- Do not penalise a deliberately narrow project for not covering all possible FCV dimensions.
- Do not recommend things beyond the PDO/scope and then rate the project low for not doing them.
```

- [ ] **Step 4: Add simplicity recognition**

Add after scope bounding:
```
# SIMPLICITY RECOGNITION
A deliberately simple, fit-for-purpose design with fewer components, a lean results framework, and narrow scope may be an intentional and appropriate FCV strategy — particularly for IPF in high-fragility settings where implementation capacity is limited, or where the team plans a follow-on AF to scale up. Do not penalise lean design. Assess whether the design elements that ARE present are FCV-informed, not whether every possible FCV element is included. If you identify a deliberately lean design, note this in the rating reasoning and adjust the denominator accordingly (similar to N/A for instrument, but for intentional scope choices).
```

- [ ] **Step 5: Add logical consistency requirement**

Add after simplicity recognition:
```
# LOGICAL CONSISTENCY
Before finalising your output, review your findings for internal contradictions. If you identify tension between findings (e.g., a project both addresses resource scarcity AND potentially intensifies competition for resources), explicitly reconcile the tension with reasoning rather than stating both flatly. Acknowledge nuance — real FCV analysis often holds tensions — but explain your reasoning so the reader understands your analytical logic. Unreconciled contradictions undermine the credibility of the assessment.
```

- [ ] **Step 6: Update the rating rubric to account for N/A and beyond-scope**

Find the sensitivity rating rubric (around line 408-418). After the table, add:
```
IMPORTANT: When counting "recs addressed", exclude any recommendations marked "N/A — not applicable to [instrument]" or "Beyond scope" from BOTH the numerator AND denominator. The rating is based only on applicable, in-scope recommendations.
```

Find the responsiveness rating rubric (around line 428-435). After the table, add the same note.

- [ ] **Step 7: Verify prompt loads**

Run: `cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT" && python -c "from app import DEFAULT_PROMPTS; p = DEFAULT_PROMPTS['2']; print(f'Stage 2 prompt: {len(p)} chars'); assert '{instrument_guidance}' in p; assert '{temporal_guardrail}' in p; print('Placeholders present')"`

- [ ] **Step 8: Commit**

```bash
git add app.py
git commit -m "feat: add instrument awareness, scope bounding, simplicity, and consistency to Stage 2 prompt"
```

---

### Task 4: Update Stage 3 prompt with scope-bounded recommendations and Horizon Considerations

**Files:**
- Modify: `app.py` — `DEFAULT_PROMPTS["3"]` (lines ~537-757)

- [ ] **Step 1: Add instrument awareness and temporal guardrail placeholders**

Find the `## Stage Awareness` section (around line 542-547). After `{playbook_guidance}`, add:
```

## Instrument Awareness
{instrument_guidance}
All recommendations MUST be feasible under this instrument type. Do not suggest DPO-style policy conditionality for an IPF, or IPF-style CERC for a PforR. Use only the operational levers available to this instrument.

## Temporal Anchoring
{temporal_guardrail}
Do NOT criticise the document for lacking information about events or policies that post-date its preparation. Frame post-preparation developments as "looking ahead" considerations, not gaps.
```

- [ ] **Step 2: Add scope bounding to priority generation**

Find the section about priority generation (around line 629-637). Add after "Each priority MUST:":
```
- Fall WITHIN the project's stated PDO, Theory of Change, and Results Framework scope
- Be achievable under the identified instrument type (use only the levers available to this instrument)
```

- [ ] **Step 3: Add Horizon Considerations section to the output structure**

Find the section after the priority JSON schema (around line 700-710, before the closing quality check). Add a new section:
```
## HORIZON CONSIDERATIONS (after the JSON block)

After the %%%JSON_END%%% block, add a separate section:

### Horizon Considerations
*These observations fall outside the project's stated PDO/scope but may be relevant for the team's broader awareness. They do not affect the FCV ratings above.*

List 2-4 beyond-scope FCV considerations that the team should be aware of. These may include:
- Legitimate FCV concerns that fall outside the current operation's mandate
- Analytical tensions from Stage 2 that could not be fully reconciled
- Emerging risks that may become relevant in future operations or restructuring
- Cross-sectoral FCV dynamics that affect the project environment but are beyond its scope

Format each as a brief paragraph (2-3 sentences). Do NOT include these in the JSON block or priority cards — they are narrative-only.

Wrap this section in delimiters:
%%%HORIZON_START%%%
[Your horizon considerations here]
%%%HORIZON_END%%%
```

- [ ] **Step 4: Update the Stage 3 format placeholders to include instrument_guidance and temporal_guardrail**

The Stage 3 prompt uses `{doc_type}`, `{timing_emphasis}`, and `{playbook_guidance}` as format placeholders. We need to add `{instrument_guidance}` and `{temporal_guardrail}` to the format call. This is handled in Task 5 (backend injection).

- [ ] **Step 5: Verify prompt loads**

Run: `cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT" && python -c "from app import DEFAULT_PROMPTS; p = DEFAULT_PROMPTS['3']; print(f'Stage 3 prompt: {len(p)} chars'); assert '{instrument_guidance}' in p; assert '{temporal_guardrail}' in p; assert 'HORIZON' in p; print('All new sections present')"`

- [ ] **Step 6: Commit**

```bash
git add app.py
git commit -m "feat: add scope bounding, instrument awareness, and Horizon Considerations to Stage 3 prompt"
```

---

### Task 5: Update backend injection logic for all stages

**Files:**
- Modify: `app.py` — `run_stage()` route handler and `run_express()` route handler

This task wires the new knowledge base constants into the right stages per the injection strategy from the spec.

- [ ] **Step 1: Update Stage 2 injection to include instrument slice and glossary**

Find the Stage 2 injection block (around line 1903-1912):
```python
            if stage == 2:
                stage_prompt = (
                    stage_prompt +
                    "\n\n--- WBG FCV Operational Manual ... ---\n" +
                    FCV_OPERATIONAL_MANUAL +
                    "\n\n--- WBG FCV Strategy Refresh Framework (4 Shifts) ---\n" +
                    FCV_REFRESH_FRAMEWORK +
                    "\n\n--- WBG FCV Sensitivity and Responsiveness Guide ---\n" +
                    FCV_GUIDE
                )
```

Replace with:
```python
            if stage == 2:
                # Get instrument type from request (passed from Stage 1 via frontend)
                instrument_type = data.get('instrument_type', 'Unknown')
                instrument_slice = get_instrument_slice(instrument_type)
                temporal_ctx = data.get('temporal_context', {})
                temporal_guardrail = _build_temporal_guardrail(temporal_ctx)

                # Format instrument and temporal placeholders in prompt
                try:
                    stage_prompt = stage_prompt.format(
                        instrument_guidance=instrument_slice,
                        temporal_guardrail=temporal_guardrail,
                    )
                except KeyError:
                    pass

                stage_prompt = (
                    stage_prompt +
                    "\n\n--- WBG FCV Operational Manual (12 Recommendations, 25 Key Questions, 3 Key Elements) ---\n" +
                    FCV_OPERATIONAL_MANUAL +
                    "\n\n--- WBG FCV Strategy Refresh Framework (4 Shifts) ---\n" +
                    FCV_REFRESH_FRAMEWORK +
                    "\n\n--- WBG FCV Sensitivity and Responsiveness Guide ---\n" +
                    FCV_GUIDE +
                    "\n\n--- FCV Glossary (Key Term Definitions) ---\n" +
                    get_glossary_for_prompt()
                )
```

- [ ] **Step 2: Update Stage 3 injection to include instrument slice and temporal guardrail**

Find the Stage 3 injection block (around line 1916-1947). Update the `.format()` call to include new placeholders:

```python
            elif stage == 3:
                doc_type = data.get('doc_type', document_type or 'Unknown')
                instrument_type = data.get('instrument_type', 'Unknown')
                instrument_slice = get_instrument_slice(instrument_type)
                temporal_ctx = data.get('temporal_context', {})
                temporal_guardrail = _build_temporal_guardrail(temporal_ctx)

                stage_config = STAGE_GUIDANCE_MAP.get(doc_type, STAGE_GUIDANCE_MAP.get('Unknown', {}))
                # ... existing playbook logic ...

                try:
                    stage_prompt = stage_prompt.format(
                        doc_type=doc_type,
                        timing_emphasis=timing_str,
                        playbook_guidance=playbook,
                        instrument_guidance=instrument_slice,
                        temporal_guardrail=temporal_guardrail,
                    )
                except KeyError:
                    pass

                stage_prompt = (
                    stage_prompt +
                    "\n\n--- WBG FCV Strategy Refresh Framework (4 Shifts) ---\n" +
                    FCV_REFRESH_FRAMEWORK
                )
```

- [ ] **Step 3: Update Stage 1 injection to include instrument slice**

Find where Stage 1 background docs are appended (around line 2030-2035):
```python
                    content_parts.append({"type": "text", "text": (
                        "\n\n--- WBG FCV Sensitivity and Responsiveness Guide (always included) ---\n" + FCV_GUIDE +
                        "\n\n--- FCV Operational Playbook — Diagnostics Phase (always included) ---\n" + PLAYBOOK_DIAGNOSTICS +
                        "\n\n--- WBG FCV Strategy Refresh Framework (always included) ---\n" + FCV_REFRESH_FRAMEWORK
                    )})
```

Add the instrument guide context for Stage 1 (inject ALL instruments briefly so Stage 1 can identify the type):
```python
                    # Brief instrument recognition guide for Stage 1 identification
                    _instrument_recognition = "\n".join([
                        f"- **{k}** ({v['name']}): {v['description'][:200]}..."
                        for k, v in WB_INSTRUMENT_GUIDE.items()
                    ])
                    content_parts.append({"type": "text", "text": (
                        "\n\n--- WBG FCV Sensitivity and Responsiveness Guide (always included) ---\n" + FCV_GUIDE +
                        "\n\n--- FCV Operational Playbook — Diagnostics Phase (always included) ---\n" + PLAYBOOK_DIAGNOSTICS +
                        "\n\n--- WBG FCV Strategy Refresh Framework (always included) ---\n" + FCV_REFRESH_FRAMEWORK +
                        "\n\n--- WBG Instrument Types (for identification) ---\n" + _instrument_recognition
                    )})
```

- [ ] **Step 4: Add _build_temporal_guardrail helper**

Add this helper function near `get_instrument_slice()`:

```python
def _build_temporal_guardrail(temporal_ctx: dict) -> str:
    """Build a temporal anchoring guardrail string from extracted temporal context."""
    if not temporal_ctx or temporal_ctx.get('error'):
        return (
            "Temporal context could not be determined from the document. "
            "Apply current standards but note this limitation."
        )
    parts = []
    ad = temporal_ctx.get('approval_date', 'Unknown')
    cd = temporal_ctx.get('closing_date', 'Unknown')
    sf = temporal_ctx.get('safeguards_framework', 'Unknown')
    tm = temporal_ctx.get('other_temporal_markers', 'None identified')
    if ad != 'Unknown':
        parts.append(f"Project approval/preparation date: {ad}")
    if cd != 'Unknown':
        parts.append(f"Project closing date: {cd}")
    if sf != 'Unknown':
        parts.append(f"Safeguards framework: {sf}")
    if tm != 'None identified':
        parts.append(f"Other temporal markers: {tm}")
    if not parts:
        return "Temporal context could not be determined."
    return "TEMPORAL CONTEXT (from document):\n" + "\n".join(parts)
```

- [ ] **Step 5: Add Horizon Considerations parsing**

Add after `extract_temporal_context()`:

```python
def extract_horizon_considerations(stage3_output: str) -> str:
    """Extract Horizon Considerations section from Stage 3 output.
    Returns the text content or empty string if not found.
    """
    m = re.search(r'%%%HORIZON_START%%%(.*?)%%%HORIZON_END%%%', stage3_output, re.DOTALL)
    return m.group(1).strip() if m else ''
```

Update `clean_stage3_output()` to strip the horizon block from display text (it will be shown separately). Add this line in the function:
```python
    text = re.sub(r'%%%HORIZON_START%%%.*?%%%HORIZON_END%%%', '', text, flags=re.DOTALL)
```

Update the Stage 3 done_data to include horizon considerations:
```python
                    done_data['horizon_considerations'] = extract_horizon_considerations(full_text)
```

- [ ] **Step 6: Update run_express() with same injection logic**

The `run_express()` route runs all 3 stages sequentially. It needs the same instrument type and temporal context extraction and injection. Find the express Stage 2 and Stage 3 message building and apply the same injection pattern.

- [ ] **Step 7: Verify the full pipeline**

Run: `cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT" && python -c "
from app import (
    DEFAULT_PROMPTS, get_instrument_slice, get_glossary_for_prompt,
    extract_instrument_type, extract_temporal_context, extract_horizon_considerations,
    _build_temporal_guardrail
)
# Test temporal guardrail
ctx = {'approval_date': '2020-06', 'closing_date': '2025-12', 'safeguards_framework': 'ESF', 'other_temporal_markers': 'None identified', 'error': False}
print(_build_temporal_guardrail(ctx))
print('---')
# Test horizon extraction
print(extract_horizon_considerations('text %%%HORIZON_START%%%\nSome considerations\n%%%HORIZON_END%%% more text'))
print('---')
print('ALL OK')
"`

- [ ] **Step 8: Commit**

```bash
git add app.py
git commit -m "feat: wire instrument slices, temporal guardrails, and glossary into stage injection logic"
```

---

## Summary

After completing all 5 tasks, the prompt pipeline is updated:

| Change | Stage 1 | Stage 2 | Stage 3 |
|---|---|---|---|
| Instrument type extraction | New delimiter block | Receives from S1, formats rubric | Receives from S1, bounds recommendations |
| Temporal context extraction | New delimiter block | Receives guardrail, bounds assessment | Receives guardrail, bounds recommendations |
| PDO/scope bounding | Extracts PDO/ToC/RF | "Beyond scope" marking in rubric | Recommendations within scope; Horizon Considerations for beyond-scope |
| Simplicity recognition | — | Rubric modifier for lean design | — |
| Concept recognition | Abbreviation handling + concept families | — | — |
| Logical consistency | — | Self-consistency check instruction | Unresolved tensions in Horizon section |
| Instrument slice injection | Brief recognition guide | Full instrument slice | Full instrument slice |
| Glossary injection | — | Full glossary for prompt | — |

**Phase 3 (Frontend UX)** will consume the new `instrument_type`, `temporal_context`, and `horizon_considerations` fields in the SSE done events to display the temporal context panel, glossary tooltips, Horizon Considerations panel, and expanded badge labels.
