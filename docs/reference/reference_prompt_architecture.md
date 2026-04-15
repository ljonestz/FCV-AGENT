# Prompt Architecture — Detailed Reference

> Extracted from CLAUDE.md to keep the main file under the 40k context limit.
> Keep this file updated when prompt schemas, delimiters, or parsing logic change.

---

## Stage 1: "Context & Extraction"

**Purpose:** Extract FCV-relevant content from uploaded project and contextual documents, enriched by automated web research and Playbook Diagnostics framing.

**Input:** Any project document at any preparation stage (Concept Note, PID, PCN, PAD, restructuring/AF draft). Optionally 1–2 contextual documents (RRA, country risk report, etc.).

**Automated FCV web research phase (runs before LLM generation):**
1. `extract_country_name()` — brief LLM call to identify project country (first 4000 chars)
2. `extract_sector_name()` — brief LLM call to identify primary project sector
3. `run_fcv_web_research(country, sector)` — Anthropic web_search tool, 9 targeted searches, up to 5500 tokens
   - Covers: conflict/security, governance, humanitarian, economic, FCV actors, structural drivers, vulnerable groups, regional dimensions, sector-specific FCV considerations
   - Results cached in-memory by `"country::sector"` key; lost on server restart
4. Research brief injected into Stage 1 context as supplemental material
5. Research brief shown as collapsible dropdown at TOP of Stage 1 output

**Three-tier citation priority:**
- Tier 1 — Uploaded contextual docs: `[From: document name]` (highest precedence)
- Tier 2 — Automated web research: `[From: web research]` or named source (e.g. `[From: ICG]`)
- Tier 3 — Training knowledge: `[From: training knowledge]` or named org/report

**Key behaviors:**
- Part A: Extract only from the project document. No outside knowledge.
- Part B: Use tiers 1→2→3 in strict priority order; always label the source tier at each point.
- Extraction guided by Playbook Diagnostics questions (RRA utilisation, compound risks, forced displacement, CPSD)
- FCV classification context from FCV Refresh injected (is this an FCS country? what trajectory?)

**Large document handling:**
- Documents > 150,000 characters are condensed via LLM extraction (FCV-relevant content only).
- Documents > 500,000 characters are truncated to MAX_DOC_CHARS.
- Truncation warnings shown to users when triggered.

**Document type classification (embedded in Stage 1):**
- The very last line of every Stage 1 response is: `%%%DOC_TYPE: [PCN/PID/PAD/AF/Restructuring/ISR/Unknown]%%%`
- The frontend extracts this via regex when Stage 1 completes and sets the `docType` state
- The DOC_TYPE line is stripped from the display text before rendering to the user
- `docType` is passed in the Stage 3 request body for stage-aware prompt injection

**Prompt constants injected:** `FCV_GUIDE`, `PLAYBOOK_DIAGNOSTICS`, `FCV_REFRESH_FRAMEWORK`

**Loading time note:** Stage 1 loading card shows "may take 60–90 seconds" due to web research phase.

---

## Stage 2: "FCV Assessment" (merged Screening + Gaps)

**Purpose:** Assess project FCV sensitivity and responsiveness using the full OST framework. Identify gaps and Do No Harm status. Produce both a TTL-facing thematic summary and detailed analytical record for FCV CCs.

**Internal analytical engine:** All 12 OST recommendations + 25 key questions + 3 key elements. The TTL sees themed findings only — the framework structure is in "Under the Hood" panels.

**TTL-facing output (400–500 words, thematic narrative):**
- FCV Sensitivity findings: what the project addresses well, where it falls short
- Do No Harm traffic-light inline (e.g., "6 of 8 principles addressed | 1 partial | 1 gap")
- FCV Responsiveness findings: framed around the 4 FCV Refresh shifts (not old pillars)
- Key gaps: 3–5 most critical, prioritised, with evidence

**Responsiveness assessment — 4 FCV Refresh shifts:**
- Shift A: Anticipate — does the project design reflect current fragility classification?
- Shift B: Differentiate — is it calibrated to the country's FCV trajectory/context type?
- Shift C: Jobs & private sector — does it address economic livelihoods/job creation as a stability pathway?
- Shift D: Enhanced toolkit — does it leverage operational flexibilities (OP7.30, TPIs, CERC, etc.)?

**Do No Harm — canonical 8 principles:**
1. Conflict-sensitive targeting and beneficiary selection
2. Avoiding reinforcement of existing power asymmetries
3. Preventing exacerbation of inter-group tensions
4. Ensuring equitable geographic distribution of benefits
5. Safeguarding against elite capture of project resources
6. Protecting project staff and beneficiaries from security risks
7. Monitoring for unintended negative consequences
8. Establishing accessible and trusted grievance mechanisms

**Strict [S+R] definition:**
[S+R] only valid for: (1) inclusion/targeting of conflict-affected populations; (2) FCV logic in ToC/PDO; (3) adaptive M&E for harm + resilience; (4) GRM for state-citizen accountability.
If in doubt → [S] or [R].

**"Under the Hood" panels (collapsed, expandable `<details>`):**
- Panel 1: Full 12-rec assessment (table: rec | status | evidence | gaps | shift alignment)
- Panel 2: Detailed DNH checklist (8 principles, traffic-light table with evidence)
- Panel 3: 25 key questions mapping (answerable/gaps, evidence for each)
- Panel 4: Evidence trail (sources used, citation tier, confidence level)

**Delimiter blocks (stripped from display, parsed by frontend):**
```
%%%STAGE2_RATINGS_START%%%
{"sensitivity_rating": "Adequate", "responsiveness_rating": "Low"}
%%%STAGE2_RATINGS_END%%%

%%%RATING_REASONING_START%%%
[step-by-step scoring logic — auditing only]
%%%RATING_REASONING_END%%%

%%%UNDER_HOOD_START%%%
  %%%RECS_TABLE_START%%%    [12-rec table with S/R Tag column]  %%%RECS_TABLE_END%%%
  %%%DNH_CHECKLIST_START%%% [8-principle DNH checklist]         %%%DNH_CHECKLIST_END%%%
  %%%QUESTIONS_MAP_START%%% [25 key questions with findings]    %%%QUESTIONS_MAP_END%%%
  %%%EVIDENCE_TRAIL_START%%% [sources, types, contributions]    %%%EVIDENCE_TRAIL_END%%%
%%%UNDER_HOOD_END%%%
```

**Backend parsing functions:**
- `extract_stage2_ratings()` — parses `%%%STAGE2_RATINGS_START/END%%%` → `{sensitivity_rating, responsiveness_rating}`; also extracts `%%%RATING_REASONING_START/END%%%` → `rating_reasoning`
- `extract_under_hood()` — parses `%%%UNDER_HOOD_START/END%%%` → `{recs_table, dnh_checklist, questions_map, evidence_trail}`
- `clean_stage2_output()` — strips ratings + under_hood + rating_reasoning blocks from display text

**Rating Rubric (v7.5):**
- **Sensitivity:** Count of 12 OST recs rated "Strongly/Partially addressed" → 6-tier baseline. Quality gates cap if 3+ DNH gaps, no conflict analysis, or no geographic specificity.
- **Responsiveness:** Count of 4 FCV Refresh shifts actively addressed → 6-tier baseline. Quality gates cap if zero shift alignment or no adaptive M&E.
- **Stage 3 inheritance:** Stage 3 copies Stage 2 ratings verbatim — no independent rating generation.

**Error handling:** If `extract_under_hood()` fails, `parse_error: true` in SSE done event; raw text shown; yellow banner displayed; Stage 3 can still proceed.

**Prompt constants injected:** `FCV_OPERATIONAL_MANUAL`, `FCV_REFRESH_FRAMEWORK`, `FCV_GUIDE`

---

## Stage 3: "Recommendations Note" (stage-aware)

**Purpose:** Generate a formal, memo-ready Recommendations Note with actionable priority cards, tailored to the project's lifecycle stage using Playbook guidance.

**Stage-awareness logic (doc_type passed in request body):**
- PCN/PID → PLAYBOOK_PREPARATION, timing: "Identification / Preparation"
- PAD → PLAYBOOK_PREPARATION, timing: "Preparation / Appraisal"
- AF/Restructuring → PLAYBOOK_IMPLEMENTATION, timing: "Implementation / Restructuring"
- ISR → PLAYBOOK_IMPLEMENTATION + PLAYBOOK_CLOSING, timing: "Implementation"
- Unknown → PLAYBOOK_PREPARATION (safe default)

**Narrative output structure:**
```
Preamble (50–75 words)
Opening Assessment (1 bold sentence)
Operational Context (150–200 words)
FCV Risk Exposure:
  RISKS_TO_PROJECT: How FCV dynamics threaten project delivery
  RISKS_FROM_PROJECT: How project design could worsen fragility
Strengths (80–120 words)
Gaps (100–130 words)
FCV Sensitivity Summary (80–100 words) ← extracted via delimiter, shown as card
FCV Responsiveness Summary (80–100 words) ← extracted via delimiter, shown as card
Stage badge (e.g., "Recommendations tailored for PCN stage")
```

**JSON block format (appended after narrative):**
```
%%%JSON_START%%%
{
  "fcv_rating": "Adequate",
  "fcv_responsiveness_rating": "Low",
  "sensitivity_summary": "...",
  "responsiveness_summary": "...",
  "risk_exposure": {
    "risks_to": "...",
    "risks_from": "..."
  },
  "priorities": [
    {
      "title": "Priority 1 · [Actionable verb phrase]",
      "fcv_dimension": "Inclusion",
      "tag": "[S]",
      "refresh_shift": "Shift B: Differentiate",
      "risk_level": "High",
      "the_gap": "...",
      "why_it_matters": "...",
      "actions": [
        {
          "document_element": "ESCP Commitment (new)",
          "guidance": "2–4 sentences describing what to add/revise and why",
          "suggested_language": "2–3 sentences of ready-to-paste draft PAD text"
        }
      ],
      "who_acts": "TTL; PIU",
      "when": "Preparation",
      "resources": "Moderate (dedicated allocation)",
      "pad_sections": "Annex 5: Stakeholder Engagement Plan; ESCP Commitment #4",
      "implementation_note": "1–2 sentences on timing, cost, or key dependency"
    }
  ]
}
%%%JSON_END%%%
```

**Field value sets:**
- `tag`: `[S]` | `[R]` | `[S+R]`
- `refresh_shift`: `Shift A: Anticipate` | `Shift B: Differentiate` | `Shift C: Jobs & private sector` | `Shift D: Enhanced toolkit`
- `risk_level`: `High` | `Medium` | `Low`
- `who_acts` (semicolon-separated): `TTL` | `PIU` | `Government` | `FCV CC` | `FM Team` | `ESF Team` | `Technical Team` | `M&E Team`
- `when`: `Identification` | `Preparation` | `Appraisal` | `Implementation` | `Restructuring`
- `resources`: `Minimal (existing budget)` | `Moderate (dedicated allocation)` | `Significant (requires restructuring)`

**`actions` array rules:**
- 2–4 structured actions per priority, each naming a specific document element to revise
- Must NOT be an options menu ("Consider A / Or B / Or C" is NOT allowed)
- Must name specific location, mechanism, and entry point in guidance
- S/R pillar justification sentence required in `why_it_matters` for [R] and [S+R] priorities

**`extract_priorities()` return shape:**
```python
{
  'error': bool,
  'message': str,              # only when error=True
  'priorities': [...],
  'fcv_rating': str,
  'fcv_responsiveness_rating': str,
  'sensitivity_summary': str,
  'responsiveness_summary': str,
  'risk_exposure': {'risks_to': str, 'risks_from': str}
}
# Each priority also gets: specificity_warning (bool), citation_warnings (list)
```

**`clean_stage3_output()` stripping order:**
1. Strip `%%%JSON_START%%%...%%%JSON_END%%%` block
2. Strip `%%%RISK_NARRATIVE_START%%%...%%%RISK_NARRATIVE_END%%%` block
3. Strip everything from `%%%PRIORITIES_START%%%` onwards
4. Fallback legacy delimiter stripping: `%%%RISK_EXPOSURE_START/END%%%`, `%%%SENSITIVITY_SUMMARY_START/END%%%`, `%%%RESPONSIVENESS_SUMMARY_START/END%%%`, `%%%FCV_RATING/RESPONSIVENESS_RATING%%%`, `%%%PRIORITY_START/END%%%`, `%%%GAP_TABLE_START/END%%%`

**Citation policy:**
- ONLY cite documents that appeared as `[From: document name]` in Stage 1. NEVER fabricate titles.
- Non-uploaded sources → `[From: training knowledge]` or `[From: web research]`
- `uploaded_doc_names` must be in `/api/run-stage` request body for citation check

**Prompt constants injected:** stage-appropriate PLAYBOOK constant + `FCV_REFRESH_FRAMEWORK`

---

## Go Deeper "alternatives" tab output format (legacy — tab removed in v7.2, prompt retained)

- Only `%%%GO_FURTHER_START%%%...%%%GO_FURTHER_END%%%` markers used
- Each item uses `%%%GF_ITEM%%%` + `%%%GF_TITLE%%%` markers
- Parsed by `parseGoFurtherText()` → `goFurtherItems[]`
- Rendered by `renderGoFurtherHtml(parsed)` into `.beyond-item` cards

---

*Last updated: 2026-04-05 — split from CLAUDE.md v7.5*
