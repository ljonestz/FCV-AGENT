# Climate-FCV South Sudan Final Validation Handover

**Date:** 2026-07-31
**Purpose:** Restart-safe handover after the South Sudan content and interface refinement
**Application:** FCV Project Screener, Render/Flask build
**Branch:** `feat/climate-country-bank`
**Validated application commit:** `fdb9c19`
**Draft PR:** [ljonestz/FCV-AGENT#59](https://github.com/ljonestz/FCV-AGENT/pull/59)
**Live service:** <https://fcv-agent.onrender.com>

## 1. Current status

The redesigned Climate-FCV module, approved South Sudan country bank, and final
readout refinements are implemented, tested, pushed, deployed, and validated in a
fresh end-to-end production run. The resulting South Sudan Recommendations Note is
substantively strong and the desktop layout is working as intended. No further
defect was identified that warrants another production run in this session.

The approved South Sudan bank was conclusively used. Live web research made two
attempts but did not pass the evidence gate, so the system correctly excluded it
and generated a `bank-only` assessment. This is a safe fallback and did not impair
the reviewed output, but the evidence-gate rejection remains a useful diagnostic
follow-up before relying on `bank+research` in future country runs.

## 2. Repository and deployment state

| Item | State |
|---|---|
| Worktree | `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\climate-country-bank` |
| Branch | `feat/climate-country-bank` |
| Validated commit | `fdb9c19 feat: polish climate FCV readout and research retry` |
| Remote | Synchronized with `origin/feat/climate-country-bank` before this handover commit |
| Draft PR | <https://github.com/ljonestz/FCV-AGENT/pull/59> |
| Render branch | `feat/climate-country-bank` |
| Validated Render build | `fdb9c19868e8` |
| South Sudan bank version | `2026.07.south-sudan-pilot` |
| Private dual-build parity log | `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md` updated; never commit publicly |

The companion bank remains pinned as a submodule. The earlier handover at
`docs/20260731_climate_country_bank_handover.md` contains the full architecture,
methodology, approval workflow, source inventory, and historical deployment record.
This document supersedes its operational status and next steps, but not that
background detail.

## 3. Final changes implemented

### 3.1 Opening and integration readout

- Replaced the colored Climate-FCV module card with a plain narrative opening.
- Added a two-to-three-sentence scene setter covering the project, FCV context,
  climate context, and their interaction before the project-specific significance.
- Retained `Why it matters` within the same narrative flow.
- Replaced reader-facing `materiality` terminology with `climate relevance`.
- Kept the gauge concise and added an explanatory subtitle. For `Adequate`, the
  production text is: `Opportunities to further strengthen climate and FCV elements`.
- Removed duplicative advisory and evidence-availability prose from the gauge.

### 3.2 Executive readout and core questions

- Renamed the green/red comparison to `Executive readout`.
- Softened the negative heading to `Where the design could be strengthened`.
- Standardized the typography of the two comparison panels.
- Expanded both mandatory climate/project interaction sections to component-anchored
  multi-paragraph analysis.
- Expanded the core questions to two-paragraph, project-specific assessments where
  the available evidence supports that depth.
- Removed the low-value reflection tags such as `compound risk` and `unspecified`.
- Replaced `Source:` with `For further insights on why this matters, see:`.
- Kept the evidence disclosure in a separate evidence-basis panel.

### 3.3 Priority navigation and layout

- Replaced the narrow desktop sidebar treatment with a wider, readable layout.
- Stacked the detailed climate interaction panels vertically at desktop width.
- Added the visible instruction: `Explore all 3 priorities. Select each numbered
  priority below to see its evidence, rationale, and implementation options.`
- Fixed priority navigation so `Next` is disabled on Priority 3 and re-enabled after
  the reader returns to Priority 1 or 2.

### 3.4 Research recovery

- Added one narrow retry when the first live-research response is structurally usable
  but fails the evidence gate.
- Kept the maximum at two attempts and did not loosen source or claim quality rules.
- Added a truncation guard: an Anthropic response ending with `max_tokens` cannot be
  treated as eligible structured evidence for this retry path.
- Added diagnostic logging without logging source content or other sensitive payloads.

## 4. Automated verification

The final suite passed after independent review and the truncation-guard correction:

```text
634 passed in 81.13s
```

Coverage includes the HTML and DOCX readout contracts, prompt requirements, priority
navigation, climate research retry behavior, invalid/truncated response handling,
country-bank loading, and legacy FCV behavior.

## 5. Production acceptance test

### 5.1 Run identity

| Item | Result |
|---|---|
| Document | `Project Concept Note (PCN)_Draft_15_June 2026.docx` |
| Assessment ID | `22de81aa-3c0e-4542-9521-7e82ac2a6291` |
| Mode | Express with Climate-FCV Lens selected |
| HTTP result | `POST /api/run-express` returned `200` |
| Completion time | Approximately 10 minutes |
| Stage 2 result | Sensitivity: `Well Embedded`; Responsiveness: `Adequate` |
| Browser console | No warnings or errors |

### 5.2 Grounding evidence

Render recorded:

```text
bank_version=2026.07.south-sudan-pilot
iso3=SSD
selected_items=12
bank_chars=3698
grounding_state=bank-only
warning_code=climate_research_failed
```

This proves that the approved South Sudan bank was available to and used by the
production assessment. The user-facing evidence note correctly stated that reviewed
country evidence was used alongside the project documents and thematic sources.

### 5.3 Live-research outcome

- Attempt 1 returned structured JSON but no source passed normalization; the evidence
  gate rejected it.
- The new retry path activated.
- Attempt 2 returned three structurally valid sources and five claims, but the overall
  claim/source bundle still failed `climate_research_insufficient`.
- The system discarded the supplement and continued with the approved bank.

Do not weaken the evidence gate solely to turn this status green. The appropriate
next diagnostic is to expose or test the specific sub-reason for rejection (for
example, project-specific claim coverage or authoritative-source linkage) using a
captured synthetic fixture that contains no sensitive document content.

### 5.4 Output review

The production output passed the agreed checks:

- concise gauge label and explanatory subtitle;
- plain, coherent opening narrative with FCV, climate, compound-risk, and project
  scene setting;
- `Why it matters` integrated into that narrative;
- constructive executive-summary labels;
- both principal interactions rendered as three paragraphs and roughly 1,900
  characters each;
- five detailed core questions tied to named components, sites, and institutions;
- no reflection tags;
- revised further-reading phrasing;
- reviewed-country-evidence disclosure present;
- visible three-priority exploration instruction;
- all priority selectors operational;
- Next-button state correct after `3 -> 1` navigation;
- no CERC recommendation for social or political unrest. The output explicitly says
  its proposed adaptive protocol does not require a CERC;
- readable desktop widths at a 1280px viewport: core questions and interaction panels
  approximately 1,074px wide, priority card approximately 1,132px wide.

## 6. Substantive South Sudan output snapshot

The final note identifies three high-priority actions:

1. define compound flood-conflict triggers, remote TPMA protocols, and site-level
   stop/go provisions for Jonglei and Upper Nile;
2. screen BFMU and CWC boundary design for climate-driven resource mobility and
   extend the GRM to climate-triggered intercommunal resource disputes; and
3. define an adaptive protocol for Sub-component 1.4 in Ruweng State, including WFP
   and OCHA coordination alongside UNHCR.

The core analysis is anchored to the fisheries corridor, Boma-Badingilo landscape,
Imatong Valley forestry pilots, Ruweng State humanitarian-development activities,
BFMUs, CWCs, community forestry associations, TPMA, GRM, WHR financing, and the
specific preparation-stage decisions documented in the PCN.

## 7. Known limitations and risks

1. **Live research is not yet acceptance-proven.** Retry worked, but the second bundle
   still failed the evidence gate. Bank-only behavior is production-proven.
2. **Bank coverage is only acceptance-proven for South Sudan.** Other countries need
   approved releases and their own content review.
3. **Dual-build parity remains manual.** Mirror shared prompt, output-schema, rating,
   and research-contract changes to the internal Azure build using the private parity
   file.
4. **Model output remains non-deterministic.** The contracts and layout are tested,
   but later runs may phrase analysis differently. Continue expert review.
5. **Current-events claims require review.** The bank is approved, but recent conflict
   and climate developments should be periodically refreshed under the bank governance
   process.

## 8. Recommended next steps

1. Treat the current South Sudan output and layout as the acceptance baseline.
2. Diagnose the live-research evidence-gate sub-reason without weakening source or
   claim requirements; add a regression fixture for the actual rejection shape.
3. Run one later South Sudan `bank+research` acceptance test after that diagnostic.
4. Mirror the shared-contract changes to the internal Azure build and record the
   parity result in the private file.
5. When ready to expand, select one additional country, build and approve its evidence
   package, then repeat the content and production acceptance checklist.
6. Keep PR #59 in draft until the internal-build parity decision and final merge-base
   strategy are confirmed.

## 9. Restart commands

```powershell
Set-Location 'C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\climate-country-bank'
git status --short --branch
git log -5 --oneline --decorate
python -m pytest -q
```

Useful production references:

```text
Service:       https://fcv-agent.onrender.com
Render logs:   https://dashboard.render.com/web/srv-d6de99jh46gs73d0jjrg/logs?t=app&r=live
Assessment:    22de81aa-3c0e-4542-9521-7e82ac2a6291
Validated SHA: fdb9c19868e8
```

## 10. Suggested opening prompt for the next session

> Read `docs/20260731_climate_fcv_final_handover.md` and the earlier architecture
> handover it references. Continue from the clean `feat/climate-country-bank`
> worktree. Treat the South Sudan bank-only production output as the accepted content
> and UI baseline. First diagnose why the second live-research bundle had three valid
> sources and five claims but still failed `climate_research_insufficient`, without
> weakening the evidence gate or exposing sensitive PCN content. Then propose the
> smallest tested change, if any, and preserve dual-build parity.
