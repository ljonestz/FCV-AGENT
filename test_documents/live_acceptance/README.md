# Standard Live-Acceptance Documents

This folder contains small, public World Bank documents retained as stable manual
browser checks. They are not used by the unit-test suite and must not be parsed or
asserted against during ordinary CI.

## Somalia STAIRP Phase 1 concept-stage PID

**File:** `somalia-stairp-p513127-concept-pid-20260207.pdf`
**Project:** Somalia Transformational Access and Infrastructure Resilience Program,
Phase 1 (STAIRP), P513127
**Prepared:** 7 February 2026
**Financing:** Investment Project Financing within an MPA
**Public source:**
`https://documents1.worldbank.org/curated/en/099020726020018361/pdf/P513127-1143db4f-6238-4203-90cb-1a0736667907.pdf`
**Size:** 316,056 bytes
**SHA-256:** `61E3EE924D114DDBDF19DD6835D2CB051A852F8A1FCD8810B3E8B77B2DE994E1`

Use this document for the normal FCV live acceptance path:

1. Initialize the repository submodule and run local tests first.
2. Wake the target Render service and confirm it serves the expected branch commit.
3. Keep a separate service page active during the run so the preview service does
   not return to dormancy during a long browser interaction.
4. Upload the complete PDF and run Step-by-Step Stage 1 through Stage 3.
5. On Smoke, verify orchestration and Summary completeness.
6. On Preview/quality, verify analytical quality, Summary/Detailed interaction,
   detailed-only HTML/DOCX exports, and source grounding.
7. Capture the Summary screenshot, Detailed browser HTML, downloaded detailed HTML,
   raw stage responses, and the assessment ID used to filter Render logs.

This is a public test document, not an approved analytical answer key. Project facts
may be used to check grounding, but current contextual claims from live research
must still be independently verified before sharing an assessment.
