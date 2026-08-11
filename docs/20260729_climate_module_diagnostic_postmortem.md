# Climate-FCV Module Diagnostic Postmortem and Course Correction

**Date:** 2026-07-29  
**Purpose:** Restart-safe record of what was checked, what was learned, what
remains uncertain, and how to continue without repeating the same costly cycle  
**Repository:** `FCV-AGENT` (Render / Flask build)  
**Worktree:** `.worktrees/climate-readout`  
**Active branch:** `feat/climate-readout-redesign`  
**Deployed branch:** `origin/feat/climate-readout-redesign`  
**Deployed commit at pause:** `b102345`  
**Main branch:** intentionally untouched by this Climate work

## 1. Executive conclusion

The investigation did not uncover one isolated bug. It exposed three sequential
failure layers:

1. The Climate web search found evidence, but the structuring request replayed
   too much provider output and could truncate before producing valid JSON.
2. Once that was bounded, structurally valid sources were rejected because the
   model-generated source identifiers did not match the app's strict internal
   naming pattern.
3. Once Stage 1 passed, the supposedly compact Climate Stage 2 still generated
   16,000 output tokens and truncated before its closing diagnostic delimiter.

The first two defects have been corrected and observed working in a live run.
The third has a deployed compact-output correction, but that correction has not
yet been verified end-to-end because two subsequent live runs stopped at the
mandatory Stage 1 evidence gate.

The current Stage 1 problem is narrower than the original failures. Recent runs
returned complete JSON with three structurally valid sources and five
project-linked claims, yet the evidence gate still rejected the bundle. The
strongest suspicion is that the claims did not collectively cite two distinct
accepted sources, or less likely that none of the cited sources was classified
as authoritative. Existing logs do not distinguish those two conditions, so
this remains a hypothesis rather than a confirmed root cause.

The user reports that this investigation has consumed almost three weekly
allowances. That is disproportionate to the original request, which was to
review and stabilize work already developed in Claude Code. The process needs
to change before any more live experimentation.

## 2. Original intended architecture

The user-approved Climate module is not a second copy of the full FCV
assessment. Its intended design is:

- mandatory targeted Climate-FCV web research;
- fail closed if that research cannot produce validated evidence;
- a compact FCV sensitivity and responsiveness baseline;
- six stable Climate-FCV question anchors, with a small number of material
  supplementary questions where the evidence supports them;
- two causal directions: Climate/FCV pressures affecting the project, and the
  project affecting Climate/FCV dynamics;
- project-specific links to components, locations, groups, institutions,
  delivery systems, assets, indicators, and relevant OPCS guidance;
- climate-specific Stage 3 priorities; and
- no full 12-standard, DNH-9, or 25-question generic assessment machinery.

This architecture remains the correct target. The investigation showed that
parts of the implementation still behaved like the generic FCV route even
after the dedicated Climate prompt had been introduced.

## 3. Repository and branch arrangement

The repository was deliberately separated to protect ITS:

- `main` was restored to the closest available ITS-compatible baseline.
- Climate and dual-regime development were retained on feature branches.
- Active Climate development was conducted in the isolated worktree:
  `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\climate-readout`.
- The active local branch is `feat/climate-readout-redesign`.
- Render is configured to deploy `feat/climate-readout-redesign`.
- A parallel remote branch, `codex/climate-fcv-output-redesign`, was also kept
  synchronized late in the investigation.

One avoidable delay occurred when a tested commit was initially pushed only to
the parallel `codex/...` branch. Render tracks the `feat/...` branch, so the
deployment did not start until the commit was pushed to the branch Render
actually watches.

## 4. Materials and code areas reviewed

The investigation reviewed:

- the current Climate feature branch and commit history;
- `CLAUDE.md`, repository instructions, and the dual-build parity boundary;
- the earlier Claude Code transcript and Climate handoff documents;
- the Climate reliability design and implementation documents;
- `app.py` Stage 1, Stage 2, Stage 3, recovery, timeout, and SSE paths;
- `sector_lenses/research.py`;
- `sector_lenses/climate_native.py`;
- sector-lens normalization and validation in `sector_lenses/pipeline.py`;
- Climate question-bank composition;
- Express and step-by-step Climate route contracts;
- relevant tests in:
  - `tests/test_climate_research.py`;
  - `tests/test_climate_native.py`;
  - `tests/test_sector_lens_app_contract.py`; and
  - `tests/test_climate_workflow_contract.py`;
- Render deployment events and application logs; and
- repeated live Express runs using:
  `Project Concept Note (PCN)_Draft_15_June 2026.docx`.

The restricted raw OPCS policy corpus was not opened. Existing approved
summaries and code-embedded guidance were used instead.

## 5. Diagnostic chronology

### 5.1 Starting symptoms

The recurring user-visible failure was:

> The required Climate-FCV web research did not return at least two relevant
> sources...

Earlier runs also produced:

- Climate research timeout messages;
- a normal generic FCV assessment instead of a Climate assessment;
- `sector-lens Stage 2 prompt exceeded its token ceiling`;
- `Lens diagnostic block was not produced`; and
- Stage 3 remaining pending.

These messages represented different underlying failures but were initially
easy to conflate because the UI often reduced them to the same Stage 1 or Stage
2 error.

### 5.2 Confirmed oversized research handoff

The original search-to-structuring path replayed the full Sonnet conversation,
including tool blocks, into a Haiku structuring request.

Observed on Render:

- structuring input: approximately 14,891 tokens;
- output reached the 2,500-token ceiling;
- the response omitted the closing Climate research delimiter; and
- the parser correctly rejected the incomplete JSON.

This was not a failure to find sources. It was a failure to turn found evidence
into a bounded validated bundle.

### 5.3 Bounded evidence-packet correction

The full provider conversation replay was replaced with a deterministic,
bounded evidence packet containing only:

- bounded evidence notes;
- trusted HTTPS source titles, URLs, dates, and short excerpts; and
- a bounded project profile.

Raw tool blocks, encrypted provider payloads, and the original full
conversation are not replayed.

Live evidence after this change:

- packet size: approximately 2,757-2,901 characters;
- packet sources: four;
- structuring input: approximately 1,787-1,826 tokens;
- output: approximately 1,916-2,007 tokens;
- JSON and both delimiters present; and
- no structuring truncation.

This reduced the structuring input by roughly 88 percent and confirmed that the
large handoff was a genuine cause of the earlier truncation.

### 5.4 Strict source-ID mismatch

After the bounded handoff, the model produced valid JSON with valid source
types, titles, and trusted URLs, but all sources were discarded.

Content-free diagnostics showed:

```text
sources_count=3
claims_count=5
source_checks=id:0,type:3,title:3,url:3,valid:0
```

The only failing field was the model-generated source ID. The validator
required names such as `climate-source-1`, while the model could return other
internally consistent labels.

The correction now:

- accepts a bounded non-empty model source identifier;
- assigns stable internal IDs in source order;
- remaps claim references to those internal IDs; and
- assigns stable internal claim IDs.

This does not weaken URL, source-type, project-anchor, or evidence validation.

### 5.5 First successful live Stage 1

On deployed build `8020586`, assessment
`c3c9a5d8-27bc-4033-98ee-749909cf3bf0` passed the Climate evidence gate:

```text
packet_chars=2757
packet_sources=4
input_tokens=1787
output_tokens=1916
sources_count=3
claims_count=4
gate_code=ok
status=partial
sources=3
claims=4
```

The UI then completed Stage 1 and entered Stage 2. This proves that the bounded
handoff and identifier normalization can work together in production.

### 5.6 Confirmed oversized Climate Stage 2

The same successful run then spent several minutes in Stage 2 and failed with:

> Lens diagnostic block was not produced.

Render provided the exact cause:

```text
Stage 2 climate output hit max_tokens (cap=16000);
diagnostic tail may be truncated
```

This was the decisive confirmation that the Climate path was still too large.
Although it no longer appended the full generic prompt, its canonical Climate
schema still invited excessive expansion:

- up to 20 findings;
- one to four pathways per interaction;
- up to five evidence entries in several arrays;
- up to three items per readout section;
- up to two additional pathways per section; and
- lengthy narrative duplication across overlapping fields.

The model used the full 16,000-token allowance and lost the closing diagnostic
delimiter. Field-level recovery could not reconstruct the missing assessment
because the primary delimited payload was incomplete.

### 5.7 Deployed compact Stage 2 correction

Commit `b102345` changed the native Climate contract to:

- an 8,000-token model ceiling;
- a target of no more than approximately 7,000 output tokens / 28,000
  characters;
- at most eight findings;
- exactly one primary causal pathway per interaction direction;
- smaller evidence and source arrays;
- no more than two items per declared readout section;
- at most one additional pathway overall;
- concise single-paragraph narrative fields; and
- explicit instruction to reserve space for the closing delimiter.

The standard non-Climate FCV route retains its 16,000-token Stage 2 ceiling.

Verification before deployment:

```text
173 passed
```

This correction is deployed, but it has not yet been observed completing Stage
2 with the live PCN because the next two runs stopped at Stage 1.

### 5.8 Subsequent Stage 1 evidence-gate failures

Two runs on `b102345` failed at the mandatory evidence gate.

First run:

```text
packet_chars=2863
packet_sources=4
input_tokens=1803
output_tokens=2253
sources_count=3
claims_count=5
source_checks=id:0,type:3,title:3,url:2,valid:0
normalized sources=2
normalized claims=1
gate_code=climate_research_insufficient
```

Second run:

```text
packet_chars=2642
packet_sources=4
input_tokens=1735
output_tokens=1733
sources_count=3
claims_count=5
source_checks=id:3,type:3,title:3,url:3,valid:3
normalized sources=3
normalized claims=5
gate_code=climate_research_insufficient
```

The second result is important: source structure, URLs, and project-linked
claims were all valid, but the evidence gate still failed.

The gate additionally requires:

- at least two distinct cited source URLs;
- at least one cited authoritative source; and
- at least one project-linked claim.

Because five claims survived normalization, the project-link requirement was
met. The unresolved condition is therefore either:

1. the claims collectively cited only one distinct source; or
2. the cited sources were all classified as non-authoritative specialist or
   current-operations sources.

Current logs do not report those two booleans separately. Citation diversity is
the stronger suspicion, but it is not yet proven.

## 6. Commit record for this diagnostic cycle

Key commits, oldest to newest:

| Commit | Purpose |
|---|---|
| `7011b8f` | Design bounded Climate evidence handoff |
| `2801b9e` | Add bounded search evidence packet |
| `5056541` | Structure bounded Climate evidence |
| `5bcf131` | Distinguish structuring truncation |
| `392aeeb` | Document bounded handoff |
| `0db8b4c` | Add content-free source validation diagnostics |
| `8020586` | Normalize Climate evidence identifiers |
| `b102345` | Enforce compact Climate Stage 2 output |

Earlier commits in the branch addressed related prompt isolation, research
continuation, overload handling, and recovery diagnostics. The length of this
sequence is itself evidence that the work proceeded through serially revealed
failure layers rather than one bounded diagnosis.

## 7. Current uncommitted work

At pause, the worktree has three modified files:

```text
M app.py
M sector_lenses/research.py
M tests/test_climate_research.py
```

The uncommitted change:

- switches the small evidence-structuring call from Haiku to Sonnet;
- strengthens the instruction that claims must cite at least two distinct
  listed sources; and
- updates the associated regression test.

Focused verification:

```text
35 passed
```

This work was intentionally not committed or deployed after the user requested
a pause.

It should be treated as a proposed hypothesis-driven change, not a confirmed
fix. The available telemetry does not yet prove whether citation diversity or
authoritative classification caused the latest gate rejection.

## 8. What worked

- Separating `main` from Climate development protected the ITS baseline.
- Content-free telemetry identified the source-ID mismatch without logging
  project or source content.
- The bounded evidence packet sharply reduced input tokens and eliminated the
  original structuring truncation.
- Deterministic identifier normalization removed a non-semantic validation
  failure.
- The evidence gate correctly failed closed rather than generating a generic
  or unsupported Climate assessment.
- A real live run proved that Stage 1 can pass and reach the native Climate
  Stage 2 path.
- The live Stage 2 log finally confirmed that the 16,000-token canonical
  payload was not compact in practice.
- Tests now assert that Climate Stage 2 does not use the generic FCV prompt
  engine and that its output ceiling is separate from the standard route.

## 9. What did not work well

### 9.1 Too many sequential live deployments

Several hypotheses were tested one deployment at a time. Each deployment
required waiting for Render and then running a multi-minute stochastic
workflow. Later failures often appeared only after the earlier stage had
completed. This is the most important source of elapsed time and model usage.

### 9.2 Observability was added incrementally

The first logs reported only a broad failure code. Additional diagnostics were
then added for response structure, source fields, and token usage in separate
cycles. A single up-front diagnostic matrix would have reduced the number of
deployments.

### 9.3 Stochastic web research blocked deterministic Stage 2 testing

After the Stage 2 compact correction was deployed, verification again started
from live web research. Two evidence-gate failures then prevented any test of
the Stage 2 change. Stage 2 should have been tested independently using a known
valid research fixture before another full end-to-end run.

### 9.4 Test success was interpreted too broadly

Contract tests proved code paths and schemas but did not prove that a live
model would stay within the requested output size. The first live run after
Stage 1 succeeded showed that the model could consume all 16,000 tokens despite
the prompt being described as compact.

### 9.5 The recovery path was treated as a safety net

When the complete delimited Stage 2 payload is truncated, field-level recovery
has too little valid primary material to repair. Recovery is useful for a few
missing fields, not for reconstructing an absent canonical assessment. The
primary response must fit reliably.

### 9.6 Branch and browser overhead

- One commit was initially pushed to the wrong remote feature branch for
  Render.
- Browser-control bindings were lost more than once, requiring reconnection and
  repeated page orientation.
- Windows Application Control blocked `apply_patch`; exact byte-preserving
  fallback edits and one encoding recovery added operational overhead.

These were not the primary technical defects, but they increased time and
context usage.

### 9.7 The scope drifted from review into redesign

The original request was mainly to inspect and improve Claude Code's completed
updates. The work expanded into architecture redesign, observability,
provider-handoff changes, recovery changes, output-contract changes, repeated
production deployments, and full browser testing. Some expansion was justified
by the discovered defects, but the cumulative scope was not explicitly
re-baselined against cost after each new layer appeared.

## 10. Why usage became disproportionate

The user reports almost three weekly allowances consumed. No precise
allowance-level accounting is available in the repository, but the likely
drivers are clear:

- a very long continuous session carrying extensive prior context;
- repeated reading of large code and documentation surfaces;
- multiple multi-minute live LLM workflows;
- serial deploy-observe-patch cycles;
- verbose browser and Render log output;
- stochastic failures that made identical PCN runs produce different evidence
  bundles;
- several new tests and diagnostic instruments added after, rather than before,
  the first reproduction;
- continued end-to-end testing when a narrower stage-specific test would have
  answered the immediate question; and
- no hard stop rule after a fixed number of failed live attempts.

The important lesson is not merely to use a smaller model. The workflow itself
must minimize the number of provider calls and isolate each stage before a full
run.

## 11. Course correction

### 11.1 Stop conditions

Do not perform another end-to-end Render run until all of the following are
true:

1. The exact next hypothesis is written down.
2. The required diagnostic signal is available before deployment.
3. The change passes a deterministic local regression.
4. The affected stage can be tested independently.
5. A single live run has explicit success and failure criteria.

Stop after one failed live verification. Do not patch immediately. Record the
new evidence and decide whether it disproves the hypothesis.

### 11.2 Separate the two remaining questions

Treat these as independent:

1. **Stage 1 reliability:** Why did a structurally valid three-source,
   five-claim bundle fail the evidence gate?
2. **Stage 2 compactness:** Does `b102345` produce a complete canonical payload
   below the 8,000-token ceiling?

Do not require Stage 1 to succeed in order to test Stage 2.

### 11.3 Cheapest next diagnostic

Before changing Stage 1 behavior, add one content-free gate summary that reports
only:

- normalized bundle status;
- distinct cited source count;
- authoritative cited source present: yes/no;
- project-linked claim present: yes/no; and
- final gate code.

This is sufficient to distinguish the two remaining Stage 1 hypotheses without
logging titles, URLs, claims, or project text.

Do not deploy the current uncommitted Sonnet switch until this diagnostic either
confirms citation diversity or provides another clear reason for the failure.

### 11.4 Test Stage 2 without web research

Use the existing South Sudan Climate research fixture or another known-valid,
content-safe fixture to call the Stage 2 path directly. The test should supply:

- a known valid `climate_research` bundle;
- the already extracted bounded Stage 1/project context; and
- Climate as the active lens.

This allows one live-model Stage 2 call, or a tightly controlled local
integration call, without paying for another web search and full Stage 1
analysis.

Required Stage 2 evidence:

- configured cap is 8,000;
- stop reason is not `max_tokens`;
- both Climate diagnostic delimiters are present;
- canonical JSON parses;
- required compact baseline and interaction directions survive normalization;
- no recovery is required, or only a genuinely small field repair is required;
  and
- rendered output is recognizably Climate-specific rather than the generic
  12-standard assessment.

### 11.5 One behavior change at a time

If the next diagnostic confirms insufficient citation diversity:

- first strengthen the structuring contract;
- decide explicitly whether Sonnet is justified for the small structuring call;
- run the focused structuring fixture tests;
- deploy once; and
- run only the research stage if a research-only path is available.

Do not simultaneously change model, gate semantics, source normalization, and
prompt wording. That would make the result uninterpretable.

### 11.6 Do not weaken the evidence gate by default

The user explicitly approved fail-closed behavior. Do not silently accept:

- two listed but uncited sources;
- generic country-level climate evidence;
- unsupported project links; or
- a generic FCV fallback presented as a Climate assessment.

If the gate proves too brittle, any policy change should be presented as a user
decision with examples of what would newly be accepted.

### 11.7 Minimize documentation and context reload

The next session should read:

1. this postmortem;
2. `docs/20260728_climate_module_reliability_handoff.md`;
3. the July 29 bounded evidence design;
4. the current three-file diff; and
5. only the specific functions and tests relevant to the chosen hypothesis.

It should not reread the full repository history, all prior handoffs, or the
entire large `CLAUDE.md` unless a specific rule requires it.

## 12. Recommended next steps

### Step 1: Preserve the checkpoint

- Do not modify `main`.
- Do not discard the three uncommitted files.
- Record the current diff before editing.
- Do not commit the proposed Sonnet switch as if it were proven.

### Step 2: Add one gate-breakdown diagnostic

Add and test the five content-free fields listed in Section 11.3. This should be
one small commit with no behavior change.

### Step 3: Validate compact Stage 2 independently

Use a known-valid research fixture and bypass stochastic Stage 1. If Stage 2
still truncates at 8,000 tokens, reduce the schema further or split generation
and deterministic rendering. Do not increase the token ceiling again.

### Step 4: Make one evidence-structuring decision

After the gate breakdown is known:

- retain Haiku if the failure was not instruction-following;
- use Sonnet only if it materially improves the small structured handoff; or
- redesign the evidence packet so source-to-excerpt attribution is
  deterministic enough that the model does not have to infer citation
  relationships.

The preferred long-term direction is deterministic source/excerpt association,
not repeated model upgrades.

### Step 5: Run one final end-to-end acceptance test

Only after Stage 1 and Stage 2 pass independently:

- deploy the combined branch once;
- run the supplied PCN once;
- capture assessment ID and low-cardinality diagnostics;
- verify Stage 1, Stage 2, Stage 3, and DOCX output; and
- stop whether it passes or fails.

If it fails, document the failure without immediately beginning another patch
cycle.

## 13. Success criteria for resuming

The issue should not be called resolved until one live run demonstrates:

- mandatory research returns at least two distinct cited relevant sources;
- at least one cited source is authoritative;
- claims remain tied to named project elements and concrete anchors;
- Stage 1 completes without generic fallback;
- Stage 2 completes below its 8,000-token ceiling;
- the canonical Climate payload parses without reconstructive recovery;
- the visible readout is the compact Climate module, not the full generic
  12-standard / 25-question assessment;
- Stage 3 produces Climate-specific priorities from the canonical payload; and
- the downloaded report preserves the Climate readout.

## 14. Restart commands

```powershell
Set-Location "C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\climate-readout"
git status --short --branch
git log -12 --oneline --decorate
git diff -- app.py sector_lenses/research.py tests/test_climate_research.py
```

Focused current verification:

```powershell
python -m pytest tests/test_climate_research.py -q -p no:cacheprovider
```

Broader Climate verification:

```powershell
python -m pytest `
  tests/test_climate_native.py `
  tests/test_climate_research.py `
  tests/test_sector_lens_app_contract.py `
  tests/test_climate_workflow_contract.py `
  -q -p no:cacheprovider
```

## 15. Final caution

Do not interpret the number of commits or tests as evidence that the system is
now reliable. The bounded research handoff and identifier normalization are
live-proven. The compact Stage 2 limit is code- and contract-tested but not yet
live-proven. The latest Stage 1 gate failure is not yet fully diagnosed.

The next session should be shorter, stage-specific, and governed by explicit
stop conditions. The objective is no longer to keep trying until a run passes.
It is to obtain one decisive signal per provider call and make the smallest
evidence-supported change.
