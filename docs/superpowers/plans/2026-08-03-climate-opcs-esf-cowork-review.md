# Targeted OPCS/ESF Cowork review plan

**Status:** Deferred. Run only after the Climate-FCV drafting workflow is stable.

## Purpose

Use the WBG LLM/Cowork environment for one bounded conformance review of the
operational-guidance layer. The review should clarify authoritative wording and
document-routing boundaries that cannot be established from the public repository.
It should not redesign the product or become a mandatory workflow stage.

## Material to provide

- `sector_lenses/climate_operational_guidance.py`
- the drafting fields and validators in `sector_lenses/climate_recommendations.py`
- the guidance and drafting portions of `sector_lenses/climate_verified_prompts.py`
- a compact table of the currently supported document and instrument combinations
- targeted questions below; do not provide the South Sudan PCN or raw country-bank sources

## Questions for the WBG LLM

1. For each registry proposition, is the proposed PCN/PID, PAD/Project Paper,
   Results Framework, E&S instrument, or implementation-document destination
   appropriate for the stated document and financing instrument?
2. Which wording may be presented as standard drafting advice, which must remain
   conditional or advisory, and which would incorrectly imply a binding OPCS/ESF
   requirement?
3. When is it appropriate to direct a TTL toward the ESCP, ESMF, SEP, Results
   Framework, POM, or another named instrument, and what evidence is required to
   establish that the instrument exists and covers the relevant activity?
4. Are the current distinctions between commitments, proposed actions, readiness
   flags, and specialist referrals consistent with applicable guidance?
5. Identify any proposition that requires an authoritative paragraph citation,
   specialist confirmation, or removal because its scope cannot be stated safely.

## Expected output

A compact review matrix with: registry/guidance ID, current proposition, verdict
(`supported`, `revise`, `remove`, or `needs authoritative source`), precise revised
wording where needed, authoritative source/paragraph when available, and a short
scope note. Separate unresolved questions for OPCS or E&S specialists.

## Explicit exclusions

- no general code review or UI/product redesign
- no review of the country-bank generation process
- no routine review of project outputs or recommendation prose
- no ingestion of raw internal guidance into the application or repository
- no requirement for team confirmation in normal Climate-FCV runs
- no change to admission thresholds based solely on this review

## Follow-up

Translate only supported changes into small registry or validator patches, add a
regression test for each changed boundary, and record any shared-contract impact in
the private build-parity log before deployment.
