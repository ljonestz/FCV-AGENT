# Climate-FCV 24-country candidate-bank handover

**Date:** 2026-08-13<br>
**Application branch:** `codex/climate-summary-quality-fixes`<br>
**Application base:** `5702497`<br>
**Bank submodule commit:** `12a804f`<br>
**Bank branch:** `expand-climate-country-bank`

## Status

The climate country bank now has reviewed candidate packages for 24 FCV country
contexts. The candidate runtime is:

`data/climate-fcv-country-bank/releases/candidates/2026.08/runtime.json`

It contains 291 sources, 565 evidence records, and 178 mediated pathways. The
packages are compiled from the supplied country research packets and retain the
packets' causal caveats, uncertainty, source locators, and known gaps.

Countries: Afghanistan, Burkina Faso, Cameroon, Central African Republic,
Democratic Republic of the Congo, Ethiopia, Haiti, Iran, Iraq, Lebanon, Libya,
Mali, Mozambique, Myanmar, Niger, Nigeria, Papua New Guinea, Somalia, South
Sudan, Sudan, Syria, Ukraine, West Bank and Gaza, and Yemen.

## How to run a preview

The default production runtime remains the approved-only
`releases/current/runtime.json`, so these candidates do not affect ordinary
screening runs. To use the full candidate bank in a controlled local or testing
run, set:

```text
CLIMATE_COUNTRY_BANK_PATH=data/climate-fcv-country-bank/releases/candidates/2026.08/runtime.json
CLIMATE_COUNTRY_BANK_PREVIEW=reviewed-candidate
```

The resulting climate grounding should remain labelled `preview; not approved`.
Do not copy the candidate runtime into `releases/current` or use the promotion
command until the substantive country review is complete.

## Validation performed

- All 24 candidate country directories pass schema-1.1 country validation.
- Candidate release validation passes with `candidate: true` and schema `1.1.0`.
- Candidate release build is deterministic and includes all 24 country summaries.
- Companion-bank targeted tests pass: `45 passed`.
- The broader suite was attempted but its temporary-directory fixtures were
  blocked by Windows/OneDrive permission errors; no assertion failure was
  identified in the targeted run.

## Next review step

Review the country dossiers and evidence ledgers by country. Promotion should be
done only for content that has passed substantive review, with a new approved
release generated explicitly. The candidate packages are structured runtime
content, not a substitute for that decision.
