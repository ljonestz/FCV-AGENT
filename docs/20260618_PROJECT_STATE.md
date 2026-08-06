# FCV-AGENT — Project State Map (2026-06-18)

Purpose: a single "where everything is" reference so any operator or LLM can orient
quickly. Covers branch layout, open PRs, deployment state, and outstanding items.
Supersedes the earlier session handoffs for current status.

> This file lives on `main`. As of 2026-06-18, `main` does **not** yet contain the
> phase 0-6 knowledge-base work or the OPCS policy corrections. Those are staged in
> PR #29 (see below) and reach `main` only when that PR is merged.

---

## 1. Coordinates

| Thing | Value |
|---|---|
| Repo | `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT` |
| Remote | `origin` = `https://github.com/ljonestz/FCV-AGENT.git` |
| Default branch | `main` |
| Deployed instance | `https://fcv-agent-1.onrender.com` (Render) |
| External review artifacts / evidence | `...\Cowork\Tasks\reviewing-fcv-agent-app-policy-changes-2026-06-17\output\` |

Core code files: `app.py` (Flask backend + all stage prompts), `background_docs.py`
(knowledge-base constants), `index.html` (single-page frontend), `Procfile`,
`requirements.txt`.

---

## 2. Branch map

| Branch | Role | Status |
|---|---|---|
| `main` | Production / default | What Render most likely deploys (confirm in dashboard) |
| `feat/phase6-intersection` | Tip of the phase 0-6 stack | 8 commits ahead of `main`; carried by PR #29 |
| `feat/phase0-kb-currency-registry` ... `feat/phase45-mpa-multicountry` | Phase stack (0-5) | Stacked PRs #24-#28; redundant once #29 merges |
| `fix/stage3-express-freeze` | Stage 3 silent-stall fix | Open PR #20 into `main`; separate from the phase stack |
| `codex-mai-fcv-skill-design` | Codex skill design work | Checked out in the root folder working tree; unrelated to phase work |

The phase work was developed as a **stacked PR chain**. PR #29 was retargeted to
merge directly into `main`, so it now carries the full phase 0-6 history in one PR.

---

## 3. Open PRs

| PR | Head -> Base | Carries |
|---|---|---|
| **#29** | `feat/phase6-intersection` -> `main` | Phases 0-6 KB expansion + OPCS policy corrections + DM/ROC timing + landing-copy fix. Ready, mergeable. The gate to production for all recent work. |
| #20 | `fix/stage3-express-freeze` -> `main` | Stage 3 silent-stall fix (Diagnosis A). Not included in #29. |
| #24-#28 | phase stack | Superseded by #29 for reaching `main`; can be closed. |

---

## 4. What PR #29 contains (commit order)

- **phase 0** — registry + policy currency patch
- **phase 1** — mid-cycle overlay (AF & Restructuring)
- **phase 2** — DPF/DPO instrument module
- **phase 3** — P4R/PforR instrument module
- **phases 4+5** — MPA wrapper + multi-country/regional layer
- **phase 6** — intersection matrix (multi-dimension composition)
- **OPCS policy corrections + timing** — renumbered WBG instruments (verified against
  intranet sources), IDA FCV Envelope reframed to three allocations (PRA/RECA/TAA),
  recommendation timing re-anchored on the Decision Review (DM/ROC). Label/definition
  changes only; enum values and CSS classes unchanged for frontend compatibility.
- **landing-copy fix** — opening text now states the tool reviews design-stage docs
  (PCN/PID/PAD) with DM/ROC timing; MTR/ISR implementation review marked "coming soon".

Policy citations were verified against intranet OPCS/FCV sources reflecting the
2024-2026 renumbering. Do **not** "re-verify" them from model memory: recall of WBG
instrument numbers is unreliable. Evidence captured in the external output folder
(`SOURCE-EVIDENCE-PACK_2026-06-18.md`, `CHANGE-RECORD_background_docs_2026-06-17.md`).

---

## 5. Deployment state (Render)

Two things to fix in the Render dashboard (no code change):

1. **Start Command** — Render is running the Flask **dev server** (`python app.py`),
   which overrides the `Procfile`. Set the service Start Command to the gunicorn line
   in `Procfile` (or clear it so Render falls back to the `Procfile`):
   ```
   gunicorn app:app --worker-class gevent --workers ${WEB_CONCURRENCY:-4} --threads ${GUNICORN_THREADS:-2} --bind 0.0.0.0:$PORT --timeout 600
   ```
2. **Deploy branch** — confirm which branch Render builds. For any recent work to go
   live, it must build `main` **after** PR #29 is merged.

The previously deployed build predates the 8-minute Stage 3 stream guards that exist
on `feat/phase6-intersection`, which contributed to the "stuck on finalising" hang.

---

## 6. Feature status — implementation review

Two independent axes (these were initially conflated):

- **Instrument / document type = ALL ACTIVE.** AF, Restructuring, DPF/DPO, MPA, PforR,
  multi-country are driven by doc-type detection in the always-on design path and work
  today when the matching document is uploaded.
- **Review *mode* (`design` vs `implementation`) = WITHHELD.** The dedicated MTR/ISR
  supervision lens (`review_mode='implementation'`) is built in the backend but
  unreachable in the UI (`selectReviewMode()` has no callers; the toggle markup does
  not exist; the mode is cleared with `// implementation review is not yet live`).

So only the dedicated MTR/ISR supervision workflow is withheld. Enabling it later means
re-adding the toggle UI and testing the impl path end-to-end.

---

## 7. Outstanding items

| # | Item | Owner |
|---|---|---|
| 1 | Merge **PR #29** into `main` | User (review + click) |
| 2 | Render **Start Command -> gunicorn** | User (dashboard) |
| 3 | Confirm Render **deploy branch** (= `main` after merge) | User (dashboard) |
| 4 | Capture **failing-run Render logs** to pin the Stage 3 hang | User |
| 5 | Consider merging **PR #20** (Stage 3 silent-stall fix) | User |
| 6 | Close superseded phase PRs **#24-#28** | Optional |
| 7 | Later: enable **implementation review** (MTR/ISR) properly | Future branch |

---

## 8. Related docs

- `README.md` — setup, deployment, key files (see "Current status" section).
- `claude.md` — full developer guide (architecture, prompts, stage pipeline).
- `docs/reference/` — per-stage prompt specs, routes, frontend functions.
- `docs/IMPLEMENTATION_REVIEW_DESIGN.md` — design notes for the withheld MTR/ISR mode.
- Earlier handoffs: `docs/20260412_SESSION_HANDOFF.md`, `docs/HANDOFF_v8_knowledge_base.md`.
