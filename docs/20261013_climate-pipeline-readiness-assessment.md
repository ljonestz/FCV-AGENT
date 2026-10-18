# Climate pipeline readiness assessment

## Scope and method

Assessment requested13October after quality6. Traced the source/research,
fact/analysis, recommendation/drafting, independent review/correction, Summary,
reader and export paths. Compared six saved paid assessments of the same named
Great Lakes AF appraisal PID across different prompt versions. Reproduced two
contract failures offline with fake clients; inspected production schemas and
validators. These observations diagnose this case and pipeline, not a statistical
estimate of performance across projects. No additional paid assessment was used.

The all-open priority layout is a separately approved implementation. The backend
redesign below is a proposal for review, not an implemented or accepted release.
Production/main and ITS remain held. Restricted OPCS source documents were not read.

## Evidence from the saved runs

| Saved quality run | Generated candidates | Structurally admitted | Final priorities | Native Summary | Research |
|---|---:|---:|---:|---|---|
| 1 | 5 | 4 | 0 | Fallback | Partial |
| 2 | 3 | 3 | 1 | Fallback | Partial |
| 3 | 3 | 3 | 1 | Fallback | Partial |
| 4 | 0 | 0 | 0 | Fallback | Failed |
| 5 | 4 | 4 | 2 | Fallback | Partial |
| 6 | 4 | 4 | 2 | Fallback | Failed |

There is no observed two-action frontend cap. Runs5/6 each admitted four candidates
before semantic review. Synthetic readers already support up to five. Suppression
occurs upstream; changing how many cards are displayed cannot recover withheld actions.

## 1. Recommendations and drafting are coupled incorrectly

Initial generation compiles candidates, separately generates drafting, attaches
the blocks, then validates/reviews the combined object. The independent reviewer
can withhold the whole recommendation for a defect in an optional drafting paragraph.
Run5's two withheld objects were explicitly criticized for drafting scope and
technical wording. Run6's site-list action was withheld because its drafting
presumed a resolution of inconsistent site counts. Its other rejection concerns
the underlying dividend/access proposal, so separating drafts would not establish
that all four actions are safe. Core decisions still require independent review.

### Confirmed correction contract defect

`CANDIDATE_SCHEMA` excludes all drafting fields and disallows extra properties.
The live compiler uses that strict schema. Correction invokes this same compiler,
but omits the drafting stage used in initial generation. For a confirmed document
route, `validate_recommendation` blocks a candidate without current-document wording
with `DRAFTING_CURRENT_MISSING`. Thus schema-shaped correction cannot pass that gate.
The unresolved-route exception does not apply to the saved run's available AF/IPF
drafting route.

Offline probe: retain only properties allowed by the native compiler in an otherwise
working correction fixture. Recovery becomes empty, `DRAFTING_CURRENT_MISSING` is
recorded, and only the first reviewer is called. Existing passing correction tests
supplied legacy drafting fields absent from the real transport schema. Quality6's
trace contains no second correction review, consistent with this defect, but its
missing raw correction response prevents attributing that historical failure with
certainty to this one cause.

Recommended contract: an operational decision has its own source, relevance,
residuality, materiality, feasibility, timing and semantic gates. Optional proposed
wording has separate target/authority/scope/entailment gates. A wording defect cannot
silently erase an independently accepted decision. The reviewer identifies whether
the defect affects the core action, narrative, current-document draft or instrument
draft. Corrections use the matching schema/compiler and retain independent re-review.
No rejected core action is restored to reach a count.

## 2. Native Summary uses a lexical gate as a factual gate

All six native Summaries fell back. Failures included sentence-opening recognition,
the now-removed four-rating-label requirement, and ordinary words such as work,
concrete and points. The present quality6 Summary still fails on points.

Offline probe: all three actual quality6 paragraphs pass the existing analytical
paraphrase controls, but the strict Summary rejects vocabulary absent from the
canonical register. A second probe reverses a supported assertion while using only
words present elsewhere in the canonical text; the strict lexical gate accepts it.
This proves that word overlap is neither a sufficient truth check nor a suitable
test of flowing prose. It does not establish that every rejected native paragraph
is factually correct.

The Summary is also generated before final recommendation admission/review. It can
describe prospective priorities that do not survive. The reader must be grounded
in the final accepted decisions and evidence, not a pre-review list.

Recommended contract: prose may paraphrase. Paragraph/claim references bind to known
facts, findings and accepted action IDs; deterministic checks retain identifiers,
numbers, dates, named entities and scope controls. Semantic review checks meaning,
including negation, planned/completed status and inference. Length and preferred
phrasing are editorial constraints, not evidence of truth. A reader defect is
repaired or falls back to approved prose without reducing the count of valid actions.
Fallback must remain readable and explicitly limited; it must not revive the old
four-dimension label-and-colon recap.

## 3. Research reconstructs proof through generative text

Quality6 search returned citations on both attempts. Each structuring response
reported four sources/five claims, but verification retained one source/one claim;
the two-source gate failed. The final failed bundle then contained no admitted
sources/claims. Therefore the observed failure is after retrieval, not simply an
absence of web-search results. Exact per-claim historical rejection causes were
not retained, so paraphrase, wrong URL, overlong excerpt and unsupported quantities
cannot be distinguished retrospectively.

The pipeline asks a second model to write a short exact source excerpt, its URL
and a claim, then checks whether that generated excerpt occurs in provider citation
passages. This is an unnecessarily fragile way to copy proof already available in
provider fields. Source packing also keeps one excerpt per URL within a four-source
cap, which can omit complementary passages useful for a regional operation.

Recommended contract: normalize provider citations directly into immutable source
and passage IDs. Preserve multiple useful passages per source within the existing
budget. Models select passage IDs and write separately labelled project implications;
they do not regenerate the quote or URL. Evidence, interpretation and project
application remain distinct. Verify relevance and geographic attribution as well
as provenance. Keep valid evidence when overall coverage is insufficient, with
explicit coverage limits; never describe a one-source result as complete research.
Plan coverage separately for Burundi and DRC. A country bank that does not support
a regional lookup is an availability limitation, not proof of an invalid manifest.

The provider documents response citations and the need to preserve encrypted search
blocks when continuing a search conversation. Strict JSON and native citation
output have compatibility constraints, reinforcing the case for separating evidence
normalization from generated editorial output. [Web search documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool),
[structured output documentation](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).

## 4. Coverage and scope need an explicit decision inventory

The same source supports climate-smart agricultural/post-harvest assistance through
Component3. Run5 retained a grant-access gap; run6 credited this response but did not
retain an equivalent residual decision, while its gap slots included document
counts, accounting and missing terminology/mechanism descriptions. Changing the
minimum recommendation count alone would not solve this selection problem.

Before ranking, map funded activities to climate-FCV pressures, existing responses,
remaining decisions/opportunities, available instruments, and evidence strength.
Document inconsistencies/accounting checks stay in04 unless they entail a material
design or delivery decision. Conditional dividends are assessed through plausible
mechanisms and enabling conditions, not whether a document uses peace/dividends terms.
Credit existing measures and distinguish an undocumented detail from a confirmed
omission. Do not impose an ideal-project requirement on every operation.

For this case, the offline benchmark should examine three distinct decision areas:

1. Climate/conflict-sensitive feasibility, siting and fair access at the new sites.
2. Delivery contingencies for security, time and funding constraints affecting
   climate-resilient investments.
3. Whether existing climate-smart grant/support arrangements can better support
   exposed trader associations while avoiding exclusion.

The third is a source-backed area to assess, not an automatically approved new
recommendation. It must demonstrate a material improvement beyond the documented
competitive scheme, respect its current status and meet the same admission gates.
The two existing accepted decisions are useful references, not automatic acceptance
of future revised wording. Fewer actions can be appropriate for a sparse concept
document; this Great Lakes case needs an explicit explanation if fewer than three
material decisions genuinely remain.

The saved context identifies AF/IPF, a PID source marker and an unresolved OIS/
processing regime. Keep source genre, operation family and preparation regime
distinct when selecting an optional drafting target. Never infer the new regime
from the filename or the PID's July date, or invent a formal review requirement.

## 5. Verification and cost controls

Large passing suites masked a runtime schema mismatch because fixtures supplied
fields live outputs cannot contain. Add actual-schema-shaped transport tests and
saved-output replays to the acceptance set. Track rejection reasons per component
and preserve pre-normalization responses separately from enriched reader objects.
Raw replies/source material remain outside Git and public logs.

Quality6's manifest has empty token usage and configured rather than actual model
aliases. Its latency map aggregates stage names; it does not make each correction
attempt and its cost independently visible. Record call count, actual model,
input/output tokens, latency, and retry/repair scope. Do not assert cost savings
until measured. Corrections must share the original wall-clock/token budget; no
unbounded retries or hidden extra generation to fill a quota.

The JSON client also applies one thinking-off policy to extraction, analysis,
recommendation generation and independent review. Its comment treats all stages
as mechanical JSON extraction. That configuration is a quality question to evaluate,
not a demonstrated cause of these failures. Pure copying should be deterministic;
analytical stages need an explicitly chosen reasoning/cost policy. Structured output
can coexist with thinking, according to the [provider documentation](https://platform.claude.com/docs/en/build-with-claude/structured-outputs). Assess stage
budgets after repairing the contracts; simply enabling more expensive reasoning
would not resolve the missing-drafting schema defect.

Historical diagnostics are incomplete: quality6's review-input snapshot is truncated,
and its candidate snapshot includes drafting added after generation. Preserve
pre-normalization transport separately from enriched candidates, plus exact rejection
reasons. This is needed for faithful replay, not extra public logging of document text.

## Options

| Option | Benefit | Limitation |
|---|---|---|
| Repair individual gates and prompts | Smallest immediate diff | Leaves action/draft coupling and generative reconstruction of evidence |
| Rebuild these backend boundaries, preserving the reader and evidence contracts | Addresses demonstrated causes and preserves the improved brief | Requires schema-realistic fixtures and staged migration |
| Replace the verified pipeline with a normal-FCV-style generation route | Fewer specialist contracts | Requires rebuilding provenance/review safeguards and creates a wider parity/regression surface |

Recommend the second option. A whole-app rewrite is not supported by the evidence.
The work is a targeted redesign of decision/artifact validation, research ingestion
and final reader compilation, with the current UI, scales, policy routing and
source guards retained. The immediate correction-schema bug must be resolved within
that redesign; adding repeated paid retries to its current path cannot fix it.

## Proposed checkpoints before another paid run

1. Core decisions, optional artifacts and corrections: schema-realistic tests show
   a draft-only failure preserves an independently passed core action; an unsafe
   core action remains withheld; a corrected artifact reaches the correct reviewer.
2. Source ingestion and reader: citation-ID tests preserve exact provenance,
   regional coverage limits and measured quantities; reader tests allow ordinary
   prose but reject unsupported/inverted assertions and align Summary to final actions.
3. Offline Great Lakes decision inventory and replay: independently assess distinct
   feasible decisions, including grant/support coverage; repeat with sparse concept,
   unknown-OIS/new/legacy preparation and unsupported-instrument cases. Demonstrate
   useful warnings and graceful partial output without inventing facts or actions.
4. Freeze one candidate and review its diagnostics, exports and measured budget.
   Only then request authorization for one fresh end-to-end quality run. Acceptance
   requires coherent prose, at least three supported priorities for this case,
   usable geographically attributed research, successful meaning-based Summary
   validation, paired scales, all-open priority cards and correct HTML/Word exports.

## Local evidence

- `output/20261013-readiness-case-inventory.json`: six saved-run diagnostics.
- `output/20261013_readiness_contract_probes.py` and corresponding JSON: deterministic
  correction and Summary reproductions; no provider calls.
- Original paid sessions and reports remain untouched under `output/playwright`.

The proposed backend is not yet implemented. No additional paid run is authorized
or used. UI implementation/verification evidence is recorded separately below.
