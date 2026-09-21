# Climate and Normal-FCV Production Validation

**Validated:** 2026-08-25
**Status:** Release candidate accepted on its feature branch and deployed to both test services.
**Integration decision:** Keep the branch separate from `main` until the maintainer chooses to merge it.

## Release state

- Repository: `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT`
- Worktree: `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\climate-summary-direct`
- Branch: `codex/climate-summary-quality-fixes`
- Accepted application head: `789825dea02bd2a92a435d26061d40c146bd37e0`
- Documentation closeout: committed after the accepted application head; the deployed services remain on `789825d`
- `main`: unchanged; no merge or cleanup was performed

The branch is a production-ready release candidate for the validated Climate and normal-FCV paths. It is not yet a `main` release. Model-generated analytical judgments remain advisory and require expert review.

## Implemented outcome

The work completed the approved production-alignment design:

1. One recursive OOXML walker now preserves visible paragraph, table, nested-table, and structured-document-tag order for both application paths. It retains checked controls, suppresses unchecked choices, and carries structured label/value fields separately from reader text.
2. Structured financing metadata takes precedence over prose heuristics. Conflicting or explicitly empty structured values fail closed, and an E&S risk value such as `Substantial` cannot by itself establish the ESF route.
3. Verified Climate uses source manifest `source-blocks-v3` and judgment contract `climate-judgments-v2.4`. The existing judgment call now returns the two-to-three-paragraph `summary_overview.paragraphs` synthesis without adding a model call.
4. Climate Summary and Detailed share the same gated drafting content. Summary uses the dedicated synthesis and closed watch/guidance disclosures; Detailed retains the comprehensive reader and purpose-led follow-up bands.
5. Normal FCV retains its prompt, schema, ratings, headline, overview, priorities, and per-priority guidance contract. It adds only a conditional closed watch-items disclosure sourced from existing normalized arrays.
6. Result tabs, result actions, and session controls now wrap correctly on narrow phones.

Maintained architecture documentation was updated in `CLAUDE.md` and the four relevant files under `docs/reference/` in commit `9d7fc20`. The private dual-build parity log was also updated without copying private content into the repository.

## Verification evidence

Fresh verification at the accepted branch head produced:

| Check | Result |
|---|---:|
| Focused narrow-phone contracts | 3 passed |
| Frontend contract suite | 86 passed in 56.39s |
| Full repository suite | 1,217 passed in 79.12s |
| Tracked worktree state after commit | Clean |
| Remote branch parity before docs closeout | Local and remote both `789825d` |

The pre-existing untracked `.pytest_tmp_*` directories remain untouched.

## Real-PCN extraction acceptance

The South Sudan PCN fixture was processed through the shared extraction path:

`C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.superpowers\brainstorm\Southsudan\Project Concept Note (PCN)_Draft_15_June 2026.docx`

Required structured values were preserved:

- `Operation ID: P511185`
- `Financing Instrument: Investment Project Financing (IPF)`
- `Environmental and Social Risk Classification: Substantial`
- resolved instrument: `IPF`
- MPA selection: false

This closes the real-template header-row/value-row defect recorded in the 2026-08-23 pause handover.

## Deployed acceptance

Both Render services were deployed from exact commit `789825d`:

| Path | Service | URL |
|---|---|---|
| Normal FCV | `srv-d6gsivcr85hc73a2833g` | `https://fcv-agent-1.onrender.com/` |
| Climate preview | `srv-d9usolvqj5pc738duvd0` | `https://fcv-agent-climate-preview.onrender.com/` |

The services are in Render workspace `tea-d6de2tsr85hc73bqdi0g`. Post-deployment 320 px and 390 px checks confirmed that session controls no longer cause horizontal overflow, and no error-level service logs were observed after deployment.

## Climate quality artifacts

The saved Climate artifacts demonstrate the completed detailed reader, watch and guidance disclosures, suggested drafting, and export parity. They are indexed in the visualization folder alongside this run's screenshots:

`C:\Users\wb559324\.codex\visualizations\2026\08\23\01a02f3c-9662-76b2-b9ce-4ee10d271bd2`

Primary files:

- `20260824_climate-fcv-smoke-export.html`
- `20260824_climate-fcv-smoke-export.docx`
- `20260824_climate-export-phone-closed.png`
- `20260824_climate-export-laptop-closed.png`
- `20260824_climate-export-wide-closed.png`
- `20260824_climate-export-wide-guidance-open.png`
- `20260824_climate-export-wide-method-open.png`
- `20260824_climate-quality-export.html`
- `20260824_climate-quality-export.docx`
- `20260824_climate-quality-evidence.json`

The standalone reader includes three ranked priorities, their suggested drafting, project-cycle placement, points to check, watch items, relevant WBG guidance, and methodology/source material. The first smoke export carries the expected P511185/IPF routing evidence.

The later `climate-quality-evidence.json` is retained as diagnostic evidence, not a clean pass certificate: its live Summary projection reported zero priority cards and phone overflow before the final mobile wrapping fixes. The comprehensive standalone export remained populated. Subsequent deployed 320 px and 390 px checks verified the mobile overflow repair.

## Normal-FCV quality run

The final normal-FCV run used the same South Sudan PCN with no sector lens selected and completed in 994.9 seconds. It produced:

- FCV sensitivity: `Adequate`
- FCV responsiveness: `Low`
- five ranked operational priorities
- populated Summary and Detailed views
- standalone HTML and DOCX exports
- no forbidden internal tokens or browser page errors

The executive headline was:

> A well-conceived community-based design is operating in a conflict environment deteriorating faster than its risk framing reflects, with its adaptive management architecture - the most critical FCV gap - yet to be built.

Primary files use the prefix `20260824_normal-fcv-final-quality-04` in the same visualization folder:

- `summary-render.html` and Summary phone/laptop/wide screenshots
- `detailed-render.html` and Detailed phone/laptop/wide screenshots
- `export.html` and `export.docx`
- `evidence.json` and `final-state.png`

Structural validation found no forbidden tokens in any saved HTML. The Summary rendering was 174,735 bytes, Detailed was 177,912 bytes, and the self-contained export was 222,623 bytes. The DOCX was 51,015 bytes with 161 non-empty paragraphs, one table, and one section.

The evidence harness records `AssertionError()` because the optional Summary watch disclosure was absent for this run; the model returned no applicable horizon considerations, so omission is the intended conditional behavior. Its `net::ERR_ABORTED` request record followed deliberate frontend stream cancellation after `express_done`, not a failed assessment.

## Acceptance boundaries and remaining observations

- The application paths, contracts, exports, responsive layout, and deployments passed acceptance on this branch.
- Normal-FCV analytical outputs are not deterministic. Repeated runs varied the responsiveness rating between `Adequate` and `Low`; one earlier run had a transient upstream network error, and another did not expose Summary tabs after all stages. The final recorded run completed with both views. This variability is a model-quality monitoring issue, not evidence of a deterministic application-contract failure.
- Long real assessments can take roughly 15-17 minutes. Browser-based monitoring should retain the established refresh/keepalive discipline when using Render test services.
- Local image inspection through the sandbox helper was blocked by Windows Application Control (`WinError 4551`). Playwright still produced the screenshots, and the HTML/DOCX artifacts were structurally validated.
- The saved normal-FCV screenshots predate the final session-bar wrapping commit and therefore retain the old 390 px top-bar overflow. The deployed post-fix checks are the authoritative mobile-layout result.

## Branch handoff

Keep `codex/climate-summary-quality-fixes` and its worktree intact. Do not merge, delete the branch, or remove the worktree as part of this validation closeout. When integration is approved, review the branch against the intended base and use the normal merge/PR workflow; the evidence above should travel with that decision.
