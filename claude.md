# claude.md — FCV-AGENT (Render build of the FCV Project Screener)

Project-level instructions for this repo. Supplements the global
`C:\Users\wb559324\.claude\CLAUDE.md`, which covers general working rules.

> **Filename is lowercase on purpose.** Tracked as `claude.md` in git; a staged
> `git add CLAUDE.md` silently matches nothing on this case-sensitive repo.

---

## Start here

1. Read `README.md` for current project scope and modes (Express vs Step-by-Step).
2. Check `git status`, current branch, and the latest commit — do not trust an
   earlier chat as the source of truth.
3. If about to change **prompts, delimiter schemas, Stage-3 priority JSON fields,
   routes, or the knowledge base**, read the parity contract first:
   `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`. The ITS build at
   `C:\Users\wb559324\WBG\FCV-RISK-PYTHON-API` must stay compatible.

## Project goal

Flask web app that guides World Bank TTLs through a 3-stage FCV assessment of
project documents (PCN, PID, PAD, DPF, PforR, MPA). Stage 1 extracts context,
Stage 2 assesses FCV dimensions with Do No Harm traffic-lights, Stage 3 generates
a structured recommendations note. Stage 3 renders one Word-aligned browser readout
(`static/fcv_readout.js`) that the Copy control and Share .html export reuse; the
toolbar offers a single Download report menu (Word / HTML). Management-brief and
review-packet helpers remain in code but have no toolbar buttons (approved 2026-10-28).

## Commands

```powershell
# Test
C:/WBG/Python313/python.exe -m pytest -q

# Lint
C:/WBG/Python313/python.exe -m ruff check .

# Run locally
C:/WBG/Python313/python.exe -m flask --app app run
```

## Deployment

- **Service:** `fcv-agent.onrender.com` (Render).
- **Auto-deploy is OFF** on main after the 2026-10-18 climate incident. Production
  deploys are manual via Render dashboard trigger.
- **Rollback reference:** commit `1168a8f` (pre-climate-pilot stable).
- Preview environments use the normal Render PR preview flow.

## Hard constraints

- **Advisory only.** No policy, compliance, eligibility, endorsement, or clearance
  determinations. Recommendations are suggestions for professional review.
- **No OPCS source material in this repo.** OPCS PPF corpus / ESF Manual lives in
  the ITS build's `ppf_indexer.py` only. Work from written summaries here.
- **Cost ceilings bind.** Paid runs require explicit per-run authorization with a
  reservation record and exclusive lock file. Never reuse a consumed allowance.
- **Humanize reader-facing prose** (five-minute readout, detailed note, briefs)
  with the `humanizer` skill as a final pass. Preserve every finding, figure,
  citation and caution exactly. Skip for code, tests, config, logs.

## Word output conventions

Arial throughout, bold opening sentence per body paragraph, no em dashes,
editable headings. Strengths use green accents, potential gaps use light orange.
Full-width navy running banner is a single header paragraph (shading, negative
horizontal indents, zero header distance, 42.5 pt exact line height, white text,
teal border). Default header only — do not create a separate even-page header.

## Standing authorisations (given by the project owner, 2026-11-18)

Act on these without asking again; report what was done.

- **GitHub (`ljonestz/FCV-AGENT` only):** push feature branches, open and edit PRs,
  mark them ready, and merge a PR into `main` (merge commit) once its checks pass and
  the owner has asked for that work to be merged, shipped or made production ready.
  Still never commit directly to `main`, force-push or rewrite history.
- **Production deploy (`fcv-agent.onrender.com`, `srv-d6de99jh46gs73d0jjrg`):** trigger
  Manual Deploy of the latest `main` commit, and roll back on request, once the work is
  merged and the owner has asked to ship it. Verify `/health` shows the new build.
  Production env vars, secrets, plans and billing remain the owner's.
- **Test service (`fcv-agent-1.onrender.com`, `srv-d6gsivcr85hc73a2833g`):** change
  branch, deploy, set `CLIMATE_RESEARCH_MODE` and the spend-guard variables, and restore
  the blocker (`FCV_PILOT_BUDGET_MICROUSD=1`) after paid runs.
- **Paid runs:** a chat authorisation naming a run count or cost cap covers that batch.
  Record each run in the ledger before it starts, never reuse a consumed slot, keep to
  the cap, prefer `bank_only` research, and run only against `fcv-agent-1`.

These are mirrored in Claude Code's auto-mode rules by
`~/.claude/tools/20261118_add-standing-authorisations.py`. If the auto-mode check
still blocks an action, stop, name it and give the owner the one-line `!` command.

## Test documents (owner's folders, outside the repo)

Real project documents for offline replay, parser checks and paid validation batches:

- `C:\Users\wb559324\OneDrive - WBG\fcv-project-screener\FCV_Screener_test_cases\`:
  - **Country cases:** AFG HCJ (PID), AFG Private (PCN), Guinea Gov and Guinea Water (BOSIB PDFs), Honduras (PCN + PAD), each with its CPF/PLR and RRA.
  - **Moz Resil:** a climate and FCV assessment.
  - **Synthetic Project Paper:** `20260727_SYNTHETIC_new-model_project-paper_chad-lac-health.docx`.
  - **`Sector_ENRM_EWS_2026-11\`:** early-warning, ENRM and water/agriculture PADs fetched from the public WDS API, with a README.
- `C:\Users\wb559324\OneDrive - WBG\Documents\Cowork\Tasks\wbg-project-documents-access-through-2026-06-22\output\WBG_Appraisal_TestCases\`:
  - Organised by instrument: DPF, IPF, MPA, multi-country MPA, PforR and closed projects.
  - Each folder has a README.
- **Syria STAR PAD (climate benchmark):** `C:\Users\wb559324\OneDrive - WBG\Attachments\P515346 Syria STAR PAD ROC.docx`.
- **Finding more documents:** use the public WDS API (`search.worldbank.org/api/v2/wds?format=json&proid=P...`). Internal Databricks `pdf_urls` redirect to SSO.

## Known gotchas

- **Climate route (instrument routing).** Instrument routing feeds
  `operational_guidance`; an unresolved route silently empties the recommendation
  compiler. See `docs/claude-journal.md` 2026-10-18 entry for the four
  deterministic fixes landed on PR84 (main `6f3d5e6`).
- **Datasheet checkbox parsing.** Unchecked `[  ] MPA` template labels used to
  flag `is_mpa=true`; deboxed in `resolve_verified_operation_context`.
- **Readout wording (approved 2026-10-28).** No generic "Draft - human review
  required", reader-review or "Preparation route" preambles in browser or Word;
  specific notices (incomplete/partial, smoke, preview evidence, unresolved-route
  drafting gate) stay. Drafting labels are "Suggested Text" / "Suggested Text for an
  operational instrument"; the optional-priorities advisory sentence accompanies
  the priorities on every route.
- **Climate country bank.** The app pins the qualified 146-country bank (pin
  recorded in the latest journal entry). Approval is permission to use, not
  certification; search results never update the bank.
  `CLIMATE_RESEARCH_MODE=bank_only` suppresses both live research providers.
- **Test-service spending is blocked by default** (web flag 0, budget 1 microUSD).
  A paid run needs fresh explicit authorization; see the journal for the ledger.
- **Large PADs + USD6 ceiling.** Final `reader_review` can be budget-blocked on
  large documents; distinguish budget withhold from genuine reviewer withhold
  before diagnosing output quality.

## Historical context

For the running incident and decision journal (61 dated entries from 2026-10
onward), see `docs/claude-journal.md`. Treat it as reference, not a load-every-
session document.
