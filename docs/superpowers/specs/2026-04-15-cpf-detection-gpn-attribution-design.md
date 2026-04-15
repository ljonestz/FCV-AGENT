# Design: CPF Detection, GPN Attribution & CPF Action-Card Links

**Date:** 2026-04-15
**Branch:** feat/v8.2-gpn-cpf-integration
**Status:** Approved — ready for implementation

---

## Background

Three related issues surfaced during live review of v8.2:

1. Stage 2 Q3 ("Is the project linked to CPF FCV objectives?") reports "No CPF available" even when a CPF was uploaded and Stage 1 extracted it correctly. Detection is filename-only and fails when the file has a non-standard name.
2. Good Practice Notes (Peace & Inclusion Lens, Strategic DRR Framing) are injected into Stage 2 but never cited in output — the prompt instructs the LLM to integrate them silently.
3. Stage 3 `cpf_alignment` field exists at priority level. User wants a brief CPF reference inside individual action cards where a genuine linkage exists.

---

## Issue A — CPF Detection: Content-Based Fallback

### Problem
Detection in all four CPF-signal injection sites (Stage 2 step-by-step, Stage 2 express, Stage 3 step-by-step, Stage 3 express) relies solely on uploaded filename matching against `['cpf', 'country partnership framework', 'partnership framework']`. A file named "Niger_FY26_Strategy.pdf" passes through undetected even if it is a CPF.

### Solution
Extract a shared helper function `_detect_cpf_present(uploaded_names, conversation_history)` that runs two checks in sequence:

**Check 1 — Filename:** unchanged existing logic.

**Check 2 — Stage 1 content fallback:** If Check 1 fails, scan all `assistant` role messages in `conversation_history` for the substrings `"CPF"` or `"Country Partnership Framework"`. If either is found, CPF is considered present.

```python
def _detect_cpf_present(uploaded_names, conversation_history):
    cpf_terms = ['cpf', 'country partnership framework', 'partnership framework']
    # Check 1: filename
    if any(any(t in n.lower() for t in cpf_terms) for n in uploaded_names):
        return True
    # Check 2: Stage 1 content
    for msg in conversation_history:
        if msg.get('role') == 'assistant':
            content = msg.get('content', '')
            if 'CPF' in content or 'Country Partnership Framework' in content:
                return True
    return False
```

### Scope
- Replace all four inline CPF detection blocks with calls to `_detect_cpf_present()`
- Place the helper near the top of `app.py` with the other utility functions
- Express path passes `documents` list as uploaded_names (same as now); step-by-step path passes `uploaded_doc_names_payload`

### Files
- `app.py`: add helper, replace 4 detection sites

---

## Issue B — GPN Attribution in Stage 2 Output

### Problem
The Stage 2 prompt Peace & Inclusion Lens instruction currently says "Do not expose these dimensions as separate framework labels in the TTL-facing output — integrate them into the thematic narrative as analytical depth." The LLM interprets this as "never name the source" — so GPNs are never cited in either the narrative or the evidence trail.

### Solution
Two prompt changes in `DEFAULT_PROMPTS["2"]`:

**Change 1 — Peace & Inclusion Lens instruction (TTL narrative section):**
Replace "Do not expose these dimensions as separate framework labels" with: "Integrate findings into themes naturally. Where a finding draws directly on these dimensions, add a brief inline attribution at the end of the relevant sentence: `(Good Practice Notes — Peace & Inclusion Lens)`. Do not use it as a section heading."

**Change 2 — Evidence trail instruction (Under the Hood):**
The mandatory GPN rows added in the previous commit are correct. Strengthen to: "These rows are required even if you believe the dimensions were not directly applicable — in that case, write 'Assessed — no gaps identified' in the Used For column."

### Files
- `app.py`: edit `DEFAULT_PROMPTS["2"]` — Peace & Inclusion Lens paragraph and evidence trail instruction

---

## Issue C — CPF References in Action Cards (Stage 3)

### Problem
CPF presence is signalled at priority level via `cpf_alignment`. User wants a brief, natural 1-sentence reference inside individual `actions[]` guidance text where a specific action would strengthen a CPF priority or outcome.

### Solution
Prompt-only change — no schema changes, no parsing changes, no rendering changes.

Add the following instruction to the `actions[]` schema description in `DEFAULT_PROMPTS["3"]`:

> "For each action, if implementing that specific action would directly help strengthen or contribute to a named CPF priority or outcome (as identified in the CPF content extracted in Stage 1), add a single sentence at the end of the `guidance` field: 'This would also help advance [CPF outcome/priority name].' Only add this where a genuine, specific linkage exists — do not add it to every action, and do not fabricate CPF outcome names."

The sentence appears as the last sentence of the existing `guidance` string, which renders naturally in the action accordion card without any UI changes.

Additionally, strengthen `CPF_INTEGRATION_GUIDE` in `background_docs.py` to mention that linkages can be noted at the action level, not just the priority level.

### Files
- `app.py`: edit `DEFAULT_PROMPTS["3"]` actions[] schema description
- `background_docs.py`: add one line to `CPF_INTEGRATION_GUIDE`

---

## Files Modified

| File | Changes |
|---|---|
| `app.py` | Add `_detect_cpf_present()` helper; replace 4 detection sites; edit Stage 2 prompt GPN attribution; edit Stage 3 prompt actions[] CPF instruction |
| `background_docs.py` | Strengthen `CPF_INTEGRATION_GUIDE` action-level note |
| `index.html` | None |

---

## Out of Scope
- No schema changes to priority JSON
- No rendering changes in `index.html`
- No changes to `extract_priorities()` parsing
- No new UI elements
