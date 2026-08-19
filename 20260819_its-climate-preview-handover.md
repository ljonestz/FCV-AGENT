# ITS handover: Climate preview

**Date:** 19 August 2026
**Preview:** <https://fcv-agent-climate-preview.onrender.com/>
**Branch:** `codex/climate-summary-quality-fixes`
**Deployed commit:** `08b3cb99a79bd0fdc855bb0f260de15ae20c45f4`

## Status

The Climate preview issue reported by ITS is fixed. The service is live and a
complete Step-by-Step run through Stages 1-3 finished without browser or server
errors.

The Climate module is still experimental/pilot. Its outputs are advisory and
should be reviewed by an FCV/climate specialist.

## What ITS reported

The original Stage 1 request returned:

```text
cannot access free variable 'lens_context' where it is not associated with a value in enclosing scope
```

Stage 1 was reading the Climate lens context inside its streaming closure before
that variable had been initialized in the Step-by-Step route.

## Fixes

1. Commit `c6aa04c` initializes the Stage 1 lens context before the streaming
   closure starts and adds a regression requiring an error-free Stage 1 terminal
   event.
2. The first Render deploy of that fix exposed a separate startup dependency
   problem: Gunicorn's gevent worker needed the `packaging` library. Commit
   `08b3cb99` declares it explicitly in `requirements.txt` and adds a deployment
   contract test.

## Checks completed

- Full automated suite: `966 passed`.
- Render deploy `dep-da2mjudbedkc73cvpn60`: live on `08b3cb99`.
- Full live Step-by-Step assessment:
  `460ebf9c-88fb-4341-8175-201a3798eff5`.

| Stage | Result |
|---|---|
| 1 | HTTP 200; completed; no parse error |
| 2 | HTTP 200; completed; sensitivity `Adequate`, responsiveness `Low`; no parse error |
| 3 | HTTP 200; completed; three priorities; no parse error |

All three stages used the same assessment ID. The browser recorded no console or
page errors, and the matching Render window contained no `lens_context`, error,
or traceback entries. Stage 1 used its normal bounded research retry once before
the evidence gate accepted the second attempt.

## Climate knowledge-bank boundary

The current candidate bank is limited to 24 FCV/FCS country contexts and remains
labelled `preview; not approved`. The Climate module can still run for other
countries, but it will rely on accepted live research and/or thematic guidance
and will have less country-specific prior knowledge.

It would be useful to add an `Experimental` or `Pilot` label to the landing page
so users see this status before starting. That is a product/UI follow-up, not part
of this documentation change.

## ITS notes

- Use `08b3cb99` as the current preview reference.
- If the internal FastAPI build has the same Stage 1 closure pattern, mirror the
  early lens-context initialization and its regression.
- Keep internal build-specific retrieval and model-provider differences.
- Preserve the candidate-bank preview label and fallback states.
- Keep expert review in the user guidance while the module remains a pilot.

The detailed recommendation-routing history remains in
[`20260814_its-production-readiness-handover.md`](20260814_its-production-readiness-handover.md).

## Short Teams message

Hi - the Climate preview issue you flagged is now fixed. It was caused by the
Step-by-Step Stage 1 flow trying to use the Climate lens context before it had
been initialized. I also fixed a separate Render startup dependency that appeared
when the patch was deployed. The preview is live again, and I ran all three stages
without any further errors.

The Climate module is still experimental, so maybe we should label it
`Experimental` or `Pilot` on the landing page. For now, the knowledge bank covers
FCV/FCS countries only. It can still run elsewhere, but with less prior country
knowledge and more reliance on live research and thematic guidance.
