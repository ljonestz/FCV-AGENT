# Claim-level review and repair: offline prototype design

## Approved scope

After repeated prompt-tuning failures, the user approved reconsidering the design:
check factual assertions, preserve qualified analysis, repair precise wording and
independently review edits once. Build one bounded offline prototype using saved
failures. No paid calls, full assessment, deployment or production integration.

## Design decision

Use a claim-level adapter around the existing exact-text correction function.
Another paragraph-verdict prompt patch would keep the same failure mode. A new
semantic classifier or larger evidence-extraction system would add unproven
machinery. The adapter instead makes each decision inspectable and separates
source comparison, edit permission and final acceptance.

Application-owned reader records, paragraph positions, original text and source
registry remain authoritative. Each finding has a unique finding ID, exact claim
span, claim role, source comparisons and a concise explanation. Multiple findings
may concern one paragraph. Review coverage must name every submitted record;
missing coverage is incomplete review. Optional precision is distinct from factual
repair. Qualified inference and proposed action are not defects merely because
the source does not state them verbatim, but embedded factual premises remain
reviewable. Unknown instrument content is not evidence of failed protection.

Corrections account for each material finding through a bounded edit or explicit
dispute. A dispute remains in the ledger for independent adjudication; it cannot
silently disappear or authorize an edit. Group approved edits by record only at
the existing apply_reader_corrections boundary. Preserve sources, evidence IDs,
untargeted text and original-offset/overlap/numeric/date protections. Never infer
an edit permission from an object's inclusion alone.

The intended orchestrated workflow permits one correction pass. The offline adapter
rejects a pending result as a fresh plan, but cannot prevent a caller from invoking
the original plan again; process-wide call/spend limits belong to the orchestrator. The final independent review is bound to the
entire revised reader digest and covers all records, every original finding,
disputes, source evidence and any new defect. An unresolved optional precision suggestion remains nonblocking and traceable.
An unresolved material finding,
missing coverage, stale text digest or failed final review withholds acceptance.
The prototype's result is a test outcome, not publication authorization. Reviewer
and editor labels record different roles; they are not an authentication mechanism.

## Required demonstrations

- Two genuine findings in the same paragraph are independently repaired while
  surrounding valid analytical text and all evidence records remain unchanged.
- A false affected-population access objection stays disputed, with valid analysis
  untouched, until explicit independent source adjudication resolves it.
- Generic safeguard and planned-delivery overclaims receive narrow edits.
- Study/site and recipient/funding scope defects remain material findings.
- Explicit matching access/protection provisions defeat blanket omission claims;
  unmeasured effectiveness does not erase a documented provision.
- Faithful weaker paraphrase (most versus92 percent) stays acceptable; optional
  temporal precision cannot itself force a factual rejection.
- Missing coverage, duplicate finding IDs, invented source IDs, nonunique quotes,
  overlapping/out-of-scope edits, number expansion, skipped/stale final review,
  unresolved or newly introduced defects cannot produce an acceptance result.

## What offline validation can establish

Exact quotes and source IDs prove traceability, not semantic entailment. Claim
classification, premise completeness and source meaning remain judgments. Record coverage is not proof of claim/premise
completeness. Digests detect text drift, not the authenticity of caller-owned state. Curated
adjudications reproduce the intended behavior and exercise application mechanics;
they are never reported as fresh successful model decisions. The latest raw failed
reviews and historical labels remain unchanged. A separate bounded model test would
be needed before runtime integration, followed by correction/re-review, latency,
cost and export acceptance. Do not promise that the next paid run will fix this.
