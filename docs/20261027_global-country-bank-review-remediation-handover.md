# Climate-FCV country banks: full-bank review and remediation handover

Date: 27 October 2026. Audience: the next coding/research agent, working in a fresh session.

## Assignment and authority

Complete the review and remediation of all 146 Climate-FCV country banks, applying the lessons from the independent Claude review across the entire collection, including inherited evidence and pathways. Implement the necessary app changes so the model receives qualified, appropriately scoped evidence and understands coverage limitations. Produce a reproducible, unapproved test build, verify both repositories, and push the bank and app branches with their draft PRs updated.

The user explicitly authorized this scope and the handover on 27 October. Execute the work; do not return only another plan or stop after the four sample countries. Use judgment for routine, reversible implementation choices. Ask only for a material scope decision, missing authority, or a blocker that safe alternatives cannot resolve.

Excluded: human approval of country banks, merging PRs, production promotion or deployment, changing Render/ITS configuration, and paid/live model assessments. A local offline or mocked test build is authorized. Preserve the earlier Word document layout/design work. Keep all candidates draft and leave the approved production release unchanged.

This handover session changes documentation only. The findings below have not yet been implemented. The full Claude review, including the Tuvalu addendum, was received in the preceding conversation; its findings and subsequent verification are consolidated here so that conversation is not required.

## Start with the correct checkouts

Two separate repositories share a branch name. Push each to its own remote.

| Item | App | Country bank |
|---|---|---|
| Repository | `ljonestz/FCV-AGENT` | `ljonestz/climate-fcv-country-bank` |
| Local worktree | `C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT/.worktrees/global-country-depth-app-20261026` | `C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT/.worktrees/global-country-depth-bank-20261026` |
| Branch | `feat/global-country-bank-depth-20261026` | `feat/global-country-bank-depth-20261026` |
| Verified pre-handover HEAD | `0f5332b2e4c9bbbd2ba36c007c31f15be591088b` | `584c7673f7a11a730dcd94f9ff35a8b19394af30` |
| Stacked base branch | `feat/ida-country-expansion-20261026` | `feat/ida-country-candidates-20261026` |
| Base SHA | `206e0a510e68e171dc0994f8fad1b7c67f0fadf0` | `97dec8a6c5f94f3cc2c8df6e73f9aac51bbfa643` |
| Existing draft PR | [App PR 89](https://github.com/ljonestz/FCV-AGENT/pull/89) | [Bank PR 5](https://github.com/ljonestz/climate-fcv-country-bank/pull/5) |

Both PRs were open/draft with these heads and bases when checked on 27 October. A documentation-only commit may follow the app SHA above. Verify live state before editing; do not reset branches to these historical SHAs.

The Word redesign ancestor is `3ab33b598492f8f9ee8882d094b00ee2dfa453a3`; the approved-integration ancestor is `7aee6406dcb92ba4573267bccbc5f3f43ff89786`. Both belong in app ancestry. Verify with `git merge-base --is-ancestor <sha> HEAD`. Retain the stacked bases unless the user explicitly changes integration strategy.

The root checkout is on `feat/word-readout-redesign` and contains unrelated user work. Do not edit, reset, clean, stage or commit there. In particular, leave its accidental untracked `research/20261026_global_depth/phase1/{AFG,BDI,BEN}.json` copies alone. Correct copies are in the bank worktree. The bank worktree also has an unrelated zero-byte untracked file named `0))`; exclude it, and do not attempt a cleanup workaround.

Read the applicable `AGENTS.md`, app `claude.md`, `HANDOFF.md`, and relevant designs/plans before implementation. Check `C:/Users/wb559324/.claude/codex_skills.prompt.md` for current instructions. Read the private parity contract specified by local instructions before touching a shared Render/ITS contract; do not copy its contents into the public bank repository. Follow applicable implementation, review, TDD and verification skills.

Use the existing isolated worktrees on this workstation. In a cloud/browser coding session, clone/check out the corresponding branches and initialize the submodule; the Windows paths are references, not required locations. Never assume the app repository contains the bank's editable branch: the app's bank is a pinned, detached submodule.

## Existing scope and source of truth

The explicit roster is 146 countries: 84 existing banks deepened and 62 additional FY27 IBRD borrowers. It comprises 78 IDA countries, including 19 blend countries, 67 IBRD countries and retained PSE. Lending eligibility is not an FCV classification. Do not expand to every IBRD member or silently change the roster.

Roster source: [World Bank country and lending groups](https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups). Preserve the recorded roster vintage; record any subsequent classification change separately.

Bank paths, relative to the separate bank repository:

- `countries/<ISO>/candidates/2026.10.26.deep/`: `sources.json`, `evidence.json`, `pathways.json`, `profile.json`, `review.json`, `dossier.md`.
- `research/20261026_global_depth/TARGET_COUNTRIES.json`: the 84 base directories and 62 additions.
- `research/20261026_global_depth/TEST_INPUTS.json`: the exact 146 candidate directories. Use this manifest, not discovery of all historical versions.
- `research/20261026_global_depth/EXTRACTION_CONTRACT.md`, `README.md`, `EXISTING_COUNTRIES.json`, `COUNTRY_ALIASES.json`.
- `research/20261026_global_depth/phase1/<ISO>.json` and `phase2/<ISO>.json`: research intake; `decisions/<ISO>.json` and `assembly/<ISO>.json`: decisions and assembly trace.
- `reviews/20261026_global-depth-baseline-freeze.json`: 878 frozen files from the bank base, hashed as UTF-8 text with normalized LF.
- `reviews/20261027_global-depth-approval-table.md` and `20261027_global-depth-review-manifest.json`: all-country counts, file identities and pending approval.
- `scripts/assemble_depth_candidates.py`, `import_research_packets.py`, `build_dossier.py`, `validate_bank.py`, `build_test_bundle.py`, `build_release.py`: inspect actual interfaces before selecting an implementation.

Baseline counts are 2,639 evidence records and 240 pathways; the expansion added 1,716 evidence records, including 1,037 named-local records, and 58 pathways in 54 countries. Eighteen new reverse/bidirectional pathways cover 18 countries. All 146 have at least one named-local addition. There are 1,094 source metadata records, 1,043 referenced sources, and 351 low-confidence new evidence records. These are inventory counts, not quality or completion targets.

All depth candidates remain draft, with country reviewer/review dates null. Coordinator decisions and checksum manifests are not human approval. Existing inherited review deadlines remain unchanged: BFA, HTI, PNG, UKR and YEM: `2026-11-10`; SSD: `2027-01-31`. Do not renew dates merely to pass a check.

## Approved production boundary

The app's production release remains 24 countries, 272 sources, 531 evidence records and 168 pathways, schema `1.1.0`, content version `2026.10.26.approved-country-bank`, `candidate=false`.

- Runtime SHA-256, UTF-8/LF text: `12f0a7b5c8267ec3a8ed8033f3e4716af69024a9290e023e5264a94ed35ebda8`.
- Source manifest checksum: `b421effc50cf0a46da126ee4deba481ea1b3ea379b846954a45c780ad6023988`.
- Earlier approved pin: `cccf251d86a8f3f3a73c930ff8b284c256304c1a`.

Do not replace this release with the draft expansion or alter approval flags. The production boundary must still hold after remediation. Improved evidence handling can change shared code, with regression tests; it must not silently activate draft data in normal startup.

## Independent review and verified dispositions

Claude reviewed Chad, Somalia, PNG and Tuvalu in depth, with supplementary structure checks on Yemen/Haiti. It found sound causal restraint but uneven operational depth, unlinked additions, missing non-violent fragility content and missing scenario qualifiers. Somalia's sources were not reopened in that review, so its favorable verdict is not source-level certification.

Apply the following dispositions after inspecting the actual files. Several original recommendations need correction.

### 1. Preserve qualifiers in the actual model prompt: highest shared priority

Read-only tracing established a cross-cutting app gap:

- `sector_lenses/climate_bank_selector.py::_score_evidence` scores `analytical_role`, not `evidence_class`. A class-only edit will not change ranking.
- `compact_bank_packet` retains evidence ID, compact statement, evidence status, analytical role and source IDs. Separate scenario, confidence, uncertainty and time-horizon fields are dropped. Pathway alternatives and uncertainty are also dropped. Source metadata is reduced to IDs.
- `sector_lenses/climate_grounding.py::_bounded_bank_projection` and `merge_climate_grounding` use that compact projection in the model's `prompt_context`. Full provenance elsewhere does not restore qualifications to the prompt.
- `sector_lenses/climate_bank.py::materialize_country_bank_packet` retrieves selected evidence and pathway support but does not carry profile `known_gaps`/coverage into the packet. Existing limitations mostly concern draft/expiry status.
- `app.py` calls selection using country, sector and project excerpt. Evidence and pathways are ranked independently; standalone evidence can be selected.

Current packet budgets are target 8 items, maximum 12 and 6,000 characters; combined grounding is bounded at 12,000. Preserve useful bounded retrieval. Choose the smallest shared fix that keeps meaning-critical qualifications with a selected claim, including through trimming. Avoid simply appending the whole profile or increasing budgets.

Add failing tests against the final merged prompt before changing behavior: scenario/time horizon, source assertion versus demonstrated mechanism, expected versus achieved results, geography/population limits, preliminary evidence, reverse-FCV claims, and coverage disclosures. Test budget-edge trimming and supporting-evidence integrity. A qualifier in JSON, provenance, a dossier or an export is insufficient if the model never receives it.

### 2. PNG: selective pathway integration; retain verified numbers

PNG has 23 evidence records and six pathways. E-101 through E-108 are not referenced by pathways, but calling them unused by the app is incorrect. Agriculture retrieval selected E-102/E-103/E-106/E-107/E-105; Water also selected new evidence. These records reached the merged prompt.

Review each addition for a defensible role: pathway premise, resilience/capacity factor, standalone context, or an explicitly limited illustration. Link only where geography, mechanism and source support match. Not every evidence record needs a pathway. Do not blanket-label all eight illustrative or attach records to unrelated mechanisms to satisfy a count.

Specific cautions: E-102 concerns Idauwi/Paipali in Hela, while P-003 concerns Carteret/coastal relocation. E-105's co-occurring intergroup violence and climate vulnerability does not itself demonstrate insecurity-caused recovery delay. E-106 describes programme design, not evaluated joint climate/peace outcomes. Disaggregate intergroup fighting, sorcery accusation-related violence (SARV), and resource-extraction conflict where supported; SARV is the abbreviation for that violence type, not an additional category.

The disputed numbers were subsequently confirmed in the original [UN PNG 2024 annual results report](https://mptf.undp.org/sites/default/files/documents/2025-05/2024_un_in_papua_new_guinea_annual_results_report.pdf): physical PDF page 17, printed spread 29-30, explicitly reports 12 disaster-prone areas/12 projects; 24 vulnerable island/atoll communities; small grants in nine communities; over 16,000 people who **will benefit**. Existing E-103/E-104 wording is faithful. Keep expected reach distinct from achieved reach. Verification used readable PDF text, not a successful screenshot. Record the locator; do not weaken supported numbers merely because Claude's extraction failed.

### 3. Tuvalu: mobility, continuity and scenario qualification

The draft has 12 evidence records and one pathway. Falepili and statehood/territorial-integrity content are absent. Add supported, explicitly non-violent governance/human-security evidence and operational implications, using existing schema categories where possible. Do not invent armed-conflict risk or an official fragility classification.

Sources and corrections:

- [Tuvalu NAP 2025](https://unfccc.int/sites/default/files/resource/NAP_Tuvalu_2025.pdf): Falepili discussion is section 3.1, printed/physical page 18, also page 55. Claude's section 1.4 locator was wrong. Verify before recording.
- [DFAT treaty overview](https://www.dfat.gov.au/geo/tuvalu/australia-tuvalu-falepili-union-treaty) and [treaty text](https://www.dfat.gov.au/geo/tuvalu/australia-tuvalu-falepili-union-treaty/treaty-text-falepili-union): signed 9 November 2023, entered into force 28 August 2024. Article 2 recognizes continuing statehood/sovereignty despite sea-level rise and supports people staying at home. Article 3 provides mobility with dignity. Characterize voluntary, bilateral rights and institutional arrangements accurately; avoid forced-relocation or inevitable state-extinction claims.
- [UNDP-IOM 2022 Tuvalu profile](https://www.undp.org/sites/g/files/zskgke326/files/2022-11/climate-security-risk-assessment-tuvalu-profile.pdf): territorial-integrity discussion is physical page 4, printed spread 6-7, not the review's page 5. It is preliminary/provisional and predates the treaty's entry into force. Keep both qualifications.
- E-103's projection that current 50-year coastal floods may recur every 1-5 years by 2060 in Funafuti, Nui, Nukufetau and Vaitupu has `SSP2-4.5 and SSP5-8.5` in its scenario field but not its compact statement. The actual Urban merged prompt lost the scenario. NAP section 4.2.4, printed/physical pages 24-25, supplies the model context. Repair canonical wording/projection and regenerated prose consistently.
- Profile `known_gaps` still says there is no completed mediated pathway although P-101 exists. Reconcile stale gap statements throughout all countries.

### 4. Chad: bounded mechanisms and accurate coverage

Chad has 14 evidence records and zero assembled pathways, but it contains livelihood, displacement, service/protection and insecurity evidence. Water/Lac retrieval sent these records to the model. Do not implement the blanket wording "hazard context only" solely because pathway count is zero.

Use factual notices such as "No structured climate-FCV pathway is assembled in this draft; the selected evidence provides [actual supported context]. Project-location mechanisms require verification." Calibrate to selected evidence and documented geographic gaps. Counts and dossier size can support triage, but cannot define quality or analytical sufficiency.

TCD-E-006 is a broad source assertion that floods exacerbate displacement/conflict. Inspect both class and analytical role and retain its report-level limitation in the served prompt. A direct source statement does not require a measured causal estimate to count as direct reporting; equally, it must not be presented as demonstrated local causality. Adjudicate the proposed sensitivity reclassification, recording why. Changing class alone does not change current ranking.

The [World Bank Chad Economic Update, April 2023](https://documents1.worldbank.org/curated/en/099070623113040139/pdf/P179299084fd380990a9b10385fd104b6d4.pdf) was accessible during subsequent verification. The general statement appears on physical pages 14-15, printed xii-xiii; recheck the existing ambiguous "PDF p13" locator. Physical page 35, printed 19, discusses conflict-displaced/refugee settlement in floodplains, double-displacement risk and barriers to activity. This is a promising already-cited basis for a bounded FCV-to-exposure/vulnerability mechanism, not proof of climate-caused violence or obstruction of a named adaptation project. Check source-use metadata before editing; the existing `restricted` label warrants checking against the document's attribution/reuse terms.

Seek accessible Eastern Chad climate-security research and Lake Chad livelihood/governance evidence where useful. One region's evidence cannot substitute for another's. Existing FAO GIEWS food-security material may add useful context, but verify period, denominator and forecast status before inserting the suggested 3.18 million figure.

### 5. Somalia and review status

Somalia's 33 evidence records and seven pathways show useful differentiation and causal restraint. It remains draft because no human approval has occurred. Do not change approval/reviewer fields to signal that it is better developed than Chad. The existing approval table already supplies counts for triage. Verify consequential source claims during the full audit; favorable internal calibration is not a substitute.

## Audit and remedy all 146 countries

Use a deterministic inventory plus a source-grounded country review. Automated structure checks and human-facing analytical sufficiency are separate gates. Every country needs a recorded disposition, including those needing no changes. Equal review standards do not require equal pathway counts.

For each whole candidate bank, covering inherited and new material:

1. Check source identity, author/publisher, date, geography, locator, accessibility/reuse limits, evidence references, and whether the claim is actually supported. Reopen material pathway, FCV/protection, numerical and current-context claims. Record verification method and access date. Do not label a whole bank source-verified from one sampled claim.
2. Check causal calibration, direction, mediators, alternative explanations, capacities and countervailing factors. Keep co-occurrence, source assertions, hypotheses, programme intentions, delivery outputs and evaluated outcomes distinct.
3. Check subnational footprint, livelihood systems and affected groups. Prevent national extrapolation from one district/programme, incompatible geographic linking, or historical administrative names being treated as current without qualification. Check known issues such as Vietnam's 2025 administrative reorganization when relevant.
4. Check all projections/numerics for scenario, baseline, time horizon, units, denominator, range and forecast/expected versus observed/achieved status. Keep decisive qualifiers with the claim in compact/model-facing text as well as full records and prose.
5. Review evidence-to-pathway assembly. Link supported premises and capacities selectively; retain legitimate standalone evidence. A pathway must not cite an unrelated place, a generic country risk, or programme intent as proof of its mechanism.
6. Check reverse pathways and non-violent fragility where material: insecurity/institutions affecting adaptation access and durability, mobility/tenure, identity, sovereignty/continuity, exclusion and local governance. Add only source-supported content relevant to that country, without turning climate vulnerability into presumed violence.
7. Reconcile profile, dossier, evidence, pathways, review summary and actual retrieval. Remove stale gap statements or explain remaining limits. Avoid claiming completeness outside supported locations/project types.
8. Assign an audit disposition such as reviewed-unchanged, corrected, enriched or unresolved-limited; record record IDs, sources, changes, remaining limitations and checks. Keep this separate from human approval, which remains pending.

Known source-quality leads: Venezuela SRC-101 uses a user-uploaded Scribd mirror; E-101 through E-103 remain low confidence pending official authentication. Seek official originals, or qualify/exclude material unsupported claims. Uzbekistan's restricted atlas has no substantive extracted evidence; do not fill it speculatively. Inaccessible does not mean false, and a search snippet is not full-document verification. No access-control bypass, bulk copied copyrighted text, credentials, private project material or raw PDFs in the public bank repo.

Avoid treating migration/refugee status or ethnic identity as a threat; distinguish human-wildlife conflict, resource disputes, interpersonal violence and armed conflict. Distinguish FCV sensitivity/do-no-harm from demonstrated FCV responsiveness or peace outcomes.

## Execution plan

Use the smallest repository-consistent implementation. No new workflow framework, quality-score system, dependency or schema category unless the existing design demonstrably cannot meet the requirement.

- [ ] Verify checkouts/remote heads, read instructions, initialize the app submodule, and freeze the pre-remediation evidence of state. Preserve unrelated files.
- [ ] Inspect assembly/review contracts and app callers, tests, fixtures, config and export boundaries. Write failing shared-code regression tests for qualifier and coverage loss. Confirm the exact mechanism with final prompt assertions.
- [ ] Inventory all 146 banks and establish a durable, country-by-country audit ledger. Use existing research/review conventions. Delegate independent bounded country batches only when available and allowed by current instructions; the coordinator owns synthesis and acceptance, and must inspect files/diffs.
- [ ] Implement the minimal shared app fix, then complete source-grounded remediation across every country. Log corrections to Claude's proposed fixes as well as accepted findings.
- [ ] Preserve the `2026.10.26.deep` snapshot and frozen approved/base files. Prefer a new dated candidate version/research remediation layer with reproducible transformations and explicit lineage. Inspect supported version patterns before choosing its name. The current assembler primarily targets added records; handle inherited corrections reproducibly rather than editing approved bases or patching only generated dossiers.
- [ ] Regenerate affected candidate files, dossiers, profiles, decisions/assembly traces, the exact 146-input manifest, approval table and file-identity manifests. Do not silently rewrite old baseline hashes. Document expected count/hash changes; never weaken assertions merely to obtain a pass.
- [ ] Create a new, short-lived unapproved test artifact with a new output filename, current generation time and valid expiry. Keep it ignored. Exercise all 146 country/name resolutions and representative Agriculture, Water and Urban retrievals. Test the final merged prompts for qualifications and honest coverage, not just JSON validity.
- [ ] Run focused tests, then one full suite per repo; investigate failures before expanding checks. Perform analytical/source review separately from structural tests. Review final diffs and staged files for frozen-base drift, unrelated Word changes, secrets and generated artifacts.
- [ ] Commit/push the bank first. Fetch and pin that immutable bank commit in the app submodule, regenerate/recheck the matching local artifact, then commit/push the app. Update existing draft PRs and verify remote heads, bases, draft state and gitlink. Do not merge, mark approved, or deploy.
- [ ] Hand back the per-country ledger, counts and unresolved limits, test commands/results, bundle instructions/expiry, both final SHAs/PR URLs, production-preservation evidence, and a short list of countries/projects for tomorrow's supervised testing.

If a consequential claim cannot be verified, complete the workflow by excluding/qualifying it or recording an explicit unresolved limitation; do not silently accept it. Distinguish "all countries reviewed with limitations disclosed" from "all claims independently verified". Report any remaining analytical approval blocker honestly.

## Test build and verification commands

The previous ignored artifact exists locally at `releases/testing/20261027_global146-test.json` in the bank worktree and pinned app submodule. It is 7,091,301 bytes, generated `2026-10-27T05:15:31Z`, expires `2026-11-02`, version `2026.10.27.global146-test`, artifact kind `unapproved-country-bank-test`, `candidate=true`. Byte SHA-256: `916d9c74c7537f60ab831b7e500cd31b0cb5634018824b0180ee48941e5a68b2`; source checksum: `d489d0043e640421db15b5c9281fcef1529c3c40aa6bfbdd679b1b771a9163cc`.

Historical build command, from the bank repository (reference only; use fresh times/version/output after remediation):

```powershell
python -m scripts.build_test_bundle --country-manifest research/20261026_global_depth/TEST_INPUTS.json --generated-at 2026-10-27T05:15:31Z --test-expires-on 2026-11-02 --content-version 2026.10.27.global146-test --output releases/testing/20261027_global146-test.json
```

The builder refuses overwrite, writes only under `releases/testing`, and allows a short zero-to-seven-day test lifetime. Normal release promotion rejects this artifact format. Do not fake timestamps or relax expiry/approval guards to reuse it.

App setup and historical preview check, from the app repository:

```powershell
git submodule sync --recursive
git submodule update --init --recursive
python -m scripts.run_country_bank_test --bundle data/climate-fcv-country-bank/releases/testing/20261027_global146-test.json --check
```

Use the new bundle path after remediation. `--serve` launches the local preview on `127.0.0.1:5001`, without debugger/reloader. It requires the three explicit guards `CLIMATE_COUNTRY_BANK_PATH`, `CLIMATE_COUNTRY_BANK_PREVIEW=unapproved-test`, and `FCV_APP_ENV=country-bank-test`, plus artifact/schema/checksum/date validation. The launcher manages the test configuration; do not put preview settings into normal startup, Render or ITS. Preserve UNAPPROVED banner, `no-store`, and absent ETag/Last-Modified behavior.

Relevant bank tests: `tests/test_global_depth_integrity.py`, `test_depth_intake_integrity.py`, `test_depth_assembly.py`, `test_unapproved_test_bundle.py`, `test_approved_october_release.py`, `test_validation.py`, `test_dossier.py`, and release/repository contracts. Relevant app tests: `tests/test_climate_bank_selector.py`, `test_climate_bank_selector_realistic.py`, `test_climate_grounding.py`, `test_climate_grounding_conflicts.py`, `test_climate_bank.py`, production/deployment contracts, `test_climate_bank_unapproved_test.py`, `test_country_bank_test_launcher.py`, and `test_bank_country_names.py`. Add tests alongside the affected contracts; expand export tests only if that boundary changes.

Full bank suite:

```powershell
python -m pytest -q -p no:cacheprovider
```

Previous app offline full-suite command, with four known browser hangs excluded:

```powershell
python -X utf8 -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-* --deselect=tests/test_climate_lens_frontend.py::test_chromium_print_opens_exported_disclosures_and_restores_screen_state --deselect=tests/test_climate_lens_frontend.py::test_result_stage_tabs_do_not_overflow_phone_viewport --deselect=tests/test_climate_lens_frontend.py::test_result_download_header_wraps_inside_phone_card --deselect=tests/test_climate_lens_frontend.py::test_result_session_bar_wraps_inside_phone_viewport
```

Historical results, not acceptance of future changes:

- Bank: 695 passed in 135.07 seconds.
- App offline full suite: 1,969 passed, two skipped, four deselected in 380.35 seconds. This preceded only the final data-pin/docs update.
- Final app preview/name/launcher focused tests: 28 passed in 4.47 seconds.
- All 146 countries materialized for Agriculture/Water/Urban; 363 ISO/name/alias resolutions passed.
- All 146 nine-file review identities/counts/references/draft fields and 878 baseline hashes checked. Nine-file identities cover six candidate files plus raw intake, decision and assembly trace; individual UTF-8/LF hashes form a sorted compact JSON relative-path/hash map, whose SHA-256 is the country identity.
- Local HTTP preview returned 200, the unapproved banner and correct no-cache headers. No assessment was submitted; server stopped.

These checks did not establish analytical completeness or preservation of separate qualifier fields in the model prompt. No complete fresh browser/model assessment, DOCX visual acceptance or hosted deployment acceptance was performed. The four deselected Chromium tests are not a browser pass. Do not turn historical counts into fresh verification claims.

## Environment and handoff hygiene

On this managed Windows machine `rg.exe` is blocked by Code Integrity policy. Use `git ls-files`, scoped `Select-String`/directory listing or Python reads. PowerShell uses Constrained Language Mode and has sometimes hung; CMD plus `C:/WBG/Python313/python.exe -X utf8` has worked for diagnostics. A recent `git status` submodule subprocess emitted `waitpid` errors, while `git status --short --ignore-submodules=all` worked; inspect the submodule separately rather than diagnosing a product regression. Wait for process completion before dependent actions.

Managed Windows pytest/browser Temp or named-pipe access failures may require normal process permissions through the approved escalation mechanism. Do not bypass organization policy, TLS checks or browser security, or install dependencies globally. Query actual browser availability before promising UI testing. Never copy credentials or tokens into prompts, documents or either repo.

Save project outputs in the relevant repo, respecting ignore rules. `docs/superpowers/` is intentionally ignored; do not force-add handovers there. The tracked earlier build guide is `docs/20261027_global-country-depth-test-build.md` in the app. Keep downloaded PDFs, raw model responses, screenshots, logs and generated bundles out of Git. Use `apply_patch` for local file edits and preserve unrelated dirty work.

## Completion gate

The task is ready for supervised app testing when all 146 countries have auditable dispositions; all consequential unresolved claims are safely excluded, qualified or visibly limited; app prompt tests prove qualifications/coverage survive selection and trimming; candidate artifacts reproduce; production/Word ancestry protections hold; relevant tests pass with exclusions stated; and both draft PRs point to the verified pushed commits with the correct bank gitlink.

That is readiness for testing and human review. Human approval, production activation and deployment remain separate decisions.
