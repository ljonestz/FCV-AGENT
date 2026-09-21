# Strengths and gaps bullet formatting

## Strengths and gaps readability (2026-09-21)

Summary Potential gaps now uses one bullet per existing priority gap. Summary
strength cards are unchanged. Detailed Strengths and Gaps headings render each
existing prose paragraph as a bullet, retaining the complete explanation and
inline emphasis. Existing lists and other narrative sections remain unchanged.
The change is presentation-only: saved sessions receive the same formatting,
without rewriting stored text or changing prompts, ratings, schemas or model calls.

`bulletFindingSections()` in `index.html` and `bullet_finding_sections()` in
`fcv_presentation.py` apply the same paragraph boundaries to the browser,
detailed HTML and detailed Word export. Brief HTML gaps also use list items;
brief Word gaps already use Word's List Bullet style.

## Verification

- Focused contracts: 106 passed.
- Python/JavaScript parity, wording preservation and idempotency checks passed.
- Saved Honduras assessment: Summary gaps and Detailed strengths/gaps displayed as bullets; exact rendered text preserved; all priority links, four exports, session save/reload and mobile layout passed. Full DOCX contains four Strengths list paragraphs and one Gaps list paragraph, matching the source paragraph boundaries.
- Independent read-only review: no blocking findings.
- Broad-suite assertion for the detailed HTML export updated for the new formatting helper.
- One fresh public Somalia concept-PID assessment completed all three stages with four priorities. Candidate browser formatting and local candidate exporters passed all links, four downloads, save/reload, mobile and no-browser-error checks. Assessment ID: `596975c6-c115-4268-a1d8-0b9bfca575df`.
- The live model call used unchanged production analysis at `8599ffbae3f8`; candidate HTML was loaded in the test browser and export requests were handled by the local candidate. No second model run was made. This is formatting/pipeline acceptance, not a new factual audit of the generated analysis.
- Full regression result: pending durable log after a tool-session reset.
- Private evidence: `app_feedback/20260921_bullets/` (gitignored).
