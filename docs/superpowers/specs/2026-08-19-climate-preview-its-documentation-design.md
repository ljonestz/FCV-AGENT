# Climate Preview ITS Documentation Refresh Design

**Date:** 2026-08-19  
**Base:** `origin/codex/climate-summary-quality-fixes` at deployed commit `08b3cb99`  
**Scope:** Documentation only

## Objective

Bring the repository's current canonical documentation into line with the
deployed Climate preview, and provide ITS with one concise, shareable Markdown
handover covering the issue they originally reported, the repair, and the final
verification evidence.

## Documentation boundary

Update only current canonical documentation:

- `README.md`
- `claude.md`
- relevant files under `docs/reference/`
- the documentation index/link surface
- a new dated ITS handover

Older dated handovers, design specifications, and implementation plans remain
unchanged because they are historical records of earlier states.

## Content model

The canonical documentation will consistently state that:

1. the Climate-FCV module is experimental/pilot and its outputs require expert
   review;
2. the controlled preview uses the 24-country reviewed-candidate bank covering
   the current FCV/FCS set represented by the release;
3. the module can run for countries outside that bank, but it then relies on
   live research and/or thematic guidance and has less country-specific prior
   knowledge;
4. candidate-bank content is preview material and is not approved production
   content;
5. the Render deployment requires the explicit `packaging` dependency for the
   Gunicorn gevent worker; and
6. Stage 1 must initialize lens context before any branch can read it.

The landing-page `Experimental` or `Pilot` signpost will be recorded as a
recommended product decision, not implemented as part of this documentation-only
change.

## ITS handover structure

Create `20260819_its-climate-preview-handover.md` with:

- current service, branch, deploy, and bank-release state;
- the original ITS-reported `lens_context` failure shown in the supplied
  screenshot;
- root cause and the two fixes (`c6aa04c` and `08b3cb99`);
- automated verification (`966 passed`);
- a complete Step-by-Step live run through Stages 1-3, including the shared
  assessment ID and clean browser/Render evidence;
- the Climate pilot and country-coverage limitations;
- actions and parity considerations for ITS; and
- a short informal Teams message.

The handover supersedes the operational status of
`20260814_its-production-readiness-handover.md` but does not replace its detailed
recommendation-routing history.

## Verification

Because this is documentation-only work, acceptance consists of:

- Markdown and relative-link checks;
- consistency scans for commit IDs, service IDs, country counts, release labels,
  and pilot terminology;
- `git diff --check`;
- confirmation that no runtime files changed; and
- the full repository suite if documentation changes touch any test-inspected
  contract text.

## Non-goals

- No application, prompt, schema, route, or UI behavior changes.
- No candidate-bank promotion or content approval.
- No edits to historical records.
- No changes to the private dual-build parity file unless a shared runtime
  contract changes; this task changes documentation only.
