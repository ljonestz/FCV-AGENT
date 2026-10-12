# Climate OPCS parity validation - 12 October 2026

Base: main `1168a8f`. Candidate branch: `fix/climate-opcs-parity`.

## Scope and method

Verified Climate context, guidance, prompts, recommendation validation and shared
reader. No standard-route changes. The maintainer authorized local OPCS source
access for this session. Policy sources were read locally; no source PDFs or raw
internal text are included in the repository.

## Policy basis

- IPF and PforR One-step / Two-step Preparation procedures (April 2026), Section I:
  OIS boundaries, risk rules, AF, MPA, FMRF and hybrid component distinctions.
- DPF Procedure (May 2026), Section I and processing tables: April 18 boundary,
  Program Document and instrument-specific processing.
- Environmental and Social Directive/Procedure for IPF (January 2026), scope and
  Annex III: ESF trigger, exceptions and PforR IPF-component E&S instruments.
- Multiphase Programmatic Approach Guidance (November 2021 revision), page 4:
  DPF cannot finance an MPA.
- Preparation of IPF Guidance (June 2026), page 15: climate co-benefits and the
  climate-indicator check when the evidenced share is at least 20%.
- Preparing the IPF Project Paper (July 2026), page 11, and PforR Program Paper
  (June 2026), page 13: Paris Alignment and climate appraisal evidence.

The curated October index warns that it lags the live PPF library. These changes
are grounded in inspected local documents, not certification of all latest policy
revisions. OIS-as-Concept-Decision wording and the exact April 17 boundary retain
the existing Help Desk caveats. TA applicability and guarantee routing remain
outside resolved coverage; no automatic TA-to-IPF conversion was added.

## Verification

- Original audit: 264 existing tests passed; additional probes exposed gaps.
- New regressions initially reproduced 16 failures (2 cases already passed).
- Focused candidate tests: 227 passed before final MPA/FMRF and E&S hardening.
- Full suite: in progress.
- Live smoke and quality: pending. Only `fcv-agent-climate-smoke`, service
  `srv-d6gsivcr85hc73a2833g`, URL `https://fcv-agent-1.onrender.com`, is authorized
  for these checks. Its initial branch was `release/fy26-app-updates`; Edge
  dashboard authentication is pending.
- Production and ITS have not been deployed or modified.

## Shared-build implications

Mirror verified Climate resolver, registry, prompt, hybrid validator and reader
changes together only after acceptance. Preserve ITS retrieval differences.
Do not port just the component prompt exception without its deterministic guard.
No external payload field, delimiter, rating or provider-call change is intended.
