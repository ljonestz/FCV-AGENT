# Design Spec: Good Practice Notes + CPF Integration (v8.2)

**Date:** 2026-04-14
**Status:** Approved
**Scope:** Embed FCV Good Practice Notes into analytical backbone; add CPF upload and alignment linkage

---

## 1. Problem Statement

The FCV Project Screener's analytical backbone currently draws from three primary sources: the FCV Operational Manual (OST), the FCV Operational Playbook, and the FCV Strategy Refresh. Two official WBG Good Practice Notes — **Peace & Inclusion Lenses** (Dec 2022) and **FCV Sensitive Programming** (Jul 2022) — contain additional project-level screening dimensions and strategic framing that are not yet embedded in the app.

Additionally, the Country Partnership Framework (CPF) is the overarching WBG country engagement document that every project operates under, but the app does not currently prompt users to upload it or link recommendations back to CPF outcomes.

### What this changes

1. **Good Practice Notes** — Enrich the existing `FCV_OPERATIONAL_MANUAL` constant with non-duplicative content from both GPNs, treating the OST as the primary framework and the GPNs as supplementary depth
2. **CPF integration** — Accept CPF as a named contextual document; extract in Stage 1; link Stage 3 recommendations to CPF outcomes via a new `cpf_alignment` field
3. **Source attribution** — Reference Good Practice Notes wherever the app lists its analytical sources

### What this does NOT change

- No new stages or workflow modes
- No changes to Stage 2 rating rubric or Under the Hood panel structure
- No web search for CPFs (upload-only)
- No changes to Go Deeper, Follow-on, or Express mode logic

---

## 2. Architecture: Knowledge Source Map

The following diagram shows how all knowledge sources feed into the 3-stage pipeline. Items marked **[NEW]** are additions in this spec.

```
 KNOWLEDGE SOURCES                          PIPELINE STAGES
 ==================                         ===============

 +----------------------------------+
 |  FCV_GUIDE (~3k tokens)          |-----> Stage 1 (Context & Extraction)
 |  Core S/R definitions,           |-----> Stage 2 (FCV Assessment)
 |  Refresh shifts, screening Qs    |
 +----------------------------------+

 +----------------------------------+
 |  FCV_OPERATIONAL_MANUAL           |-----> Stage 2 (FCV Assessment)
 |  (~5k tokens, enriched)           |
 |  12 OST recs + 25 key questions  |
 |  + 3 key elements + Box 1 & 2    |
 |  + Peace & Inclusion Lens dims   | [NEW]
 |  + Strategic DRR framing          | [NEW]
 +----------------------------------+

 +----------------------------------+
 |  FCV_REFRESH_FRAMEWORK (~1.5k)   |-----> Stage 1
 |  4 strategic shifts, FCV          |-----> Stage 2
 |  classification scheme            |-----> Stage 3 (Recommendations)
 +----------------------------------+

 +----------------------------------+
 |  PLAYBOOK_DIAGNOSTICS (~2k)      |-----> Stage 1
 |  RRA methodology, data sources    |
 +----------------------------------+

 +----------------------------------+
 |  PLAYBOOK_PREPARATION (~2k)      |-----> Stage 3 (PCN/PID/PAD)
 |  Preparation-phase guidance       |
 +----------------------------------+

 +----------------------------------+
 |  PLAYBOOK_IMPLEMENTATION (~2k)   |-----> Stage 3 (AF/Restructuring/ISR)
 |  Implementation-phase guidance    |
 +----------------------------------+

 +----------------------------------+
 |  PLAYBOOK_CLOSING (~1k)          |-----> Stage 3 (ISR)
 |  ICR and closing guidance         |
 +----------------------------------+

 +----------------------------------+
 |  FCS_LIST (~1k)                  |-----> Stage 1
 |  39 current FCS + 9 graduated    |-----> Stage 2
 +----------------------------------+

 +----------------------------------+
 |  WB_INSTRUMENT_GUIDE (dict)      |-----> Stage 1 (per instrument type)
 |  IPF/PforR/DPO/TA/MPA/IPF-DDO   |
 +----------------------------------+

 +----------------------------------+
 |  FCV_INSTRUMENT_CALIBRATION      |-----> Stage 2
 |  DPF failure modes, FCV Envelope |
 +----------------------------------+

 +----------------------------------+
 |  FCV_GLOSSARY (dict, 29 terms)   |-----> Stage 1 (tooltip/lookup)
 +----------------------------------+

 +----------------------------------+
 |  WB_PROCESS_GUIDE (dict)         |-----> Stage 1 (lifecycle context)
 |  MTR/ISR/AF/Restructuring/ICR    |
 +----------------------------------+

 +----------------------------------+       +-----------------------------+
 |  CPF_INTEGRATION_GUIDE (~400t)   | [NEW] |                             |
 |  How to use CPF content when     |-----> | Stage 3 (Recommendations)   |
 |  uploaded; cpf_alignment field    |       |                             |
 +----------------------------------+       +-----------------------------+


 USER-UPLOADED DOCUMENTS                    HOW THEY FLOW
 ========================                   ==============

 +----------------------------------+
 |  Project document (required)     |-----> Stage 1 Part A (extraction)
 |  PCN / PID / PAD / AF / Restr.   |       then all stages via history
 +----------------------------------+

 +----------------------------------+
 |  Contextual documents (optional) |-----> Stage 1 Part B (contextualised)
 |  RRA, CPF [NEW], PPSD, conflict  |       then all stages via history
 |  analysis, technical studies,     |
 |  stakeholder analysis             |
 +----------------------------------+

 +----------------------------------+
 |  Web research (auto, Stage 1)    |-----> Stage 1 Part B (Tier 2 source)
 |  9-search brief, cached by       |       then all stages via history
 |  country::sector                  |
 +----------------------------------+


 STAGE PIPELINE FLOW
 ====================

 Stage 1: Context & Extraction
 |  Inputs: project doc + contextual docs (incl. CPF if uploaded) + web research
 |  Outputs: Part A (doc extract) + Part B (contextualised) + classifier lines
 |  Knowledge: FCV_GUIDE, PLAYBOOK_DIAGNOSTICS, FCV_REFRESH_FRAMEWORK,
 |             FCS_LIST, WB_INSTRUMENT_GUIDE, FCV_GLOSSARY, WB_PROCESS_GUIDE
 |
 v
 Stage 2: FCV Assessment
 |  Inputs: Stage 1 output (conversation history)
 |  Outputs: thematic narrative + ratings + Under the Hood blocks
 |  Knowledge: FCV_OPERATIONAL_MANUAL (enriched with GPN content [NEW]),
 |             FCV_REFRESH_FRAMEWORK, FCV_GUIDE, FCS_LIST,
 |             FCV_INSTRUMENT_CALIBRATION
 |
 v
 Stage 3: Recommendations Note
    Inputs: Stages 1-2 history + doc_type + instrument_type + temporal_context
    Outputs: narrative memo + JSON priorities (with cpf_alignment [NEW])
    Knowledge: stage-appropriate PLAYBOOK, FCV_REFRESH_FRAMEWORK, FCV_GUIDE,
               CPF_INTEGRATION_GUIDE [NEW]
```

---

## 3. Detailed Changes

### 3.1 `background_docs.py` — Enrich `FCV_OPERATIONAL_MANUAL`

Add two new subsections at the end of the existing constant, before the closing `"""`.

#### New subsection: Peace & Inclusion Lens Dimensions (~600 tokens)

Source: Good Practice Note on Peace and Inclusion Lenses (Dec 2022)

Content to distill (non-duplicative with existing OST content):

| GPN concept | What it adds beyond OST |
|---|---|
| Geographic targeting against RRA-identified divides | OST Rec 2 mentions targeting but doesn't link to subnational RRA mapping; GPN explicitly ties project geographic scope to RRA-identified fault lines (north/south, ethnic, regional) |
| Social cohesion and reconciliation | OST Box 2 briefly mentions; GPN expands with inter-group dialogue, community dispute resolution, state legitimacy through local service delivery |
| Project-cycle-specific application | GPN is explicit: greatest impact at earliest design stages; separate considerations for concept, appraisal, MTR, restructuring |
| Stakeholder engagement with conflict actors | OST mentions FCV-affected groups; GPN adds explicit attention to non-beneficiaries, conflict actors, and use of local languages |
| Unintended consequences framework | GPN provides structured positive/negative examples (exclusion, elite capture, undermining resilience vs. bolstering cohesion, legitimacy) |

#### New subsection: Strategic DRR Framing (~400 tokens)

Source: Good Practice Note on FCV Sensitive Program and Portfolio Analysis (Jul 2022)

Content to distill (used as contextual guidance, not direct screening questions):

| GPN concept | How it applies at project level |
|---|---|
| DRR mapping (Drivers, Risks, Resilience) | Individual project findings should be interpreted against the wider landscape of FCV drivers, risks to project from FCV, and resilience factors the project can leverage |
| 4 P's framework | Recommendations can be clustered around Policies (reform/regulatory), Programming (project design/targeting), Partnerships (HDP nexus, UN, NGOs), Personnel (staffing, capacity, security) |
| Strategic vs. operational recommendations | Distinguish between recommendations that require strategic/portfolio-level action vs. those actionable within the project |
| Positive/negative unintended consequences | Structured lens: could the project inadvertently increase inequality, undermine state legitimacy, exacerbate grievances, or weaken resilience? Conversely, could it bolster cohesion, strengthen institutions, or address root causes? |

### 3.2 `background_docs.py` — New constant: `CPF_INTEGRATION_GUIDE`

~400 tokens. Content:

```
## Country Partnership Framework (CPF) Integration Guide

### What is a CPF?
The CPF is the World Bank Group's main country-level strategic engagement document,
typically covering a 5-6 year period. It defines the overarching goals, outcomes,
and areas of engagement for all WBG activities in a country. Every project operates
under the CPF's strategic umbrella.

### When CPF content is available
If the user has uploaded a CPF among the contextual documents, use it to:
1. Identify the CPF's stated outcomes, priority sectors, and FCV-related commitments
2. Note where the project under review aligns with or supports specific CPF outcomes
3. For each priority recommendation, assess whether it strengthens a CPF outcome
4. Populate the `cpf_alignment` field with a 1-2 sentence statement linking the
   recommendation to the relevant CPF outcome, or null if no CPF was provided

### How to reference CPF content
- Cite the CPF by its formal title and period (e.g., "Niger CPF FY26-FY31")
- Reference specific outcomes by number/name as stated in the CPF
- Do not fabricate CPF content — only reference what was extracted in Stage 1
- If a recommendation does not clearly map to any CPF outcome, set cpf_alignment
  to null rather than forcing a weak connection
```

### 3.3 `app.py` — Prompt changes

#### Stage 2 prompt (`DEFAULT_PROMPTS["2"]`)

Add 1-2 sentences in the thematic assessment instructions:

> "When generating thematic findings, also consider Peace & Inclusion Lens dimensions from the enriched operational manual: geographic targeting against RRA-identified subnational divides, social cohesion and reconciliation dynamics, stakeholder inclusion of conflict actors and non-beneficiaries, and the potential for positive or negative unintended consequences."

No structural change to the prompt.

#### Stage 3 prompt (`DEFAULT_PROMPTS["3"]`)

**CPF alignment paragraph** — add after the existing priority generation instructions:

> "If a Country Partnership Framework (CPF) was provided among the contextual documents in Stage 1, identify which CPF outcome(s) each priority recommendation supports or strengthens. Populate the `cpf_alignment` field with a 1-2 sentence statement linking the recommendation to the relevant CPF outcome. If no CPF was provided, set `cpf_alignment` to null."

**4 P's framing** — add to the recommendation narrative guidance:

> "Where relevant, frame recommendations in terms of the 4 P's: Policies (reform, regulatory), Programming (project design, targeting), Partnerships (HDP nexus, UN, NGOs), and Personnel (staffing, capacity, security). This framing shapes the narrative memo and the `guidance` field within actions — it does not require a separate JSON field."

**JSON schema** — add `cpf_alignment` field to the priority object:

```json
"cpf_alignment": "This recommendation strengthens CPF Outcome 1 (Healthier, Better Educated and Skilled Population) by ensuring FCV-sensitive targeting in education interventions." | null
```

Add to the field validation note: "The `cpf_alignment` field should be null (not 'Not identified') when no CPF was uploaded."

#### Stage 3 prompt — source attribution line

Update any preamble text that lists analytical sources to include:

> "...grounded in the WBG FCV Strategy Refresh, FCV Operational Manual (OST), FCV Operational Playbook, and Good Practice Notes on Peace & Inclusion Lenses and FCV-Sensitive Programming."

### 3.4 `app.py` — Backend changes

#### `extract_priorities()` function

- Accept `cpf_alignment` as a valid field (string or null)
- No validation beyond type check — content is free-text

#### `CPF_INTEGRATION_GUIDE` injection

- Import `CPF_INTEGRATION_GUIDE` from `background_docs.py`
- Inject into Stage 3 system message alongside `FCV_REFRESH_FRAMEWORK` and stage-appropriate PLAYBOOK
- Inject unconditionally (the constant itself tells the LLM to use it only when CPF content is present in history)

### 3.5 `index.html` — Frontend changes

#### Contextual upload zone hint

**Line ~1926** — update zone hint text:
> "Upload 1-3 documents with FCV context for the country or region — e.g., RRA, **Country Partnership Framework (CPF)**, country risk assessment, conflict analysis, technical studies, PPSD, or stakeholder analysis."

**Line ~2056** — update tooltip text similarly, adding CPF to the list.

#### `showPriority()` — CPF alignment zone

Add a conditional zone between "Why it matters" and "How to act":

```html
${pr.cpf_alignment ? `
<div class="pc-zone zone-cpf">
  <div class="pc-zone-title">
    <div class="pc-zone-icon">[link/globe icon SVG]</div>
    CPF Alignment
  </div>
  <div class="pc-zone-body">${esc(pr.cpf_alignment)}</div>
</div>` : ''}
```

Styling: `.zone-cpf` gets a 3px left border in `rgba(0, 159, 218, 0.25)` (WB blue at 25% opacity) and a light blue background tint `rgba(0, 159, 218, 0.04)`.

#### `downloadReport()` — DOCX export

For each priority with non-null `cpf_alignment`, add a line after "Why it matters":
> **CPF Alignment:** {cpf_alignment text}

#### Source attribution in UI

Update the following locations to include Good Practice Notes in the analytical source list:

1. **Landing page introductory text** — where the app describes its analytical framework
2. **Stage 2 Under the Hood Panel 4** (Evidence trail) — reference Good Practice Notes as part of the analytical framework
3. **Stage 3 narrative memo** — the prompt already handles this (section 3.3 above)
4. **Download report methodology note** — add to the disclaimer/methodology section of the `.docx` export

Consistent phrasing across all locations:
> "...grounded in the WBG FCV Strategy Refresh, FCV Operational Manual (OST), FCV Operational Playbook, and Good Practice Notes on Peace & Inclusion Lenses and FCV-Sensitive Programming."

### 3.6 `CLAUDE.md` — Documentation updates

- Add `CPF_INTEGRATION_GUIDE` to the constants list in section 1.2
- Add `cpf_alignment` to the Stage 3 JSON field list in section 1.3
- Note Good Practice Notes as part of the analytical backbone in the Overview
- Update version to v8.2

---

## 4. Files Changed

| File | Change type | Description |
|---|---|---|
| `background_docs.py` | Edit | Enrich `FCV_OPERATIONAL_MANUAL` with 2 new subsections (~1k tokens); add `CPF_INTEGRATION_GUIDE` constant (~400 tokens) |
| `app.py` | Edit | Stage 2 prompt: 1-2 sentence addition; Stage 3 prompt: CPF alignment paragraph + JSON field + 4 P's framing + source attribution; `extract_priorities()`: accept `cpf_alignment`; import + inject `CPF_INTEGRATION_GUIDE` |
| `index.html` | Edit | Upload zone hint text (2 locations); `showPriority()`: conditional CPF alignment zone; `downloadReport()`: CPF alignment in export; source attribution (3-4 locations) |
| `CLAUDE.md` | Edit | Update constants list, JSON schema, version |

---

## 5. What is NOT in scope

- No web search for CPFs (upload-only, per decision)
- No changes to Stage 2 rating rubric or thresholds
- No new Under the Hood panels
- No changes to Go Deeper, Follow-on, or Express mode logic
- No new stages or workflow modes
- No changes to the Peace & Inclusion Lens or Portfolio Analysis GPNs being treated as separate constants (merged into OST per Approach B decision)

---

## 6. Testing Checklist

- [ ] Stage 2 thematic findings reference Peace & Inclusion Lens dimensions when relevant (geographic targeting, social cohesion, unintended consequences)
- [ ] Stage 2 output does NOT duplicate OST content (no repeated screening questions)
- [ ] Stage 3 priorities include `cpf_alignment` field when CPF was uploaded
- [ ] Stage 3 priorities have `cpf_alignment: null` when no CPF was uploaded
- [ ] CPF alignment zone renders in priority cards only when non-null
- [ ] CPF alignment appears in downloaded `.docx` report
- [ ] Upload zone hint text mentions CPF
- [ ] Source attribution mentions Good Practice Notes in: landing page, Under the Hood Panel 4, download report
- [ ] Token overhead is minimal (~1.4k tokens total across enriched OST + CPF guide)
- [ ] Express mode still works (no structural pipeline changes)
