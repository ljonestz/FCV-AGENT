# Climate FCV country bank approval and production readiness

Review date: 26 October 2026. Decision requested: approve the staged release approach below. This note does not approve country evidence or authorize a production deployment.

## Recommendation

Complete the existing country bank before collecting more countries. Review and release countries in small batches, with an explicit record of included evidence, exclusions, reviewer and review dates. Keep the current approved South Sudan release available for rollback.

Start the substantive review with the six original candidate profiles: South Sudan, Burkina Faso, Haiti, Papua New Guinea, Ukraine and Yemen. Their profile notes have evidence links, but their country review windows have expired. They are a practical first review batch, not six countries already cleared for publication. Review the other 18 after repairing their profile references. A country can proceed earlier if its review is completed; the batch order is not a quality ranking.

## Method and limits

The review compared the pinned bank, candidate records, release builder and app loader; validated all candidate directories; ran the bank test suite; and spot-checked selected public sources. Structural validation tests fields and relationships. It cannot establish that every claim is supported, geographically appropriate or current. Source checks so far are a sample, not substantive sign-off of the 565 candidate evidence records.

Local app baseline: `7faa259588f8f0debff550dde44efd409fdc1810`.
Pinned bank: `12a804fe92bacfdaf0bec7926725d8a7a9376fe4`.
The deployed service branch, SHA and environment have not been verified in this review.

## Existing releases

| Bank artifact | Content | Status |
|---|---|---|
| `releases/current/runtime.json` | South Sudan; 12 referenced sources, 19 evidence records, 7 pathways; schema 1.0.0 | Approved July pilot; country review due 31 July 2027 |
| `releases/candidates/2026.08/runtime.json` | 24 countries; 291 referenced sources, 565 evidence records, 178 pathways; schema 1.1.0 | Reviewed preview; human approval pending |

The candidate country registers contain 323 sources. The release contains 291 because it includes referenced sources. The thematic climate module is separate from the country bank and contains 8 sources/source notes and 19 questions.

## Country review inventory

Sources below are country-register counts, not release-reference counts. Unlinked notes count executive, geographic and sector profile notes without evidence IDs. A missing ID is a traceability defect, not proof that the statement is false. All 24 candidates remain reviewed, not approved.

| Country | ISO3 | Sources | Evidence | Pathways | Unlinked profile notes | Country review due |
|---|---|---:|---:|---:|---:|---|
| Afghanistan | AFG | 14 | 30 | 8 | 6/9 | 2027-08-13 |
| Burkina Faso | BFA | 10 | 15 | 6 | 0/6 | 2026-09-10 |
| Central African Republic | CAF | 13 | 22 | 8 | 8/11 | 2027-08-13 |
| Cameroon | CMR | 12 | 26 | 8 | 8/11 | 2027-08-13 |
| Democratic Republic of Congo | COD | 12 | 24 | 8 | 7/8 | 2027-08-13 |
| Ethiopia | ETH | 14 | 22 | 8 | 8/11 | 2027-08-13 |
| Haiti | HTI | 11 | 15 | 6 | 0/6 | 2026-09-10 |
| Iran | IRN | 14 | 24 | 8 | 8/11 | 2027-08-13 |
| Iraq | IRQ | 15 | 24 | 8 | 8/11 | 2027-08-13 |
| Lebanon | LBN | 13 | 22 | 7 | 8/11 | 2027-08-13 |
| Libya | LBY | 13 | 25 | 8 | 8/9 | 2027-08-13 |
| Mali | MLI | 13 | 26 | 8 | 9/12 | 2027-08-13 |
| Myanmar | MMR | 15 | 27 | 8 | 4/7 | 2027-08-13 |
| Mozambique | MOZ | 11 | 26 | 8 | 8/11 | 2027-08-13 |
| Niger | NER | 15 | 30 | 8 | 8/11 | 2027-08-13 |
| Nigeria | NGA | 14 | 28 | 8 | 7/10 | 2027-08-13 |
| Papua New Guinea | PNG | 11 | 15 | 6 | 0/6 | 2026-09-10 |
| West Bank and Gaza | PSE | 12 | 28 | 8 | 8/11 | 2027-08-13 |
| Sudan | SDN | 14 | 30 | 8 | 7/10 | 2027-08-13 |
| Somalia | SOM | 14 | 23 | 6 | 10/13 | 2027-08-13 |
| South Sudan | SSD | 16 | 27 | 7 | 0/8 | 2026-09-01 |
| Syria | SYR | 17 | 24 | 8 | 7/10 | 2027-08-13 |
| Ukraine | UKR | 12 | 16 | 6 | 0/6 | 2026-09-10 |
| Yemen | YEM | 13 | 16 | 6 | 0/6 | 2026-09-10 |

## Findings that affect approval

1. Six candidate country review windows have expired. Renew them only after a recorded review. The approved South Sudan July release and the larger August candidate are different artifacts.
2. Eighteen profiles have substantive notes without evidence IDs. Add references only after checking that the cited records support the actual wording; narrow or remove unsupported notes. Automatically attaching the first available ID is not an acceptable repair.
3. Somalia records `SOM-E001` to `SOM-E003` use near-term horizon metadata for claims spanning 2030, 2050 and 2080. The [Somalia climate risk profile](https://weatheringrisk.org/sites/default/files/document/Climate_Risk_Profile_Somalia.pdf) supports projections across those dates. Correct the horizon mapping without changing the source's scenarios or baselines.
4. Somalia records `SOM-E006` to `SOM-E008` refer to older harvest and price conditions through a rolling FAO URL. The [FAO Somalia country brief](https://www.fao.org/giews/countrybrief/country.jsp?code=SOM) inspected on 26 October carries a reference date of 15 September 2026. Preserve an identifiable historical edition or refresh the records; the changing page does not establish that the older figures were false.
5. No current-tier candidate records are overdue according to their stored dates on 26 October. That result does not establish currentness: imported review intervals can outlast a seasonal claim's relevance.

The [SIPRI West Africa assessment](https://www.sipri.org/publications/2022/sipri-insights-peace-and-security/climate-change-and-violent-conflict-west-africa-assessing-evidence) supports mediated pathways involving livelihoods, mobility, armed actors and elite grievances, with limits to the evidence base. Preserve that qualification in Burkina Faso material; do not turn a regional mechanism into a proven country-level causal effect.

## Proposed approval procedure

For each country, prepare a decision sheet with the exact candidate version, evidence and pathway IDs, source locators, affected geography, applicable period, uncertainty and proposed disposition: retain, revise or exclude. Check every included record and each profile synthesis. Distinguish FCV sensitivity from responsiveness and distinguish a plausible mechanism from an evaluated effect.

Use dated, stable editions for changing situation reports. Keep historical evidence explicitly historical. For projections retain the emissions scenario, baseline, horizon and geographic scope. Preserve limitations where evidence is local, qualitative or programme-specific. Lack of a national causal estimate does not itself disqualify a carefully bounded operational lesson.

Lindsey or another designated reviewer approves the exact included records and country profile after the corrections. Record the actual reviewer and review date, with review intervals suited to the claims. Automation must not turn a general instruction to proceed into substantive approval of unread records.

## Proposed production changes

The existing app accepts schema 1.1.0 only through its explicitly enabled candidate-preview route. The bank promotion function emits approved schema 1.1.0 with `candidate: false`. Promoting that file alone would make it incompatible with the current loader.

Keep the existing bank and importer architecture. Make a narrow loader change that separates schema validation from approval policy: support approved schema 1.1.0, retain approved schema 1.0.0 compatibility, and permit reviewed records only in the existing explicit preview mode. Unknown schemas and unapproved production records must fail closed.

Define and test current-record freshness at selection time. Expired current evidence must not be selected as current context; dependent profile or pathway content must not retain an unsupported claim. Keep usable structural evidence when the remaining packet is sufficient, with an explicit limitation. Do not disable expiry checks globally to keep a country selectable.

Promotion must include only signed-off countries and records. Validate source and evidence references after exclusions, build a versioned release, and pin the bank commit in the app. Preserve the previous approved release and app commit for rollback. Production must not depend on candidate-preview environment settings.

## Verification and deployment conditions

Completed:

- All 24 candidate directories passed schema 1.1.0 validation with required profiles and an as-of date of 26 October 2026.
- Bank test suite: 288 passed in 122.08 seconds, using normal process permissions. Earlier sandbox temporary-directory failures were environment failures.
- No generic `verified source record` locators were found in candidate evidence.

Before release:

- Test approved schemas 1.0 and 1.1, preview opt-in, reviewed-record rejection in production, unsupported schemas, expiry, missing references and rollback.
- Test country selection for each included country and clear fallback for excluded or unavailable countries. Check that geography, dates and uncertainty remain available to the assessment workflow.
- Run focused app tests, then the full suite once. Keep analytical review separate from test success.
- Verify the target service, configured branch, deployed SHA and environment. Run the repository's standard Somalia IPF smoke and quality checks on the agreed test service, including detailed HTML and DOCX exports, before production promotion.
- Obtain a specific paid-run allowance before model-backed acceptance checks; this review incurred no paid model calls. Record the accepted release and deployment decision explicitly.

No country statuses, review dates, runtime release, application code or production configuration were changed by this readiness review.

## Expansion after the first approved release

Use the same approval procedure for new countries. The later browser collection package should return draft evidence with source editions, locators, geography, dates, uncertainty and coverage gaps. It must not self-approve findings. Parameterize the existing importer's hardcoded candidate version and dates, and remove automatic evidence-link and horizon guesses before using it for another batch. Test one new-country packet end to end before collecting the wider set.
