# Climate Country-Bank Preview Rollout Handover

**Date:** 2026-08-13

**Branch:** `codex/climate-summary-quality-fixes`

**Application commit:** `828b0df01a338cd1fc88514f78f88d838be345d7`

**Bank gitlink:** `12a804fe92bacfdaf0bec7926725d8a7a9376fe4`

## Final service state

| Service | Render ID | URL | Final mode | Candidate bank |
|---|---|---|---|---|
| Existing smoke | `srv-d6gsivcr85hc73a2833g` | https://fcv-agent-1.onrender.com | `smoke` | enabled |
| Dedicated preview | `srv-d9usolvqj5pc738duvd0` | https://fcv-agent-climate-preview.onrender.com | `smoke` | enabled |
| Production | `srv-d6de99jh46gs73d0jjrg` | https://fcv-agent.onrender.com | unchanged | approved runtime only |

Both non-production services deploy the feature branch with `python
render_build.py` and use:

```text
CLIMATE_COUNTRY_BANK_PATH=data/climate-fcv-country-bank/releases/candidates/2026.08/runtime.json
CLIMATE_COUNTRY_BANK_PREVIEW=reviewed-candidate
CLIMATE_VERIFIED_RUN_MODE=smoke
```

The dedicated service is a Free Render service in the existing Production
environment. Its final health response reported build `828b0df01a33`,
`climate_verified_run_mode: smoke`, and `status: ok`.

Production was not edited or redeployed. Its branch remains `main`, its deployed
commit remains `79f0c164954bdeb575c27a5a8136d79a9a7490a4`, it has no candidate-bank
environment variables, and its final `/health` response remained `{"status":"ok"}`.

## Candidate runtime validation

Runtime:
`data/climate-fcv-country-bank/releases/candidates/2026.08/runtime.json`

- schema: `1.1.0`
- content version: `2026.08.multi-country-preview`
- candidate: `true`
- countries: 24
- sources: 291
- evidence records: 565
- pathways: 178

The actual application loader resolved every package by country name and ISO3.
A new regression also selects and materializes all 24 country packages. This
exposed and fixed a release-wide URL-uniqueness check: the same public source may
appear in different countries, while normalized duplicate URLs within one
country remain invalid.

## Verification evidence

- 36 initial targeted application bank/selector/deployment/frontend tests passed.
- 95 companion-bank release tests passed.
- Candidate schema/count validation passed with the exact `24/291/565/178`
  counts above.
- All 24 packages resolved through the actual application loader by name and
  ISO3.
- The all-24 materialization regression and the existing within-country
  duplicate rejection test passed together during red-green verification.
- Final HTML/DOCX render suite: `104 passed, 1 deselected` (the deselected test
  requires a Chromium subprocess unavailable under the Windows sandbox).
- Broader pytest attempts remained constrained by the previously documented
  Windows/OneDrive `tmp_path` permission failures. No application assertion
  failed in the final render suite.

## Live smoke evidence

### Existing smoke service

The authentic South Sudan PCN dated 15 June 2026 completed in Express smoke
mode. Render recorded:

```text
assessment_id=91bc8170-8bec-4bc7-8c82-92770c38971b
bank_version=2026.08.multi-country-preview
iso3=SSD selected_items=12 bank_chars=3727
research_status=accepted grounding_state=bank+research warning_code=none
```

This corrected an earlier pre-fix run that had degraded with
`bank_manifest_invalid`.

### Dedicated preview service

The same authentic PCN completed in Express smoke mode. Render recorded:

```text
assessment_id=961e4897-7254-42f7-852b-1363a01701a2
bank_version=2026.08.multi-country-preview
iso3=SSD selected_items=12 bank_chars=3727
research_status=accepted grounding_state=bank+research warning_code=none
```

The Detailed analysis visibly showed both safeguards:

```text
Smoke test: validates workflow completion only; not a quality benchmark.
Candidate country evidence: preview; not approved.
```

The browser security boundary denied automated export downloads. Export-label
parity was therefore verified through the shared HTML/DOCX renderer tests rather
than by retaining downloaded artifacts.

## Bounded quality sample

Only the dedicated preview service was temporarily switched to `quality`. One
South Sudan run used the same authentic PCN and completed in about ten minutes.

The rendered assessment was internally coherent at a review level:

- rating: Moderate;
- seven project-specific climate-FCV questions;
- four ranked operational priorities;
- document checks and watch items remained separately presented;
- `Candidate country evidence: preview; not approved.` was visible; and
- the smoke warning was absent.

The quality-run grounding log recorded the same candidate release, `iso3=SSD`,
and 12 selected bank items, but live research failed and the application safely
degraded to `bank-only`:

```text
assessment_id=961e4897-7254-42f7-852b-1363a01701a2
bank_version=2026.08.multi-country-preview
iso3=SSD selected_items=12 bank_chars=3727
research_status=empty grounding_state=bank-only
warning_code=climate_research_failed
```

No second quality run was performed. The user requested a bounded one-or-two
sample, and the completed run established candidate-bank grounding and render
behavior; repeating it solely to obtain successful optional live research would
not add country-bank coverage.

After the sample, the dedicated service was restored to `smoke` and its health
endpoint confirmed the restored mode.

## Approval and use boundary

All 24 packages are usable for controlled preview runs through either
non-production service. They remain reviewed candidates, not approved country
content. The production `releases/current/runtime.json` remains the approved
South Sudan-only release. Substantive country review and the companion-bank
promotion workflow are still required before any production promotion.
