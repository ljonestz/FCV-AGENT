# Implementation Review Mode — Design Archive

**Status:** Deferred — backend complete, frontend disabled pending redesign of Stage 3 output  
**Branch:** `feat/v8-knowledge-base`  
**Last updated:** 2026-04-12  
**Reason for deferral:** Stage 3 Recommendations Note requires a fundamentally different structure for implementation-stage documents (MTR/ISR), distinct from the design-stage recommendations note. The current Stage 3 output is optimised for PAD-stage recommendations; course-correction recommendations for active projects need different fields, framing, and document targets.

---

## What Is Already Built

### Backend (`app.py`)

All backend code is complete and committed. The following functions and prompts are production-ready but gated behind the `review_mode` parameter (only triggered when `review_mode == 'implementation'`).

#### New functions

```python
def extract_process_type(stage1_output: str) -> str:
    """Extracts %%%PROCESS_TYPE: ...%%% from Stage 1 impl output.
    Valid values: MTR | ISR | AF | Restructuring | ICR | Unknown"""

def get_process_slice(process_type: str) -> str:
    """Returns formatted WB_PROCESS_GUIDE entry for the detected process type.
    Injects into Stages 2 and 3 prompts. Falls back to MTR."""
```

#### New DEFAULT_PROMPTS keys

| Key | Purpose |
|---|---|
| `impl_1` | Stage 1 for implementation documents — extracts context, detects process type (MTR/ISR), instruments, temporal context, and FCV conditions at current implementation stage |
| `impl_2` | Stage 2 for implementation — assesses FCV performance against OST operational standards; uses same delimiter structure as design Stage 2 (Under the Hood panels, ratings) but reframed for implementation reality |
| `impl_3` | Stage 3 for implementation — generates course-correction recommendations; uses same JSON structure as design Stage 3 but with implementation-specific fields, document targets, and framing |

#### Route changes

Both `/api/run-stage` and `/api/run-express` read `review_mode` from the request payload:
- `'design'` (default) → uses existing `1`, `2`, `3` prompts
- `'implementation'` → uses `impl_1`, `impl_2`, `impl_3` prompts

Stage 1 done events include `process_type` and `review_mode` fields when in implementation mode.

---

### Frontend (`index.html`)

The following frontend elements exist but are currently **disabled** (Implementation Review card has `pointer-events:none`):

- `reviewMode` and `processType` state variables declared
- `selectReviewMode()` function — updates zone hints, start button label, localStorage
- Review type selector UI (`#review-type-section`, `#rt-design`, `#rt-implementation`)
- `review_mode` and `process_type` passed in all API payloads
- `processType` captured from Stage 1 `stage_done`/`done` events
- Temporal context panel: shows process type when in implementation mode
- Express progress titles: switch to implementation-specific labels
- `getStageActivityText()`: returns implementation-specific messages

**To re-enable**: Remove `review-type-card-disabled` class and `aria-disabled` attribute from `#rt-implementation` in `index.html`. The backend is already wired.

---

## What Needs Redesign Before Re-enabling

### Stage 3 output structure

The current Stage 3 output is designed for **design-stage recommendations**:
- Recommends changes to PAD sections, ESCP commitments, Results Framework indicators
- `pad_sections` field maps to PAD document elements
- `when` field references preparation/appraisal lifecycle stages
- Suggested language is written for insertion into project preparation documents

For **implementation-stage course corrections**, the output needs:
- Recommendations targeting ISR rating narrative sections, aide-mémoire action points, restructuring triggers
- `when` field referencing implementation milestones (e.g., before next ISR, by MTR, at restructuring)
- Suggested language written for ISR narrative boxes, mission aide-mémoire, or TTL supervision notes
- Different document targets: ISR ratings narrative, aide-mémoire, mission back-to-office notes, mission workplan

### MTR vs ISR distinction (critical)

| Dimension | MTR | ISR |
|---|---|---|
| Scope | Comprehensive backward+forward review at project midpoint | Operational progress flag per supervision mission |
| Output | MTR report with recommendations, potentially triggering restructuring | ISR rating + short narrative per component |
| FCV lens | Full re-assessment of theory of change, design validity in FCV context | Flag whether FCV conditions have changed since last supervision |
| Recommendations | Can trigger redesign, restructuring, AF scope change | Operational adjustments within current design |
| Document targets | MTR report sections, restructuring paper trigger, post-MTR workplan | ISR rating narrative boxes, aide-mémoire action points |

The `impl_2` and `impl_3` prompts currently treat MTR and ISR as broadly similar with process-specific nuances. A full redesign should create separate prompt paths for MTR (comprehensive) vs ISR (operational flags).

### Potential Stage 3 fields for implementation mode

```json
{
  "process_type": "MTR",
  "overall_fcv_performance_rating": "Adequate",
  "key_finding": "100-word summary of FCV performance since approval",
  "course_corrections": [
    {
      "title": "Action title",
      "priority_level": "High | Medium | Low",
      "fcv_dimension": "...",
      "tag": "[S] | [R] | [S+R]",
      "what_has_changed": "What FCV condition has changed since appraisal",
      "operational_gap": "What the project is currently missing",
      "recommended_action": "Specific action for the task team",
      "document_target": "ISR Component Rating narrative | Aide-mémoire Section X | Restructuring trigger",
      "who_acts": "TTL; FCV CC; PIU",
      "by_when": "Before next ISR | At MTR | Within 3 months",
      "restructuring_trigger": true/false
    }
  ],
  "rating_trajectory": "Improving | Stable | Deteriorating",
  "restructuring_warranted": true/false,
  "restructuring_rationale": "If true, why restructuring should be considered"
}
```

---

## Related Knowledge Base Content

### `WB_PROCESS_GUIDE` in `background_docs.py`

Complete entries exist for:
- `MTR` — purpose, scope, key policies, typical documents, FCV considerations, common pitfalls, backward/forward look
- `ISR` — same structure

These are already injected into `impl_2` and `impl_3` via `get_process_slice()`. No changes needed here.

### IPF fields added to `WB_INSTRUMENT_GUIDE`

Two new fields added to the IPF entry for FCV-specific operational risks:
- `cdd_sub_modality` — CDD elite capture, exclusion, sustainability risks
- `non_state_actor_engagement` — Para 18 applicability, armed group engagement guardrails

These apply in both design and implementation modes.

---

## Suggested Re-activation Steps

When ready to build Implementation Review:

1. **Redesign Stage 3 JSON schema** for implementation mode (separate from design Stage 3)
2. **Update `impl_3` prompt** to use new schema; ensure MTR and ISR have distinct recommendation framing
3. **Update `extract_priorities()`** in `app.py` to handle implementation-mode JSON structure (may need separate parsing path)
4. **Update `showPriority()` and priority card rendering** in `index.html` for implementation-specific fields
5. **Consider separate ISR and MTR prompt paths** within `impl_2` and `impl_3`
6. **Re-enable the frontend**: Remove `review-type-card-disabled` from `#rt-implementation`
7. **Test with a real MTR report** and a real ISR document

Estimated scope: 1–2 development sessions for Stage 3 redesign + testing.

---

## Deferred Enhancements (Post-MVP)

- ISR rating trajectory analysis (flag improvement/deterioration from prior ISR)
- AF "defensive vs constructive" detection (AF as emergency response vs planned expansion)
- ICR honesty lens (whether ICR accurately captures FCV failures)
- Separate Stage 2 path for ISR (shorter, operational flags only — full OST assessment not appropriate for ISR cadence)
