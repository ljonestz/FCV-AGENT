# Climate-FCV Country Bank and Runtime Grounding Handover

**Date:** 2026-07-31
**Purpose:** Restart-safe handover for a new Codex session
**Application:** FCV Project Screener v9.23, Render/Flask build
**Application branch:** `feat/climate-country-bank`
**Runtime implementation head before this handover commit:** `0f4eeaa`
**Draft application PR:** [ljonestz/FCV-AGENT#59](https://github.com/ljonestz/FCV-AGENT/pull/59)
**Live service:** <https://fcv-agent.onrender.com>
**Companion bank repository:** <https://github.com/ljonestz/climate-fcv-country-bank>
**Companion pin:** `96e80d6` on `origin/feat/south-sudan-pilot`

## 1. Executive status

The Climate-FCV country-bank architecture and runtime integration are implemented,
tested, pushed, and deployed. A real South Sudan PCN completed all three Express
stages after a production Stage 2 truncation defect was fixed. Lindsey has also
completed a full browser run and reports that it ran through properly; substantive
feedback on the output is the first topic for the next session.

The system is not yet using the South Sudan bank in production. The South Sudan
package is deliberately `reviewed`, not `approved`. There is therefore no
`releases/current/runtime.json`, and current production runs correctly report
`research-only` or, if live research is unavailable, `thematic-only`. This is an
expected approval-state limitation, not a deployment bug.

The next session should not redesign the architecture or generate the full country
bank. It should:

1. collect and address Lindsey's feedback on the successful South Sudan output;
2. review the South Sudan dossier, evidence records, pathways, and source balance;
3. decide what must change before approval;
4. approve and materialize the South Sudan runtime release only after explicit
   human sign-off; and
5. run one `bank-only` and one `bank+research` production acceptance test before
   expanding to other countries.

## 2. Repository, branch, and deployment state

### 2.1 FCV-AGENT

| Item | Current state |
|---|---|
| Worktree | `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\climate-country-bank` |
| Branch | `feat/climate-country-bank` |
| Base | `feat/climate-readout-redesign` at `13ce1a7` |
| Runtime head | `0f4eeaa fix: prevent climate stage 2 truncation` |
| Remote tracking | `origin/feat/climate-country-bank` |
| Draft PR | <https://github.com/ljonestz/FCV-AGENT/pull/59> |
| PR base | `feat/climate-readout-redesign`, not `main` |
| Render branch | `feat/climate-country-bank` |
| Render live commit | `0f4eeaa` at final acceptance |
| `main` | Intentionally untouched by this work |

Render originally remained on `feat/climate-readout-redesign`, which is why the
latest country-bank updates did not appear. The service branch was changed in the
Render dashboard to `feat/climate-country-bank`, and subsequent commits now
auto-deploy from that branch.

### 2.2 Companion bank repository

| Item | Current state |
|---|---|
| Repository | `ljonestz/climate-fcv-country-bank` (public) |
| Root path | `data/climate-fcv-country-bank` Git submodule |
| Pinned commit | `96e80d6 data: draft South Sudan climate fcv evidence package` |
| Source branch | `origin/feat/south-sudan-pilot` |
| Checkout state | Detached HEAD, expected for a pinned submodule |
| South Sudan status | `reviewed` |
| Approved release | None |
| Runtime file | `releases/current/runtime.json` intentionally absent |

The root `.gitmodules` points to:

```text
https://github.com/ljonestz/climate-fcv-country-bank.git
```

The application can instead use `CLIMATE_COUNTRY_BANK_PATH`, pointing to the
companion repository root or directly to a `runtime.json`. The default remains the
pinned public submodule.

### 2.3 Private parity record

The shared-contract changes were recorded locally in:

```text
C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md
```

That file is private and intentionally not committed. ITS/FastAPI implementation
remains deferred.

## 3. Objectives and user decisions carried into the implementation

The implementation reflects the following decisions from the design discussion:

- Build a structural country bank and keep current/project-specific research as a
  separate live layer.
- Give the greatest analytical weight to qualitative vulnerability, adaptive
  capacity, institutions, sectors, livelihoods, services, displacement, resource
  access, and mediated Climate-FCV pathways.
- Treat detailed physical-climate projections as supporting evidence rather than
  the centre of the assessment.
- Prioritize direct Climate-FCV and trusted country analysis from sources such as
  UN entities, CCDRs, government climate plans, Weathering Risk/adelphi, SIPRI,
  ODI, SEI, CGIAR, International Alert, ICG where relevant, and trusted NGOs and
  humanitarian sources.
- Use model assistance for extraction, classification, and summarization, but
  never cite model general knowledge as evidence.
- Select project-relevant bank content dynamically, but use deterministic local
  selection in version 1 rather than a required runtime curator-agent call. This
  avoids another provider call, extra latency, and another failure point.
- Always attempt live research for current, subnational, and project-specific
  enrichment, but never let its failure terminate an otherwise valid assessment.
- Keep the bank public. Privacy is not required because it contains public-source
  structured summaries and citations, not confidential project material or raw
  copyrighted documents.
- Build and validate South Sudan first. Do not generate the full multi-country bank
  until the pilot's content, balance, and runtime usefulness are reviewed.
- Preserve the dedicated climate-native Stage 2 route. Do not recreate the generic
  12-OST, DNH-9, and 25-question engine inside Climate mode.
- Keep `main` and the ITS-compatible baseline untouched until there is a separate
  integration decision.

The earlier brainstorming idea of a video or a generated long readout is not a
runtime feature. The implemented review artifact is the structured South Sudan
dossier generated from traceable records. A video was not produced.

## 4. What was implemented in FCV-AGENT

### 4.1 Versioned bank loader

**Primary file:** `sector_lenses/climate_bank.py`

The loader:

- resolves the default pinned submodule release or
  `CLIMATE_COUNTRY_BANK_PATH` override;
- reads schema `1.0.0` runtime releases only;
- validates release structure, checksums, compatibility, country code, approval
  state, and review window;
- materializes only approved records and pathways;
- rejects unsafe paths, malformed IDs, invalid URLs, cross-country references,
  duplicate normalized URLs, and invalid source/evidence/pathway links; and
- returns typed nonfatal states such as `bank_missing`, `bank_incompatible`,
  `bank_content_expired`, and `bank_manifest_invalid`.

Missing or invalid bank content never terminates the Climate assessment.

### 4.2 Deterministic project-relevant selector

**Primary file:** `sector_lenses/climate_bank_selector.py`

The selector uses already-extracted project signals, including country, sector,
instrument, components, locations, affected groups, institutions, systems/assets,
resources/livelihoods, climate signals, time horizon, and priority points. It:

- supports the single-country South Sudan pilot;
- returns `bank_scope_unsupported` for multi-country/regional operations and
  continues without bank grounding;
- prioritizes direct geography, component, sector, group, institution, system, and
  mediator matches;
- favors direct Climate-FCV and vulnerability/capacity evidence over generic
  physical-baseline evidence;
- preserves source and pathway diversity;
- targets 8 selected items and caps the set at 12;
- caps the compact bank packet at 6,000 characters; and
- uses stable IDs for deterministic tie-breaking.

It adds no runtime model call and does not rewrite approved evidence statements.

### 4.3 Grounding merger

**Primary file:** `sector_lenses/climate_grounding.py`

The merger combines selected bank records with accepted live research while:

- retaining bank and live provenance separately;
- removing exact duplicates;
- preserving conflicting findings as uncertainty rather than silently choosing one;
- preferring accepted live evidence for genuinely current facts;
- keeping structural vulnerability/capacity evidence from being displaced by live
  search;
- allowing at most 6 live claims;
- enforcing a 12,000-character combined grounding boundary; and
- emitting one of four states:
  `bank+research`, `bank-only`, `research-only`, or `thematic-only`.

### 4.4 Workflow integration

**Primary file:** `app.py`

Both Express and Step-by-Step routes now:

1. extract the existing country, sector, instrument, and project signals;
2. resolve and select the local bank before live research;
3. always attempt bounded live Climate research;
4. treat search timeout, empty results, provider overload, or validation failure as
   nonfatal;
5. merge the available evidence into one bounded canonical grounding packet;
6. pass that packet to the existing dedicated climate-native Stage 2 prompt; and
7. carry display-safe provenance metadata into Stage 2, Stage 3, live output, and
   exports.

Canonical source and evidence IDs are rematerialized server-side. Browser-supplied
bank records, source labels, or approval metadata are not trusted.

### 4.5 Climate-native prompt grounding

**Primary file:** `sector_lenses/climate_native.py`

The existing native prompt now receives one external-grounding data block with:

- the actual grounding state;
- approved bank evidence and accepted live claims where available;
- observed, projected, and inferred labels;
- pathway-strength and uncertainty labels;
- strict source-ID rules; and
- an explicit untrusted-data boundary preventing evidence text or user priority
  points from changing the prompt contract.

It retains conditional causal language and the advisory boundary. Co-occurrence is
not converted into a climate-conflict causal claim, and analytical sources are not
presented as OPCS policy authority.

### 4.6 Provenance in UI and exports

**Primary files:** `index.html` and `app.py`

Live HTML, shared HTML, and DOCX now show matching provenance notices:

- `bank+research`: reviewed country evidence plus accepted current research;
- `bank-only`: reviewed bank evidence, with a warning that recent/local changes may
  be missing;
- `research-only`: no reviewed bank release, accepted live research used; and
- `thematic-only`: neither reviewed bank evidence nor accepted live research was
  available.

DOCX generation rematerializes canonical server-side grounding from the manifest.
It cannot accept a forged browser-supplied reviewed source or grounding state.

### 4.7 Documentation and deployment contract

Updated tracked documentation includes:

- `README.md`;
- `claude.md` version entry v9.23;
- `docs/reference/reference_backend_routes.md`;
- `docs/reference/reference_prompt_architecture.md`; and
- `docs/reference/reference_sector_lenses.md`.

`pytest.ini` prevents the root Flask suite from accidentally collecting the
companion repository's independent test suite. The two suites are run separately.

## 5. What was implemented in the companion bank repository

The companion repository provides:

- JSON schemas for sources, evidence, pathways, review records, and runtime
  releases;
- deterministic schema and cross-reference validation;
- safe repository-path and URL checks;
- deterministic approved-only release generation;
- deterministic country dossier generation;
- CLIs under `scripts/validate_bank.py`, `scripts/build_release.py`, and
  `scripts/build_dossier.py`;
- repository-contract, validation, release, dossier, and South Sudan content tests;
  and
- the South Sudan pilot package under `countries/SSD/`.

### 5.1 South Sudan package

| Artifact | Current count/status |
|---|---:|
| Registered sources | 12 |
| Atomic evidence records | 19, all `reviewed` |
| Mediated pathways | 7, all `reviewed` |
| Direct pathways | 3 |
| Triangulated pathways | 3 |
| Analytical-inference pathways | 1 |
| Country review status | `reviewed` |
| Reviewer label | `Codex-assisted draft for Lindsey review` |
| Review date | `2026-07-30` |
| Approved records/pathways | 0 |
| Current runtime release | None |

The package files are:

- `data/climate-fcv-country-bank/countries/SSD/sources.json`;
- `data/climate-fcv-country-bank/countries/SSD/evidence.json`;
- `data/climate-fcv-country-bank/countries/SSD/pathways.json`;
- `data/climate-fcv-country-bank/countries/SSD/review.json`; and
- `data/climate-fcv-country-bank/countries/SSD/dossier.md`.

The dossier and structured records cover flood and drought exposure, livelihood
and food-system vulnerability, displacement and return dynamics, pastoral mobility
and resource access, service and infrastructure disruption, institutional capacity,
community resilience, conflict-sensitive adaptation, and both directions of the
Climate-FCV interaction. The next session must still assess whether the source mix,
locators, nuance, and pathway framing are good enough for approval.

## 6. Major architectural and methodological decisions

### 6.1 Rich research and compact runtime context are separate products

The 8-12 page dossier is for human review. It is never injected into the model. The
runtime receives only a small set of approved, project-relevant records. This avoids
recreating the context-window and attention problems the bank was intended to solve.

### 6.2 Two independent source dimensions

The bank evaluates:

1. source quality and traceability; and
2. the analytical role a source can support.

A high-quality physical-climate source may support the pressure link without
supporting the FCV mediator or consequence. Rankings such as ND-GAIN and INFORM can
orient inquiry but do not establish a causal pathway.

### 6.3 Evidence priority

The analytical priority is:

1. direct Climate-FCV evidence;
2. vulnerability, capacity, institutions, groups, sectors, and services; and
3. the supporting physical-climate baseline.

Physical-baseline records may occupy no more than two of twelve runtime slots when
more relevant Role A or Role B evidence is available.

### 6.4 Causal discipline

Every pathway must distinguish climate pressure, documented impact, mediator,
affected group/institution/system, possible consequence, alternative explanations,
resilience factors, uncertainty, and source support. `analytical-inference` pathways
must remain conditional and cannot be presented as established causality.

### 6.5 Human approval is a hard release boundary

Models may prepare a candidate dossier and structured evidence. They cannot approve
it. Only records and pathways explicitly marked `approved`, within the approved
country review window, enter a production release.

### 6.6 Live research is enrichment, not a gate

This is the central reliability decision. The application should always attempt live
research, but a failed or empty pass produces an honest provenance warning rather
than suppressing the Climate assessment.

### 6.7 Deterministic selector before a curator agent

The original idea of a Climate/conflict literature injector agent was retained in
function but implemented deterministically for version 1. The selector changes the
evidence packet based on the project context without using another LLM call. A model
curator can be evaluated later behind a feature flag, but must not become required.

### 6.8 Public companion repository

Public deployment was chosen because the inputs are public-source summaries and
citations. The bank does not contain raw project documents, secrets, API keys,
restricted OPCS material, or model self-citation. Raw PDFs are not redistributed
unless rights clearly permit it.

### 6.9 South Sudan first; broader bank deferred

No other countries should be generated until South Sudan's methodology, record
schema, review experience, selector behavior, and output usefulness are accepted.
The later comparison set should represent different FCV/climate archetypes, but the
specific countries have not yet been selected.

### 6.10 Stage 2 compact target with a 16,000-token safety ceiling

Commit `b102345` had reduced the Climate Stage 2 model ceiling from 16,000 to 8,000
tokens because the prompt asks for a compact payload. Two production South Sudan
runs reached exactly 8,000 tokens before the closing diagnostic delimiter, causing:

```text
Lens diagnostic block was not produced.
```

The fallback repair had only 4,500 tokens and, with no complete primary JSON, could
not reconstruct the full evidence-grounded assessment. Commit `0f4eeaa` restored the
16,000-token safety ceiling in both Express and Step-by-Step routes. The prompt still
targets a complete response within roughly 7,000 output tokens; the higher ceiling
is headroom, not a target. The successful retest used the headroom and completed
without recovery.

Do not restore the 8,000-token ceiling merely because the 2026-07-29 postmortem
recommended it. That recommendation is superseded by direct production evidence.

## 7. Verification evidence

### 7.1 FCV-AGENT automated verification

| Verification | Result |
|---|---:|
| Stage 2 truncation regression, red state | 2 expected failures at 8,000 tokens |
| Stage 2 truncation regression, green state | 2 passed at 16,000 tokens |
| Focused climate workflow/native/diagnostic/app contracts | 155 passed |
| Complete Flask application suite | 618 passed in 56.16 seconds |
| Worktree after runtime commit | Clean; local and remote both `0f4eeaa` |

The full suite must use a local Windows temp directory for pytest fixtures. Pytest's
Unix-style `0700` temp permissions can make OneDrive directories unreadable and
produce setup errors unrelated to application behavior.

### 7.2 Companion bank verification

Fresh verification on 2026-07-31 at pinned commit `96e80d6`:

```text
Climate-FCV country bank validation passed.
149 passed, 1 pytest cache warning
```

The warning is the same nonfunctional OneDrive pytest-cache permission issue.

### 7.3 Local South Sudan selector acceptance

Using the real South Sudan PCN and an in-memory approved fixture, the selector:

- returned 8 items;
- selected 6 direct evidence IDs and 2 pathway IDs;
- produced a 4,141-character compact packet; and
- selected material on flood/access disruption, host/displaced-community capacity,
  livelihood recovery, negotiated mobility/resource sharing, and conflict-sensitive
  flood response.

Nothing was approved or released by this fixture test.

### 7.4 Production South Sudan acceptance

The hotfix was deployed as `0f4eeaa`. The controlled production Express run used:

```text
assessment_id=ss-live-hotfix-1785503089404
```

Results:

| Stage | Evidence |
|---|---|
| Stage 1 | Completed; South Sudan detected; live research accepted; grounding state `research-only`; warning `bank_missing` |
| Stage 2 | Completed; 19,013-character rendered diagnostic; `parse_error=false`; diagnostic present; no recovery |
| Stage 3 | Completed; 3 priorities; no error events |

The run streamed beyond the previous 8,000-token failure point and completed all
three stages. Lindsey subsequently ran the app in the browser and reports that the
full workflow also completed properly. The substantive quality of that browser
output has not yet been reviewed in this handover and is the next-session priority.

## 8. What is live-proven versus still unproven

### Live-proven

- Render deploys the correct branch.
- The real South Sudan PCN can complete all three Express stages.
- The Stage 2 diagnostic can close, parse, render, and feed Stage 3 without recovery.
- Accepted live research produces `research-only` provenance when no approved bank
  release exists.
- Bank absence and live-research failure are nonfatal by contract.
- The standard application test suite remains green.

### Tested locally but not yet live-proven with approved data

- Approved-release loading from the public submodule on Render.
- `bank-only` production behavior.
- `bank+research` production behavior.
- Project-specific South Sudan selection from an actual approved runtime release.
- Visible bank source details in a production report.
- DOCX and shared-HTML provenance from a bank-backed live run.

### Not yet checked or intentionally deferred

- Lindsey's substantive output feedback.
- Live Step-by-Step bank-backed acceptance.
- Multi-country or regional bank selection; version 1 intentionally returns
  `bank_scope_unsupported` and continues without the bank.
- Broader country generation.
- ITS/FastAPI implementation parity.
- Merge strategy into `main`.

## 9. Immediate next-session work

### 9.1 Start with Lindsey's output feedback

Do not begin by changing the bank or prompt. First ask Lindsey to walk through the
successful output and identify what was too generic, missing, over-weighted,
incorrectly framed, or operationally unhelpful.

Review at least:

- whether the operating context is recognizably South Sudan-specific;
- whether vulnerability, capacity, institutions, sectors, livelihoods, displacement,
  and local conflict dynamics receive the intended weight;
- whether the two interaction directions are clear and appropriately conditional;
- whether strengths and weaknesses reflect the actual PCN;
- whether the core-question reflections add insight rather than repeat the document;
- whether the integration rating is justified;
- whether the three priorities are specific, actionable, instrument-appropriate, and
  timed to the project's current stage;
- whether cited sources and uncertainty are visible and credible; and
- whether the readout is concise enough for operational use.

Check the browser output and, if available, the downloaded DOCX or shared HTML. The
automated live run proved pipeline completion, not editorial quality.

### 9.2 Conduct the South Sudan country-bank review

Open:

```text
data/climate-fcv-country-bank/countries/SSD/dossier.md
data/climate-fcv-country-bank/countries/SSD/sources.json
data/climate-fcv-country-bank/countries/SSD/evidence.json
data/climate-fcv-country-bank/countries/SSD/pathways.json
data/climate-fcv-country-bank/countries/SSD/review.json
```

Review:

- source credibility, balance, and currency;
- whether direct Climate-FCV evidence and qualitative vulnerability/capacity evidence
  dominate appropriately over physical projections;
- exact page, section, table, or paragraph locators;
- whether evidence statements remain faithful to sources;
- whether affected groups, geographies, sectors, systems, resources, institutions,
  and time horizons are adequately differentiated;
- pathway mediation, alternative explanations, resilience factors, and uncertainty;
- whether `direct`, `triangulated`, and `analytical-inference` labels are justified;
- whether any material contrary evidence is missing;
- dossier balance and readability; and
- whether the compact statements are suitable for runtime injection.

Do not approve the package as a whole without inspecting the linked evidence and
pathway records.

### 9.3 Promote only after explicit approval

After Lindsey approves the content:

1. apply agreed edits in the companion repository;
2. set retained evidence and pathways to `approved`;
3. set the country review to `approved` with Lindsey as reviewer;
4. set a review date and review-due date;
5. add the South Sudan release acceptance test;
6. run `scripts.build_release` to create `releases/current/runtime.json`;
7. run validation and all 149+ companion tests;
8. commit and push the companion branch and open its PR;
9. update the FCV-AGENT submodule pin to the approved release commit;
10. run the FCV-AGENT bank and full suites;
11. push the application branch and let Render deploy; and
12. confirm that Render actually initializes the submodule, or configure
    `CLIMATE_COUNTRY_BANK_PATH` to a deployment artifact.

### 9.4 Run the two remaining live acceptance cases

After deployment of an approved release:

1. **Bank-only:** use a controlled test in which live research is unavailable. The
   assessment must complete, show `bank-only`, use approved South Sudan records, and
   display the amber current/local-evidence warning.
2. **Bank+research:** run the real PCN with live research. The assessment must show
   `bank+research`, preserve bank and research provenance, avoid duplicate/conflicting
   overstatement, complete Stage 2 without routine recovery, and produce grounded
   Stage 3 priorities.

For both runs, inspect live HTML and download DOCX/shared HTML. Stop after one failed
live verification and record the evidence before changing code.

### 9.5 Decide whether the PR can leave draft status

PR #59 should remain draft until:

- Lindsey's output feedback is addressed;
- the South Sudan bank is approved and released;
- the application pin points to that approved release;
- bank-only and bank+research live cases pass; and
- export provenance is visually checked.

The PR currently targets `feat/climate-readout-redesign`. A later maintainer decision
is required about whether and how the combined branch should reach `main`.

## 10. Known risks and watch items

### 10.1 `bank_missing` is currently expected

Do not treat production `bank_missing` as a new loader defect until an approved
`releases/current/runtime.json` exists at the deployed path.

### 10.2 Render submodule checkout must be verified after release

The default loader depends on the submodule being initialized during checkout. The
current research-only run cannot prove that Render will materialize an approved
release. Verify the deployed file path and bank version after updating the pin.

### 10.3 Live research remains stochastic

One earlier user run reached the research structuring output ceiling and degraded to
`thematic-only`; later runs accepted research. This no longer blocks completion, but
it can affect current/subnational richness. Do not reintroduce a mandatory research
gate. If quality is inconsistent, isolate and diagnose the research stage before
changing multiple limits or models.

### 10.4 Monitor Stage 2 output size

The 16,000-token ceiling fixed the observed South Sudan truncation. The compact
prompt target still matters. If a future run reaches 16,000 tokens, capture the stop
reason and payload structure before changing the cap. Do not rely on full-payload
recovery after a missing closing delimiter.

### 10.5 Context bounds are contractual

Do not inject the dossier or expand the bank packet casually. Preserve:

- target 8 / maximum 12 selected bank items;
- 6,000 bank characters;
- maximum 6 live claims; and
- 12,000 combined external-grounding characters.

### 10.6 Multi-country selection is deliberately out of scope

A correct multi-country selector needs budget allocation across countries and
cross-border pathways. Do not remove `bank_scope_unsupported` without a separate
design.

### 10.7 Public-source and copyright boundary

Continue storing citations, locators, compact derived statements, and permitted
local files only. Do not bulk-copy source text or commit raw PDFs without clear
redistribution rights.

### 10.8 Review freshness

Approved country content must have a review window. Stale content remains available
for research/review but must not silently enter a new production release.

### 10.9 OneDrive pytest permissions

When tests using `tmp_path` fail with `PermissionError` under OneDrive, use a fresh
local Windows temp path. Do not interpret those setup failures as application
failures.

### 10.10 Old plans and postmortems contain superseded instructions

- `docs/superpowers/plans/2026-07-30-climate-fcv-country-bank-reliability.md` is
  explicitly superseded and must not be executed.
- The 2026-07-29 postmortem's instruction to retain an 8,000-token Climate Stage 2
  ceiling is superseded by the July 31 live failure and hotfix.
- The current controlling design is
  `docs/superpowers/specs/2026-07-30-climate-fcv-evidence-bank-design.md`.
- The controlling implementation plans are the South Sudan pilot plan and runtime
  integration plan listed below.
- Their Markdown checkboxes were not updated as execution progressed. Use the branch
  commits and this handover as the implementation record.

## 11. Commit and file inventory

### 11.1 Application branch commits after the base

| Commit | Change |
|---|---|
| `25bf2cd` | Initial reliability/country-bank design |
| `58180fc` | Initial implementation plan |
| `95be93b` | Evidence-bank architecture redesign |
| `3592124` | Replacement implementation plans |
| `f46e030` | Versioned approved-release loader |
| `4769067` | Deterministic project-relevant selector |
| `1720b19` | Bounded bank/live grounding merger |
| `54eabc7` | Bank selection before live research |
| `ab39636` | Live research made nonfatal |
| `20673d6` | Climate-native prompt grounded in reviewed evidence |
| `0a07522` | Provenance in UI, shared HTML, and DOCX |
| `466a9cc` | Runtime/deployment documentation |
| `c53c0de` | Root/companion pytest isolation |
| `859e63f` | Grounding edge-case, security, and validation fixes |
| `0f4eeaa` | Restore Stage 2 safety ceiling after live truncation |

### 11.2 Principal application files added

```text
.gitmodules
pytest.ini
sector_lenses/climate_bank.py
sector_lenses/climate_bank_selector.py
sector_lenses/climate_grounding.py
tests/fixtures/climate_bank/runtime_v1.json
tests/test_climate_bank.py
tests/test_climate_bank_deployment_contract.py
tests/test_climate_bank_selector.py
tests/test_climate_bank_selector_realistic.py
tests/test_climate_grounding.py
tests/test_climate_grounding_conflicts.py
```

### 11.3 Principal application files modified

```text
README.md
app.py
claude.md
index.html
sector_lenses/__init__.py
sector_lenses/climate_native.py
sector_lenses/research.py
tests/test_climate_lens_frontend.py
tests/test_climate_native.py
tests/test_climate_research.py
tests/test_climate_workflow_contract.py
tests/test_sector_lens_app_contract.py
docs/reference/reference_backend_routes.md
docs/reference/reference_prompt_architecture.md
docs/reference/reference_sector_lenses.md
```

### 11.4 Controlling design and plans

Read in this order:

1. `docs/20260731_climate_country_bank_handover.md`;
2. `docs/superpowers/specs/2026-07-30-climate-fcv-evidence-bank-design.md`;
3. `docs/superpowers/plans/2026-07-30-climate-fcv-bank-pilot.md`;
4. `docs/superpowers/plans/2026-07-30-climate-fcv-bank-runtime-integration.md`;
5. `data/climate-fcv-country-bank/README.md`; and
6. `claude.md`, especially v9.23 and the repository commands.

Use `docs/20260729_climate_module_diagnostic_postmortem.md` only as historical
failure context. Its unresolved conclusions are not the current state.

## 12. Suggested new-session startup

```powershell
Set-Location "C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\climate-country-bank"
git status --short --branch
git log -8 --oneline --decorate
git submodule status
git -C data/climate-fcv-country-bank status --short --branch
git -C data/climate-fcv-country-bank log -3 --oneline --decorate
```

If the submodule is missing:

```powershell
git submodule update --init --recursive
```

Do not begin with a full test rerun unless code or bank content changes. The first
task is to collect output feedback. After changes, use:

```powershell
# Focused application contracts
python -m pytest `
  tests/test_climate_bank.py `
  tests/test_climate_bank_selector.py `
  tests/test_climate_grounding.py `
  tests/test_climate_workflow_contract.py `
  tests/test_climate_native.py `
  -q -p no:cacheprovider

# Companion repository
Set-Location data/climate-fcv-country-bank
python -m scripts.validate_bank
python -m pytest -q -p no:cacheprovider
```

For the complete Flask suite, use a fresh local Windows temp directory for
`--basetemp` if pytest reports OneDrive permission errors.

Suggested opening instruction for the next Codex session:

> Continue the Climate-FCV country-bank work from
> `docs/20260731_climate_country_bank_handover.md` on
> `feat/climate-country-bank`. First collect my feedback on the successful South
> Sudan output. Do not approve the bank, generate other countries, or change the
> architecture until we have reviewed that feedback and the South Sudan dossier.

## 13. Explicit stop and scope boundaries

- Do not approve South Sudan without Lindsey's explicit content decision.
- Do not generate the wider country bank yet.
- Do not merge to `main` or mark PR #59 ready yet.
- Do not weaken source traceability or causal-discipline checks to obtain a passing
  run.
- Do not make live research mandatory again.
- Do not add a required runtime curator-model call.
- Do not inject long dossiers into the runtime prompt.
- Do not apply bank selection to multi-country operations without a new design.
- Do not expose the private ITS parity document in the public repository.
- Stop after one failed live acceptance test, record the assessment ID and evidence,
  and diagnose before patching.

The implementation is now at the point intended for a South Sudan content and output
review. The remaining work is primarily evidence approval, editorial calibration,
and bank-backed acceptance, not another reliability re-architecture.
