# Climate Country-Bank Preview Deployment Design

**Date:** 2026-08-13

**Branch:** `codex/climate-summary-quality-fixes`

**Application commit:** `dd7e3d8`

**Candidate runtime:** `data/climate-fcv-country-bank/releases/candidates/2026.08/runtime.json`

## Objective

Make all 24 reviewed candidate country packages usable in controlled Render
preview environments without changing the approved production runtime or
implying substantive country approval.

## Scope

The rollout has two stages:

1. Enable and validate the candidate runtime on the existing Render smoke
   service.
2. Create an isolated Render preview service that also defaults to the smoke
   model profile.

After smoke validation, run one or two representative end-to-end assessments
with the quality profile on the dedicated preview service. Return that service
to the smoke profile after the checks.

Production promotion, country approval decisions, and changes to
`releases/current/runtime.json` are out of scope.

## Deployment Architecture

The production service continues to use the default approved runtime and must
not receive either candidate-preview environment variable.

The existing smoke service and the dedicated preview service use:

```text
CLIMATE_COUNTRY_BANK_PATH=data/climate-fcv-country-bank/releases/candidates/2026.08/runtime.json
CLIMATE_COUNTRY_BANK_PREVIEW=reviewed-candidate
CLIMATE_VERIFIED_RUN_MODE=smoke
```

Both preview services deploy `codex/climate-summary-quality-fixes` at
`dd7e3d8` or a later commit containing the same candidate-bank and summary
quality changes. The pinned companion-bank submodule must resolve to commit
`12a804f` and be initialized during the Render build.

For the final quality sample, change only the dedicated preview service's
`CLIMATE_VERIFIED_RUN_MODE` from `smoke` to `quality`, run the selected
assessments, and restore it to `smoke` afterward. The country-bank path and
preview token remain unchanged.

## Rollout and Data Flow

On service startup, the application resolves the explicit candidate runtime,
checks schema compatibility and the source-manifest checksum, and accepts the
schema-1.1 candidate only when the exact preview token is present. Country
selection then resolves project country names or aliases against the 24-country
release. Any missing, invalid, incompatible, or stale bank content degrades to
the existing live-research or thematic fallback rather than terminating an
assessment.

The rollout order is:

1. Record the existing smoke-service branch and relevant environment values.
2. Set the candidate path and preview token on the smoke service, retaining
   `CLIMATE_VERIFIED_RUN_MODE=smoke`.
3. Deploy and validate the smoke service.
4. Create the dedicated preview service from the same repository and branch,
   with the same build/start configuration and the three environment values
   above.
5. Deploy and validate the dedicated preview service.
6. Run one or two representative quality-profile assessments on the dedicated
   preview service, then restore its smoke profile.

## Safeguards and Failure Handling

- Do not change the production service's bank path, preview token, or approved
  runtime.
- Do not copy the candidate runtime into `releases/current` or invoke the bank
  promotion workflow.
- Preview output must remain visibly labelled `preview; not approved` in the
  browser and generated exports.
- Smoke output must retain its smoke-profile label.
- If Render does not initialize the submodule at `12a804f`, stop acceptance
  testing and fix the build before exercising assessments.
- If the loader reports anything other than a valid 24-country candidate
  release, restore the service's prior environment values and redeploy.
- If quality testing exposes an application defect, return the dedicated
  preview service to smoke mode and address the defect on the feature branch;
  do not alter production as a workaround.

## Verification and Acceptance Criteria

Before changing Render, rerun the smallest relevant local checks on the current
branch: candidate loader tests, selector/deployment-contract tests, frontend
preview-labelling tests, and candidate-bank release validation. Use a temporary
directory outside the OneDrive worktree for pytest if necessary.

The smoke service is accepted when:

- the build initializes the expected submodule commit;
- startup or diagnostic output identifies the candidate content version and 24
  available countries;
- every country resolves through a low-cost smoke check without a bank-loader
  error;
- representative browser and export output shows both preview and smoke
  labelling; and
- the production service remains unchanged.

The dedicated preview service is accepted when:

- it meets the same loader and labelling checks;
- all 24 countries are available under the smoke profile;
- one or two representative assessments complete under the quality profile
  with country-bank grounding and preview labelling; and
- it is returned to `CLIMATE_VERIFIED_RUN_MODE=smoke` after quality acceptance.

The final handover records service URLs, deployed commit, bank content version,
the quality-sample countries, checks performed, outcomes, and any unresolved
country-content caveats. No result from this rollout changes a candidate's
substantive approval status.
