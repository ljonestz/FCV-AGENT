# ITS Handover: Normal FCV Five-Minute Summary

**Date:** 2026-08-22
**Application branch:** `codex/climate-summary-quality-fixes`
**Application commit:** `012eaa2`
**Status:** Implemented, pushed, deployed to Smoke and Preview, and live-validated

## Purpose and delivered behavior

The normal FCV route now presents Stage 3 through a concise-first Summary in the
same broad interaction style as the verified Climate + FCV reader. The Summary is
an optional presentation layer over the existing Recommendations Note. It does not
replace the detailed analysis, change ratings, reorder priorities, or enter report
downloads.

- Complete normal FCV design and implementation reviews open on **Summary**.
- **Detailed analysis** remains available beside it.
- Summary contains a one-sentence judgment, a 150-200 word overall assessment, both
  existing FCV ratings, and exactly three grounded strengths.
- Every ranked priority appears. Priority 1 opens initially; opening another card
  closes the previous one.
- The selected priority is retained when switching tabs.
- Both normal and Climate + FCV summaries show the deterministic non-mandatory
  advisory and specialist-consultation wording.
- HTML and DOCX downloads remain detailed-only.

## Shared contract for ITS parity

The shared Stage 3 JSON surface adds optional top-level `concise_readout` and
per-priority `concise` fields. ITS should mirror these rules:

1. Apply the concise contract only to the normal core FCV route, not active lenses.
2. Emit the Stage 3 JSON before the detailed narrative; parsing must not assume a
   trailing block.
3. Validate atomically. The readout and every priority concise object must be
   complete; otherwise discard all concise data but retain the detailed result.
4. Do not make a second model call to repair Summary.
5. Transport the normalized optional bundle through both workflow variants.
6. Persist concise readout, priorities, and ratings together for restoration.
7. Keep ITS-specific OPCS retrieval and FastAPI infrastructure unchanged.

The private parity register at `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md` is
updated and intentionally remains outside this public repository.

## Live acceptance

Both services used the official World Bank concept-stage PID for Somalia STAIRP
Phase 1 (P513127), prepared 7 February 2026 as IPF within an MPA. A repository copy
and provenance record now live under `test_documents/live_acceptance/`.

Services and accepted assessment IDs:

- Smoke: `https://fcv-agent-1.onrender.com`, assessment
  `1504cc34-d36c-4f23-afa9-00f0d4f92f98`
- Preview quality: `https://fcv-agent-climate-preview.onrender.com`, assessment
  `f22abd6b-f789-4eab-b7ce-306ad2de5682`

Smoke and quality both opened Summary by default, rendered three strengths and five
complete concise priorities, and began with only Priority 1 open. The quality run
also verified single-open behavior, tab state preservation, exact advisory text,
and detailed-only HTML/DOCX exports. All three stage requests returned HTTP 200 in
both runs, with no error-level Render log entries.

The quality run's overall assessment was 187 words. One content caveat was recorded:
Priority 4 repeated a dated Puntland-FGS assertion from live research that the
uploaded PID did not substantiate. Verify it before external use. This is a content
QA finding, not a Summary contract or rendering failure.

## Evidence artifacts

Saved outside the repository under:
`C:\Users\wb559324\.codex\visualizations\2026\08\21\01a0230a-b7a7-7de0-8076-403fbe8c4bd7`

- `20260822_smoke-summary-readout.png`
- `20260822_quality-summary-readout.png`
- `20260822_quality-detailed-browser.html`
- `20260822_quality-detailed-export.html`
- `20260822_quality-detailed-export.docx`
- `20260822_smoke-stage-responses-core-schema.txt`
- `20260822_quality-stage-responses-core-schema.txt`

## Verification and operational lessons

- Focused concise/parser plus bank cases: `98 passed`.
- Full suite after submodule initialization: `1012 passed`.
- `python -m py_compile app.py` and `git diff --check`: passed.
- Luna xhigh review: no remaining actionable implementation issue.
- Keep a second service page active during multi-minute browser work; these preview
  services were observed heading toward dormancy after about eight idle minutes.
- Wait for stable upload controls after cold start before treating a first navigation
  miss as an application defect.
- Correlate all live issues by assessment ID before changing code or timeouts.
- Keep JSON first and avoid silent post-stream model work.

## Branch disposition

Keep `codex/climate-summary-quality-fixes` and its isolated worktree as-is. The
branch is pushed and is not merged into `main`.
