# IPS/ITS Handover Brief - PforR Timeout and Render Main State

Date: 2026-07-14

Audience: IPS/ITS colleagues maintaining or testing the internal World Bank build of the FCV Project Screener.

Purpose: summarize the PforR/P4R timeout work now merged to `main`, what has been verified on the public Render build, and what logs to inspect if long-running PforR tests still appear to hang.

---

## 1. Current Main Branch State

The public Render app deploys from `main`. The latest relevant merge is PR #51:

- `origin/main`: `2877bf9` - `Merge pull request #51 from ljonestz/codex/main-pforr-timeout-push-20260714`
- PR branch commit: `9665ab3` - `fix: handle PforR timeout and upload limits`
- Prior PforR/DPO vocabulary timeout patch: PR #47 / merge `234bf43`, commit `3b04a97`
- Test suite before merge: `208 passed`

The deployed app at `https://fcv-agent.onrender.com/` was confirmed live after PR #51: `/health` returned `200`, and the served HTML included the new timeout/payload handlers.

---

## 2. What Changed for PforR/P4R

The PforR issue had more than one contributing pathway. Main now includes fixes for each known pathway:

1. **Blocking vocabulary repair removed.** PforR/DPO Stage 2 and Stage 3 no longer run a non-streaming model rewrite after generation. `repair_vocabulary_violations()` is now a deterministic regex scrub, so it cannot create a silent post-stream gap or truncate the Stage 3 JSON block.
2. **Backend stage caps raised for PforR-scale outputs.** `_stream_stage()` now uses wall-clock caps of Stage 1 = 8 minutes, Stage 2 = 9 minutes, Stage 3 = 9 minutes.
3. **Frontend abort budgets now sit above backend caps.** Express and step-by-step budgets are Stage 1 = 9 minutes, Stage 2 = 10 minutes, Stage 3 = 10 minutes. This avoids browser/backend timeout races.
4. **Frontend timeout messages are preserved.** `requestErrorMessage()` keeps custom `AbortController.abort(new Error(...))` messages instead of collapsing them into `Could not reach the server.`
5. **Stage 1 preprocessing diagnostics added.** Both `/api/run-stage` and `/api/run-express` log low-cardinality summaries at preprocessing start and extraction completion.
6. **Secondary-document distillation now streams progress.** Distillation yields each completed/timeout card as it arrives and emits `keepalive` / `distilling_wait` events while slower secondary documents remain pending.
7. **Upload-size failure is explicit.** Oversized browser base64 JSON uploads now return `413` with a clear message; the frontend also preflights raw file size before submission.

---

## 3. Live Render Evidence So Far

These checks were run against the public Render app after PR #51 was merged.

| Test document | Route | Result | Notes |
|---|---|---|---|
| Morocco Green Generation PforR PAD (`P170419`) | `/api/run-stage`, Stage 1 only | Success | HTTP 200, 237 SSE events, completed in about 4:14. |
| Morocco Green Generation PforR PAD (`P170419`) | `/api/run-express` | Success on rerun | HTTP 200, all three stages streamed, clean stream end after about 13:42. One earlier attempt returned transient Cloudflare/Render 502 after about 35s. |
| India STARS PforR PAD (`P166868`) | `/api/run-express` | Hung before response headers | Client timed out after 30 minutes with no HTTP response headers. Local PDF extraction for this same file completed in about 18s, so this is not obviously a PyPDF extraction hang. Requires Render-log review. |
| Seychelles Social Protection PforR PAD (`P168993`) | Pending | Test was interrupted before completion. Local PDF extraction completed in about 11s. |

Local extraction timings for the three PforR PADs:

| Document | Size | Pages | Extracted chars | Local extraction |
|---|---:|---:|---:|---:|
| India STARS PAD | 1.78 MB | 120 | 320k | about 18s |
| Seychelles Social Protection PAD | 2.15 MB | 98 | 201k | about 11s |
| Morocco Green Generation PAD | 4.19 MB | 165 | 500k cap reached | about 32s |

Interpretation: Morocco proves the current main can complete a substantial PforR end-to-end. India suggests there may still be an intermittent Render worker/gateway stall before the first SSE response, or a pre-response call path that can block on some documents. The new logs should identify where.

---

## 4. What to Check in Render Logs

For any PforR run that appears to load for a very long time, capture the exact start/failure time and search logs for these lines:

```text
Stage 1 preprocessing start route=run-express summary=...
Stage 1 extraction complete route=run-express elapsed_ms=... doc_parts=... extracted_chars=... warnings=...
```

Use the log position to classify the failure:

| Log pattern | Likely meaning | Next check |
|---|---|---|
| No `Stage 1 preprocessing start` | Request never reached Flask route or worker did not begin generator. | Render gateway/proxy, worker availability, cold start, deploy/restart. |
| Preprocessing start exists but no extraction complete | Request reached app but stalled/crashed during JSON parsing or document extraction. | Worker memory/CPU, PyPDF extraction, `SIGKILL`, OOM, timeout. |
| Extraction complete exists but no `research_status` / Stage 1 chunks | Stall is after extraction, likely country/sector extraction, web research, or first model call. | API latency/errors, research client timeout, provider logs. |
| Stage 1/2/3 chunks stream then explicit stage timeout | App-level stage cap hit. | Consider output reduction, cap increase, or higher Render instance. |
| Cloudflare/Render `502` | Gateway lost backend worker/connection. | Worker restart, OOM, deploy event, free-tier instability. |
| Browser shows `Could not reach the server.` | True fetch/network failure, not the custom frontend timeout message. | Compare browser time with Render 5xx/restart logs. |

---

## 5. Porting Notes for the Internal Build

If the internal build has equivalent PforR/DPO vocabulary repair logic, keep it deterministic or stream/keepalive it. Avoid any blocking, non-streaming post-generation model call before the client receives a completion event.

If the internal build does not have that vocabulary repair path, focus on generic long-run infrastructure:

- per-stage server wall-clock limits;
- frontend/proxy idle timeouts;
- keepalive cadence before time-to-first-token and between stages;
- synchronous post-stream processing;
- whether the first SSE event is flushed before extraction/research/model setup;
- memory/CPU pressure for PforR PADs on the selected hosting tier.

The public Render build is resource-constrained. A paid/larger instance may still be needed for reliable multi-minute PforR runs under real user load, even with the app-level timeout fixes.

---

## 6. Brief Teams Message Draft

Hi all - quick update on the FCV screener PforR timeout issue. I have merged a set of changes to the public Render `main` build that address the main timeout paths we found: the blocking PforR/DPO vocabulary repair, Stage 2/3 timeout caps, frontend timeout messaging, Stage 1 diagnostics, and clearer handling of oversized uploads. The Morocco PforR PAD has now completed end-to-end on Render in testing, though I am still watching one India PforR case that appeared to hang before the first response. If useful, you can try the current Render version here: https://fcv-agent.onrender.com/ and let me know whether you see any remaining PforR failures, ideally with the approximate run time so I can line it up with the logs.
