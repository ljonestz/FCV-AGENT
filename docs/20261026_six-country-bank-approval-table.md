# Six-country Climate-FCV bank: approval table

Review date: 26 October 2026. Candidate version: `2026.08`. Bank commit: `12a804fe92bacfdaf0bec7926725d8a7a9376fe4`.

**Decision requested: approve the proposed corrections and exclusions for preparation of new candidates, not production release.** All six countries remain pending human approval. No candidate content, approval status, review date, submodule pin or deployment was changed during this review.

## Method and limits

The review compared all 104 evidence records with their cited primary-source passages, checked all 37 pathways against their evidence and causal-strength labels, and reviewed all 62 profile synthesis components and their dependencies. The register contains 73 sources; 72 support evidence records. The unused BFA-SRC-001 was not fully inspected and received no substantive verdict.

Checks covered geographic and temporal scope, observations versus projections or recommendations, uncertainty, locators, source metadata and reuse notices. Where direct access failed, continuous relevant passages indexed under official publisher URLs were used only when they exposed the necessary claim and qualifications. This is passage-level review, not cover-to-cover verification of every source. Historical findings remain historical. No source documents are bundled or cleared for redistribution.

`RETAIN` means no mandatory record-level edit; source-register corrections may still apply. `REVISE` means an explicit correction is required before approval. `DEFER` means exclude from the proposed release until the identified evidence gap is resolved. These are review recommendations, not human approval decisions.

## Country approval table

Counts below are **retain / revise / defer**. Every human decision is pending.

| Country | Evidence | Pathways | Required before human approval | Human decision |
|---|---:|---:|---|---|
| South Sudan | 26 / 1 / 0 | 7 / 0 / 0 | Correct sorghum locator, source-date metadata and three profile sentences; distinguish projected exposure and programme outputs from observed or durable capacity. | Pending |
| Burkina Faso | 13 / 2 / 0 | 4 / 1 / 1 | Correct rainfed-land wording and unsupported delivery-cost modifier; narrow P-003; exclude P-005; correct profile outcome language and dependencies. | Pending |
| Haiti | 14 / 1 / 0 | 4 / 2 / 0 | Correct ICRC date/locator; remove unsupported recruitment consequence; downgrade one pathway from direct to triangulated; note revised WFP plan version. | Pending |
| Papua New Guinea | 11 / 4 / 0 | 3 / 3 / 0 | Correct rainfall uncertainty and three locators; narrow drought consequences and evidence links; correct recovery strength, profile wording and reuse metadata. | Pending |
| Ukraine | 12 / 4 / 0 | 5 / 1 / 0 | Correct locator; distinguish inferred ecosystem/adaptation effects and reconstruction recommendations from observed capacity; downgrade P-003 and qualify profile synthesis. | Pending |
| Yemen | 6 / 9 / 1 | 1 / 4 / 1 | Correct dates, periods, sampling scope, projections, locators and exposure assumptions; narrow water/electricity claims; exclude E-009 and P-005; propagate dependency and metadata corrections. | Pending |
| **Total** | **82 / 21 / 1** | **24 / 11 / 2** | **104 evidence records and 37 pathways reviewed. No country is approvable as stored.** | **Pending** |

## Exact correction and exclusion register

IDs below use each country's prefix. The linked reviews provide replacement wording, source links, locators and profile changes; this table does not replace those instructions.

| Country | Evidence to revise | Evidence to defer | Pathways to revise | Pathways to defer | Detailed review |
|---|---|---|---|---|---|
| SSD | E-003 | None | None | None | [South Sudan / Burkina Faso](20261026_source-review-ssd-bfa.md) |
| BFA | E-002, E-009 | None | P-003 | P-005 | [South Sudan / Burkina Faso](20261026_source-review-ssd-bfa.md) |
| HTI | E-008 | None | P-002, P-004 | None | [Haiti / Papua New Guinea](20261026_source-review-hti-png.md) |
| PNG | E-001, E-006, E-011, E-012 | None | P-002, P-004, P-005 | None | [Haiti / Papua New Guinea](20261026_source-review-hti-png.md) |
| UKR | E-004, E-011, E-015, E-016 | None | P-003 | None | [Ukraine / Yemen](20261026_source-review-ukr-yem.md) |
| YEM | E-001, E-004, E-005, E-006, E-007, E-011, E-013, E-014, E-016 | E-009 | P-001, P-002, P-003, P-004 | P-005 | [Ukraine / Yemen](20261026_source-review-ukr-yem.md) |

Three exclusions are recommended:

- **BFA-P-005:** municipal service and trust evidence does not establish the required climate interaction. The underlying contextual evidence can remain.
- **YEM-E-009:** the broader governance, enforcement and utility-finance claim could not be verified against its cited water-diagnostic pages. Inspected monitoring passages do not establish every clause. This is an access/evidence limitation, not a finding that the claim is false.
- **YEM-P-005:** programme-delivery findings do not establish a valid climate-to-FCV, FCV-to-climate or bidirectional pathway. Keep the supporting response-performance evidence, but remove the pathway and its profile dependencies from the proposed release.

## Conditions applying across the package

1. **Time and approval:** country review deadlines have expired: South Sudan on 1 September and the other five on 10 September 2026. This review does not renew them. Stored `reviewed` flags are not new human sign-off. Of the evidence records, 48 are in the current refresh tier; their stored due dates do not prove currentness.
2. **Source access:** several checks relied on official indexed passages. Haiti's old climate profile and NAP, Ukraine's climate report and Yemen's water diagnostic were not all available as full PDFs through the review tools. The detailed reviews identify the passages and limitations. Yemen E-001 can be corrected to the inspected alternate official PDF, section 3.1.1, printed page 61; E-009 remains deferred.
3. **Yemen current context:** the October-December 2026 IPC figure is a June projection using information through 20 April, for the analysed government-controlled areas, not a fresh nationwide observation. An [October WFP update](https://www.wfp.org/news/wfp-warns-hunger-surging-yemen-conflict-displaces-thousands) reports deterioration but does not replace that IPC classification. Preserve the different periods, populations and methods.
4. **Reuse metadata:** public download does not establish an open licence. Correct the identified permission-required notices and use `unknown` where explicit open terms were not established. Apply the documented source-date and version corrections. Do not redistribute source PDFs on the strength of this review.
5. **Dependencies:** evidence, pathways, profile text and dossier must agree after corrections. Remove deferred IDs from substantive support chains; preserve the distinction between documented programme outputs, intended capacity and demonstrated outcomes.

## Next approval step

If the correction package is accepted, prepare new candidate versions with the specified edits and exclusions, regenerate dossiers, run bank validation and record new hashes. A named human reviewer should approve or reject those exact revised artifacts. Production promotion and deployment require a separate decision and remain out of scope.

This table supersedes the earlier spot-check recommendations in [the first-wave review](20261026_first-wave-country-bank-review.md), not its frozen-file hash record. All 36 canonical candidate files were checked against the review-start hashes and remained unchanged. Record coverage was checked against the actual candidate JSON: each of the 104 evidence IDs and 37 pathway IDs appears exactly once in the three detailed reviews.

No application tests or live deployment checks were repeated for this documentation-only review. The remaining risks are incomplete source access for YEM-E-009, historical or local evidence being read too broadly, unresolved reuse metadata, and human approval still pending.
