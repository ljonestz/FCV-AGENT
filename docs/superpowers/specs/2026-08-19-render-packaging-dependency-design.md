# Render Packaging Dependency Design

## Problem

Render checked out and built commit `c6aa04c7936785268877936955c6bd69bbd1fb36`, but the new instance failed before the application started. Gunicorn's gevent worker imported `packaging.version`, while the clean Render environment did not contain the `packaging` distribution. Render retained the previous live deploy at `7c7f1b8087bceb8ce434800da227ef49b8c942f8`.

## Selected approach

Declare `packaging` as an explicit runtime dependency in `requirements.txt`. This keeps the fix version-controlled and reproducible across clean Render builds, rather than adding an untracked service-specific build-command workaround.

## Scope

- Add a deployment-contract test that parses `requirements.txt` and requires an explicit `packaging` declaration.
- Observe that test fail on the current target commit.
- Add the narrowest compatible `packaging` requirement needed by Gunicorn's gevent worker.
- Run the targeted test and the complete test suite.
- Commit and push the fix branch, open a pull request into `codex/climate-summary-quality-fixes`, and merge it after checks pass.
- Monitor Render until the resulting deploy is `live` and confirm its commit descends from `c6aa04c`.
- Repeat the supplied PCN Stage 1 workflow in Step-by-Step mode with the Climate-FCV lens, capturing the assessment ID, terminal SSE event, browser console, and matching Render logs.

## Files

- Modify `requirements.txt` to declare the missing runtime dependency.
- Add one focused test under `tests/` for the Render dependency contract.

No application logic, prompts, frontend code, Render service configuration, or climate-bank data will change.

## Error handling and verification

The regression test checks the deployment input rather than the developer environment, so it will fail whenever a future edit removes the explicit dependency even if `packaging` happens to be installed transitively locally. Live verification requires both a successful Render startup and an error-free Stage 1 `done` event; a successful HTTP 200 alone is insufficient because the endpoint streams terminal errors over SSE.

## Rollback

If the new dependency causes an unexpected deployment problem, revert the dependency commit on the preview branch. Render will retain the prior live deploy until a replacement starts successfully.
