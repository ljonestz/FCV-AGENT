# Global country bank: routine-use activation and supplementary research

Status: implemented and offline-verified on
`feat/global-country-bank-depth-20261026`. Both PRs remain draft; not merged or deployed.

## Authority and meaning of approval

On 27 October 2026 Lindsey asked that the bank be used routinely and activated,
while retaining the app's own web research for updates and information missing
from the bank. This authorizes qualified routine-use approval of all 146 remediated
banks. It supersedes the earlier instruction to leave every bank unapproved.
Draft PRs remain draft. Deployment, hosted configuration changes, merging and
paid/live model assessments remain outside this work.

Routine-use approval is not independent verification of every source. The
preceding remediation checked 74 evidence records and one pathway at claim level.
The other 2,569 evidence records and 240 pathways retain their stated limitations.
All 146 whole-bank audit dispositions remain `unresolved-limited`. Source assertions,
programme intent and projected results remain distinct from evaluated effects.
The dated remediation results and original independent-review adjudications remain
historical records; this note records the subsequent activation decision.

The [remediation results](20261027_global-country-bank-remediation-results.md)
record the source adjudications and reproducible candidates. The bank's
`reviews/20261027_remediated-country-ledger.json` covers every country;
`research/20261027_remediation/audit/<ISO3>.json` inventories inherited records
and verification limits. Approval provenance and original/new hash bindings are
in `reviews/20261027_global-production-approval-manifest.json`. The activation
method and reproduction commands are in `research/20261027_activation/README.md`.

## Release and review dates

The normal pinned runtime is `2026.10.27.approved-global-country-bank`,
schema 1.1.0, `candidate=false`, with 146 country profiles, 2,643 evidence records
and 241 pathways. Separate `approved/2026.10.27` snapshots record Lindsey Jones's
qualified routine-use approval. Original drafts, previous approved country files,
source text, confidence, uncertainty, scenarios and evidence deadlines are preserved.
Only exact generic profile sentences about pending approval are corrected in the
new copies; independent source-verification limits remain explicit.

Country review dates use the earliest existing structural-evidence deadline in
each bank: July–October 2027. The 429 current-context records keep their own shorter
deadlines, beginning 10 November 2026. Expired evidence and pathways dependent on
it are omitted independently. There is no three-day expiry on this approved release.
The 30 October date belongs only to the earlier isolated unapproved test artifact;
it did not mean the underlying evidence became invalid on that day.

The exact old 24-country runtime is retained at
`releases/archive/2026.10.26.approved-country-bank/runtime.json`, with normalized-LF
SHA-256 `12f0a7b5c8267ec3a8ed8033f3e4716af69024a9290e023e5264a94ed35ebda8`.
The original 878-entry freeze manifest remains unchanged. Legitimately replaced
frozen code/schema/test files have exact archived originals and old/new hash
bindings in the new approval manifest; all other frozen paths still match in place.

## What web research does

With the Climate-FCV lens selected, the code default is live research. Stage 1
selects the bank first, then runs core research (or its existing six-hour cache)
and a separate Climate search. The Climate search receives bounded bank coverage,
known gaps and dated-source scope so it can seek updates and supplementary local
information. It retains the existing two-search budget, trusted-source gate,
keepalives, error handling and spend controls. Research supports the current
assessment and does not automatically write claims back into the bank.

Failure to obtain admissible research degrades to available bank evidence with a
visible limitation. Explicit `CLIMATE_RESEARCH_MODE=bank_only` suppresses both
providers and cached live context when the Climate lens is active. Normal FCV
research retains its existing behaviour. Structural tests with fake providers
prove routing and prompt construction; they do not establish live search quality.

A read-only health check of `https://fcv-agent.onrender.com/health` on 27 October
2026 returned build `6f3d5e65e213` and `climate_research_mode=bank_only`. Therefore
the existing hosted service was not performing Climate live searches. This branch
neither changes that setting nor deploys the new bank. A separately authorized
rollout must deploy the intended immutable app/bank pair and enable live research.
If the pilot spend guard prohibits tools, use its existing approval workflow
before supervised live testing. Its controls remain unchanged.

## Reproduction and supervised testing

From the bank checkout, the new activation script builds separate approved
snapshots and the profiled runtime from the exact remediated candidates. Its
manifest records the approval scope, inputs, profile wording changes, review-date
rule and preserved historical identities. Run its documented nonpublishing check
before considering a new release; do not renew source dates by rerunning approval.

From the app worktree after initializing its pinned submodule, run these checks
in a normal-permission shell on managed Windows:

```powershell
git submodule sync --recursive
git submodule update --init --recursive
# Clear any CLIMATE_COUNTRY_BANK_PATH and CLIMATE_COUNTRY_BANK_PREVIEW overrides.
python -m scripts.check_approved_country_bank
python -m pytest tests/test_climate_bank_global_activation.py tests/test_climate_research.py -q
```

The offline checker exercises normal startup, every country/name/alias and all
146 countries across Agriculture, Water and Urban development. It checks the
actual merged prompt, whole qualifiers, source support, complete pathway closure,
coverage/gaps and the unchanged 6,000/12,000 character budgets. It makes no provider
calls. The earlier unapproved test launcher remains a separate explicit opt-in.

For a later authorized supervised model test, clear preview/path overrides and
confirm `/health` reports the intended build and `live` research mode. Inspect any
spend controls before starting. Select the Climate-FCV lens and use the documented
Somalia recent-IPF PDF. Follow with Tuvalu Urban for projection/mobility
qualifications, Chad Water for floodplain/settlement scope, and PNG Agriculture or
Water for Hela/Carteret separation and expected-reach wording. Run Smoke before
Quality within the separately agreed budget. Save assessment IDs and inspect
admitted source URLs/dates, source excerpts, bank/research provenance, omitted stale
records and failure disclosures. Check supplementary information is project-specific
and supported, rather than treating a successful search request as analytical
acceptance. Verify Summary, a non-first priority, Detailed HTML and DOCX against the
preserved Word design. These model/browser/export checks have not been run here.

## Release identity and verification

The bank commit is `daf594f8ca899a44bcea4e057a85b0d547ed9c33`, pushed before
updating the app submodule pin. Both existing PRs remain draft.

The approved runtime has normalized UTF-8/LF SHA-256
`5a07c67eefc8ac9e509a7109df75d0789f3575a6efe8b156ccaabaac6d307461`,
and source-manifest checksum
`e72a1c766cedcd8e6a8eefa2a040afca082d34eff4a0f596e97e73fd11daf4bf`.
It references 1,045 sources; the 1,096 source definitions in the country snapshots
include 51 definitions not referenced by runtime evidence. The normal producer
retains only referenced sources.

Independent comparison with the unchanged 146-country draft test artifact matched
all 2,643 evidence records and 241 pathways after approval metadata and established
canonical citation/support ordering. Every evidence deadline is identical. All
146 profile pairs differ only by the two exact generic approval-notice prefixes;
other profile text and coverage remain identical. Country review dates match the
earliest original structural deadline in every case. The seven deliberately replaced
frozen paths have archived originals; the other 871 frozen paths remain in place.
The original freeze manifest and approval records remain unchanged.

Offline research checks passed: 67 research tests and 24 grounding, conflict and
handoff tests. They cover unset-mode bank plus both research providers, explicit
bank-only refusal to use providers or cached live context, whole-row budget-edge
trimming, current-date instructions and profile gap/date scope. Fake providers were
used throughout. A real-packet Agriculture audit covered all 146 draft countries:
every search context retained dated scope, coverage and known gaps within 2,500
characters; later omitted profile rows were marked as truncated.

The final default-startup checker passed against the actual pinned submodule:
146 countries, 344 unique country/name/alias identifiers, 438 final merged prompts
and 438 supplementary search contexts, with zero provider calls. All contexts
retained dated scope, coverage and known gaps within 2,500 characters. All bank-only merged
prompts preserved retained claim qualifications and complete pathway support within
the 6,000/12,000 character boundaries; separate grounding tests cover combined
budget-edge trimming. An independent explicit-bank-path run of the
same checker also passed against the identical runtime SHA.

Bank verification: the full offline suite reported 701 passed and one historical
IDA freeze assertion failure. That assertion still expected deliberately archived
code at its live path. The resolver now checks the unchanged original manifest
against its exact old archive plus the approval manifest's new live hash. The
subsequent eight focused checks passed, including all 505 IDA and 878 global frozen
identities, old-release reproduction, complete new-release reproduction and exact
canonical approval-manifest equality, approval-copy preservation and collision
preflight. No second full bank-suite run was performed.

The two activation/deployment test files initially produced 31 passes and one
failure. Inspection found two inaccurate expectations in the final-prompt test:
it required a redundant administrative approval row despite explicit whole-row
truncation, and guessed the phrase "report-level" for a pathway whose canonical
uncertainty instead specifies the dated national scope and absence of a named-site
causal estimate. The corrected test keeps the substantive disclosure mandatory,
requires honest truncation, and checks exact canonical pathway uncertainty plus
its causal-limit and non-threat wording. That test passed on rerun; production
code and prompt budgets were unchanged.

The first full app run was mistakenly started inside the sandbox: 1,875 passed,
two skipped, four deselected and 115 setup errors in 392.00 seconds. The setup
trace is `PermissionError: [WinError 5]` when pytest's `tmp_path` fixture scans its
Windows Temp directory. The identical command was rerun with normal process
permissions; this is an environment prerequisite rather than a product fix.

The normal-permission full app suite exited 0: **1,990 passed, two skipped, four
deselected in 374.10 seconds**. It used the offline command recorded in the
[remediation results](20261027_global-country-bank-remediation-results.md), with
only the four documented Chromium hangs excluded: exported disclosure printing,
phone stage-tab overflow, phone download-header wrapping and phone session-bar
wrapping. These exclusions are not a browser acceptance pass. No real model or
research-provider assessment was run. The staged scope, immutable submodule pin,
whitespace and sensitive-pattern checks passed.

The Word exporters, style module, logos, sample fixtures and render tests match
Word-design commit `3ab33b598492f8f9ee8882d094b00ee2dfa453a3` exactly. Approved
integration ancestor `7aee6406dcb92ba4573267bccbc5f3f43ff89786` remains in the branch.
The user checkout on `feat/word-readout-redesign` and its unrelated work are preserved.
