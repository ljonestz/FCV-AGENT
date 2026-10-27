# Global country bank: controlled deployment acceptance

Lindsey authorized an isolated Render test deployment, then a fresh combined
USD15 ceiling for one Smoke assessment and, only if Smoke succeeds, one Quality
assessment. This includes upload helpers, research, native stages, reviews,
bounded corrections and retries. Earlier allowances are consumed and untouched.
No merge or production deployment is authorized. Both PRs remain draft.

## Deployment and test scope

- Test service: `fcv-agent-climate-smoke`, `srv-d6gsivcr85hc73a2833g`,
  <https://fcv-agent-1.onrender.com>, workspace FCV LLM Services.
- Branch: `feat/global-country-bank-depth-20261026`; auto-deploy off;
  build entry point `python render_build.py`.
- Initial deployment: `dep-dbgdcf6k1f9s73bus5r0`, app
  `37dd1e5e842285189f970abbc5b163bcd2e34c89`, live 27 October at 16:51:52 UTC.
- Bank: immutable `daf594f8ca899a44bcea4e057a85b0d547ed9c33`, qualified
  routine-use release `2026.10.27.approved-global-country-bank`, 146 countries.
- Initial health: build `37dd1e5e8422`, live research, Smoke. Spending remains
  blocked at one microUSD while the web-search guard is verified.
- Production health remains `6f3d5e65e213`, bank-only, Quality. No production
  setting or deployment was changed.
- A settings update automatically rebuilt the old test-service commit first
  (`dep-dbgd72ou01pc738lkd6g`). The explicit branch deployment superseded it;
  spending was blocked throughout.

Use the complete public Somalia STAIRP P513127 concept PID in
`test_documents/live_acceptance/`, SHA256
`61e3ee924d114ddbdf19dd6835d2cb051a852f8a1fcd8810b3e8b77b2de994e1`.
Select the Climate-FCV lens and Express workflow for both authorized tests. The
pilot permits the Climate-active core search's three-use maximum and dedicated
Climate search's two-use maximum; ordinary four-use core research is outside this
pilot. Step-by-Step live behavior is not newly accepted by these two runs.
Keep assessment IDs, observed requests, raw outputs, browser/export evidence and
budget records ignored under `output/20261027-global-bank-deployment/`.
The immutable authorization record is
`20261027_fifteen-dollar-test-authorization.json` in that folder.

## Minimal cost-control extension

Legacy plain-text pilots retain their USD6 maximum and no-refund reservations.
An explicit web-search pilot mode permits at most USD15 with a separately bound
ledger. It admits only the currently priced, nonstreaming basic Anthropic web
search tool on Haiku 5.5. Unsupported pricing, caching, compaction, tool variants
and request shapes fail before transport. Default production behavior is unchanged.

The test service selects Haiku for core and dedicated Climate web research only.
Quality assessment and reviewer models remain Sonnet. Sonnet remains the normal
research default. This test therefore cannot establish Sonnet web-search quality.
The operator setting is `FCV_RESEARCH_MODEL=claude-haiku-5-5`; only that exact ID
or `claude-sonnet-5-5` is accepted. `/health` exposes the effective nonsecret model
selection. Haiku omits Sonnet's `between_tools` thinking option, including on a
paused-turn continuation.

Each web request reserves ten full one-million-token input contexts at Haiku's
highest published tier, ten output maxima at that tier, and the permitted search
fees. Only a complete, valid successful usage response can release unused web
reservation; failures retain the hold. Atomic SQLite reservations are shared
across clients. Plain-text reservations are never refunded. Settlement is
idempotent and cannot create a new allowance.

The ten-iteration bound uses Anthropic's documented current default server-tool
loop, with no loop-changing feature enabled. It is a versioned API assumption,
not a provider billing-account limit. Recheck it before reusing this pilot mode
after provider changes. Prices and bounds were checked on 27 October:
[Haiku specifications and tier prices](https://platform.claude.com/docs/en/models/haiku-5-5/overview),
[server-loop stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons),
[web-search pricing](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool).

Render's ephemeral ledger does not survive replacement deployments. Before a
Quality-mode redeploy, retain all Smoke charges and unresolved reservations and
subtract them from the new phase allowance. Never reissue the original USD15.
Restore the one-microUSD blocker after testing.

## Acceptance gates

Before spending: focused guard/configuration tests, independent review, one full
offline suite, diff/ancestry/pin checks, push, and exact deployed SHA/mode checks.
Consume a unique local start lock before the first upload helper.

Smoke must complete the pipeline and demonstrate actual research behavior and
bank provenance before Quality. Preserve fallback and source-gate diagnostics;
a live-mode setting alone is not proof that web evidence was admitted.

For the final run, inspect Summary and a non-first priority, Detailed browser HTML,
standalone HTML, DOCX, review packet hashes and saved-session restoration. Inspect
the actual Word layout and consequential project/source assertions. Record
reviewer verdicts and retained limitations honestly; model success does not
certify factual accuracy. Named human review remains required before sharing.

Fresh verification and test results will be recorded below when available.

## Unpaid verification completed

- Full standard PDF: eight pages, 21,988 extracted characters, expected SHA256;
  deterministic routing PID/IPF/single-country, with genuine MPA context.
- Default pinned bank: 146 countries, 344 identifiers, 438 final prompts and 438
  supplementary-search contexts checked with network and provider calls blocked.
  Source checksum remains
  `e72a1c766cedcd8e6a8eefa2a040afca082d34eff4a0f596e97e73fd11daf4bf`.
- Research configuration and existing core/Climate research tests: 100 passed in
  69.79 seconds, using local fake providers and normal Windows process permissions.
- Legacy and web budget guard tests: 69 passed in 9.17 seconds. A regression
  reproduced acceptance of a nested cache annotation before the targeted fix.
  Independent review found no remaining blocker in the Climate-active test path.
- Full offline app suite: 2,051 passed, two skipped and the same four documented
  hanging Chromium tests deselected, in 292.38 seconds with normal Windows process
  permissions. This includes the final caching regression and research settings.
- Immutable gitlink remains `daf594f8ca899a44bcea4e057a85b0d547ed9c33`.
  Word design/export files match the preserved design ancestor; both required
  design/integration commits remain ancestors. No submission lock exists yet.
