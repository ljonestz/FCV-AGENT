# Standard FCV Screener: production readiness recheck

Date: 25 September 2026

**Decision: GO for the stated, supervised first-pass use on the paid, always-on host.** The application is broadly functional in the tested standard-FCV workflows. Its outputs still require an FCV/ESF specialist or task team to verify project facts, source use, and proposed commitments before operational use. This is a release decision for an expert-reviewed analytical aid, not an assertion that every generated claim is source-verified. The prior [24 September hold](20260924_standard-fcv-evidence-review-qa.md) remains relevant to any use that would treat generated text as authoritative without that check.

## Method and scope

I used the paid [Render Preview](https://fcv-agent-climate-preview.onrender.com/) host because the free production host can sleep during a long run. Public Somalia concept-PID and Honduras PAD/ESCP examples tested distinct workflow paths; Honduras was an adversarial source-check case, not the target product domain. Live runs checked stage completion, structured output, reviewer edits, ratings, parse status, and suppression of unreviewed streaming text. Browser checks covered saved-session restoration, Summary/Detailed presentation, copy and downloads, and a narrow mobile-width check. I compared the Honduras findings against the source audit in the earlier QA record. No restricted OPCS/ESF corpus was uploaded.

The application code verified on paid Preview was `eff819bf4fe74626ac208b6cd21a1be782246678` (`dep-daqsq6avcj2c739q2r2g`); later documentation-only commits do not change that code. The last end-to-end core generation preceded that commit: subsequent changes were confined to the Playbook prompt and session/summary presentation, with separate live checks of each.

## Evidence

| Check | Result |
|---|---|
| Somalia Express and normal Step workflows | Fresh three-stage runs completed on earlier candidate SHAs. The fixed FCV rating enums survived reviewer edits; no raw draft SSE or parse error appeared. Somalia content was a workflow and contract check, not an independent analytical sign-off. |
| Honduras PAD + ESCP normal Step | The initial fresh run exposed a Stage 3 reviewer edit conflict. After the indexed-review fix, Stages 2 and 3 completed from its saved normal Stage 1 history on `8487d51`: seven and eleven reviewer issues, four priorities, `Adequate`/`Adequate` ratings, no parse error or draft SSE. |
| Source/status checks | Later output no longer states that the Security Management Plan is unprepared; HEIS approval is distinguished from unverified activation, and regional crime reporting is qualified as context rather than site evidence in reviewed passages. Past design gates are conditionalized and the review date is passed into the reviewer. |
| Playbook follow-up | The deployed default prompt on `f774b9c` returned a completed security-priority response without recommending CERC for violence alone or repeating the disputed department claim. One successful follow-up is a targeted check, not a guarantee across all priorities. |
| Browser and exports | The core saved session passed Summary/Detailed, copy, brief/full HTML and Word, save/load, and 390-pixel checks. On final `eff819b`, a historical PAD session showed its retrospective notice in Summary; its saved JSON retained `approval_date: 2024-12`, the full HTML contained the notice, and reset cleared the date. The browser assertions and artifacts passed; Playwright stalled during shutdown after printing the pass result and was stopped. |
| Automated suite | **1,377 tests passed** on final `eff819b` (`python -m pytest -q -p no:cacheprovider --basetemp=... tests`). Pytest needed filesystem access to its temporary directories on this Windows runner; the first sandboxed attempts failed at test setup, not in application code. |

The ignored `app_feedback/20260923_readiness_qa/` directory contains the live events, reviewed outputs, saved sessions, and downloaded artifacts. It is not part of the PR.

## Residual analytical limitation

The reviewer still missed some related instances of a project-location error. It corrected several unsupported references to Ocotepeque as a Honduras project-corridor department, yet the final Stage 3 result retained one unqualified reference and priority fields retained further references, including possible monitoring boundaries. This is a **general source-consistency failure mode**: correcting one occurrence does not establish that every variant in narrative, indicators, and suggested text is grounded. Similar errors could misdirect operational work if copied without review. The generated first-pass disclaimer and expert verification are therefore part of the supported use, especially for named sites, risk incidents, instrument status, timing, and proposed ESCP or Operations Manual language.

This test set is deliberately small and does not establish accuracy rates across countries, instruments, or sector lenses. The full project documents and current implementation status were not independently verified for every statement. No automatic source-review gate can be claimed to catch all consequential errors.

## Release boundary

The paid Preview host is the validated run environment. The free production host's idle sleep makes it unsuitable for uninterrupted assessments unless it is separately kept awake. Production Render and the internal ITS build were not changed. Draft [PR #73](https://github.com/ljonestz/FCV-AGENT/pull/73) remains stacked on draft PR #72; merge and production promotion still need an explicit release decision. For this release, present the tool as an LLM-assisted first pass and require expert checking of project-specific assertions and operational text before adoption.
