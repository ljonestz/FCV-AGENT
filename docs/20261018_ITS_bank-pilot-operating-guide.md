# ITS operating guide: bank-based supervised Climate-FCV pilot

## Delivery boundary

This handover is the FCV-AGENT reference application and its pinned country bank,
configured for a controlled, supervised IPF pilot. The user accepted this scope on
18 October. It is not a claim that an ITS FastAPI/Gemini port has been integrated,
deployed or accepted. Use the delivery manifest for the exact source revision,
bank revision, file hashes and acceptance result. A branch name alone is not a
version identifier. Final live acceptance is recorded separately from this guide.

The pilot uses project documents and the pinned bank. Live web research is outside
the accepted scope. A human must check current-context claims and consequential
premises before sharing: phase/asset scope, funding, mandates, commitments,
beneficiary eligibility and claimed outcomes. Minor editorial inconsistencies and
qualified analytical inferences need not block useful advice.

## Reference deployment

Use an isolated Python environment. Install the application dependencies from
`requirements.txt`; the delivery includes no credentials. Configure the provider
key through the host's existing secret-management workflow as `ANTHROPIC_API_KEY`.
Keep the exact model configuration identified in the acceptance manifest.

For a Git checkout, initialize the pinned bank using the existing build entry point:

```sh
python render_build.py
```

The source archive includes bank files at `data/climate-fcv-country-bank`. An archive
has no Git metadata, so install dependencies directly with
`python -m pip install -r requirements.txt` and verify the bank files against the
delivery manifest. Do not run Git submodule commands in an extracted archive.

Set the accepted operating mode explicitly:

```text
CLIMATE_VERIFIED_RUN_MODE=quality
CLIMATE_RESEARCH_MODE=bank_only
```

Keep assessment/reviewer model overrides unset unless a separately tested model
is approved. The mode skips both live research providers and cached live material
only on the Climate route. Normal FCV keeps its existing research behaviour.

On the existing Linux hosting configuration, use the WSGI entry point so gevent
patches networking before the provider SDK is imported:

```sh
gunicorn wsgi:app --worker-class gevent --workers 1 --threads 1 --bind 0.0.0.0:$PORT --timeout 1200
```

Do not shorten the hosting timeout below the application's existing stage budgets.
Check `/health` for the expected build, `quality` and `bank_only` before testing.
Do not confuse a cold start, missing bank or host timeout with an analytical error.

## Pilot spending controls

The acceptance guard is opt-in and separate from production operational budgeting.
It permits only known plain-text first-party requests and rejects live tools. Set
both `FCV_PILOT_BUDGET_MICROUSD` and `FCV_PILOT_BUDGET_DB` together. A ceiling above
5,000,000 microUSD is rejected. Reservations include the full allowed output once,
double input-byte/framing headroom, failures and retries; they are not invoices.
Ledgers are atomic and cannot have their ceiling changed. Never reset a consumed
ledger or repeat an allowance after an ephemeral host redeploy.

The preview is returned to a 1-microUSD blocker after testing. It cannot run paid
assessments until an authorized allocation is activated. Do not copy that blocking
test configuration into a service expected to process pilot users, or silently
remove operational cost controls. Agree the pilot's operating allowance separately.

## Review and sharing

1. Upload the complete current project document. Verify document type, IPF scope,
   country and the selected Climate lens. Start a new analysis for a new project.
2. Review all ranked priorities and the three core questions. Useful peace/social
   dividend mechanisms can be qualified inference without explicit peace objectives.
   Proposed arrangements must not be presented as existing commitments.
3. Resolve consequential source issues. In particular, an open activity or city list
   does not reopen an explicitly selected subset of assets; later phases are not
   current-phase candidates. Preserve useful advice on design and delivery.
4. Keep the automated review status visible. Minor findings may retain prose with a
   notice. Consequential findings withhold affected sections; structural invalidity
   and block remain closed. A fallback is not the richer generated native narrative.
5. Download Word/HTML, the review packet and saved session. Record named approval in
   the existing authenticated organisational workflow against the exact packet hash
   and files. `publication_approved` stays false in the application. A material edit
   requires a new bound packet; approval of an earlier version does not transfer.

## ITS integration and acceptance

For an ITS port, preserve the verified pipeline, native schemas, prompt versions,
normalization, object-specific admission and canonical renderer together. Copying
only the prompts does not reproduce the accepted behaviour. Implement the provider
adapter contract with the ITS model and repeat semantic acceptance on that model.
Preserve ITS-specific internal OPCS retrieval; country context cannot establish
project commitments. Do not replace ITS retrieval with the reference build's public
research code. Preserve normal-FCV delimiters, rating semantics and shared routes.

Mandatory port checks: selected/open scope, explicit proposals versus commitments,
minor/consequential review disposition, invalid/missing review behaviour, Summary/
Detailed parity, non-first priority, standalone HTML/Word, session restore/new ID,
snapshot-bound packet hashes and rejection of reader drift. Verify bank loading
and that bank_only makes no research provider calls. Current-context review remains
human-led. Reference-build acceptance does not certify a different model or port.

## Release and rollback

Production promotion needs the user's explicit release decision on the exact tested
candidate and its remaining limits. No automatic merge, production deployment or
message to ITS is part of this handover. Preserve the development branch/worktree.

Before promotion, record the current production commit and configuration. Deploy
the exact accepted candidate, verify health/mode/bank and a saved-session/export
smoke without a new paid assessment. If those checks fail, restore the recorded
production commit and configuration. Never test by modifying the original acceptance
artifacts or by silently substituting a new model. Keep the previous production
version available until the receiving team confirms the pilot works in its host.
