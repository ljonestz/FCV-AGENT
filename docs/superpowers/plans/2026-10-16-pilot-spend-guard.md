# Preview campaign spend guard

User authorized one smoke-and-quality test with a total USD5 ceiling in the
existing isolated Render test service. Add an opt-in HTTP request hook to all
four Anthropic clients. Before each attempt reserve full text request bytes plus
4096 framing tokens and max output at known prices with a 2x margin. Block unknown
models, server tools, caching, non-global routing and nontext inputs before send.
Use SQLite atomic reservations shared across clients; never refund failed or
completed attempts. Default off leaves production unchanged. Ledger survives
worker restarts but not Render redeploys: phase allowances must sum to <=USD5;
never reissue the full allowance after a redeploy. No claims of independent
analytical acceptance follow from this operational test.

Verification: failing import first; exact-limit, retry/restart, concurrent
reservation, transport rejection, unsupported-price and four-client integration
tests. Connected runtime/export tests, read-only review, then full suite.
Deployment: existing free preview only, explicit phase budget and DB path,
verify SHA and health before any upload. If guard blocks a required call, report
incomplete assessment; do not evade it or automatically spend a second allowance.
