"""Opt-in, conservative prepaid reservations for a single preview campaign.

No refunds: failed attempts and retries retain their full reservation. The SQLite
ledger survives worker restarts, not replacement of Render's ephemeral filesystem.
After a redeploy, the operator must subtract all prior reservations from the new
limit. Never reuse a fresh ledger to repeat a campaign's original allowance.
"""
from pathlib import Path
from contextlib import closing
import json
import os
import sqlite3


class PilotBudgetExceeded(RuntimeError):
    """Request was not sent because its cost could not be safely reserved."""


class PilotSpendGuard:
    def __init__(self, path: Path, limit_microusd: int):
        if type(limit_microusd) is not int or not 0 < limit_microusd <= 6_000_000:
            raise ValueError("Pilot allowance must be positive and at most USD6")
        self.path = Path(path)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY CHECK(id=1), ceiling INTEGER, reserved INTEGER)")
            db.execute("INSERT OR IGNORE INTO budget VALUES (1, ?, 0)", (limit_microusd,))
            if db.execute("SELECT ceiling FROM budget WHERE id=1").fetchone()[0] != limit_microusd:
                raise ValueError("Existing campaign allowance differs; do not reset the ledger")

    def reserved_microusd(self):
        with closing(sqlite3.connect(self.path)) as db:
            return db.execute("SELECT reserved FROM budget WHERE id=1").fetchone()[0]

    def __call__(self, request):
        # Only the first-party Messages API and known plain-text pricing are allowed.
        if request.url.host != "api.anthropic.com" or request.url.path != "/v1/messages":
            raise PilotBudgetExceeded("Pilot permits only first-party Messages requests")
        try:
            raw = request.read()
            body = json.loads(raw)
        except Exception as exc:
            raise PilotBudgetExceeded("Cannot inspect provider request") from exc
        allowed = {"model", "max_tokens", "messages", "system", "stream", "thinking",
                   "output_config", "temperature", "top_p", "top_k", "stop_sequences",
                   "metadata", "service_tier", "inference_geo"}
        if not isinstance(body, dict) or set(body) - allowed:
            raise PilotBudgetExceeded("Unknown request fields are not budgeted")
        rates = {"claude-sonnet-5-5": (20, 100), "claude-haiku-5-5": (5, 25),
                 "claude-opus-5-5": (40, 200)}  # tenths of a microdollar/token
        model = body.get("model")
        output = body.get("max_tokens")
        if (model not in rates or type(output) is not int or not 0 < output <= 128000
                or body.get("tools") or body.get("service_tier", "auto") != "auto"
                or body.get("inference_geo", "global") != "global"
                or b'"cache_control"' in raw or b'"speed"' in raw):
            raise PilotBudgetExceeded("Unbounded or unsupported pilot request pricing")
        # No images, documents or remote tool results: UTF-8 bytes conservatively
        # bound text tokens; double input plus framing headroom. Output already
        # has a provider-enforced max_tokens ceiling, so reserve that ceiling once.
        def text_only(value):
            if isinstance(value, str):
                return True
            return isinstance(value, list) and all(
                isinstance(block, dict) and set(block) == {"type", "text"}
                and block["type"] == "text" and isinstance(block["text"], str)
                for block in value
            )
        messages = body.get("messages")
        if (not isinstance(messages, list) or not messages
                or not text_only(body.get("system", ""))
                or any(not isinstance(m, dict) or set(m) != {"role", "content"}
                       or m["role"] not in {"user", "assistant"}
                       or not text_only(m["content"]) for m in messages)):
            raise PilotBudgetExceeded("Only text inputs are allowed in the pilot")
        input_rate, output_rate = rates[model]
        reserve = (2 * (len(raw) + 4096) * input_rate + output * output_rate + 9) // 10
        with closing(sqlite3.connect(self.path, timeout=30)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            ceiling, used = db.execute("SELECT ceiling, reserved FROM budget WHERE id=1").fetchone()
            if used + reserve > ceiling:
                raise PilotBudgetExceeded("Pilot budget exhausted before provider request")
            db.execute("UPDATE budget SET reserved=reserved+? WHERE id=1", (reserve,))
        print(f"PILOT_BUDGET reserved_microusd={used + reserve} ceiling_microusd={ceiling}", flush=True)


def pilot_http_client():
    """Return SDK kwargs only when the operator explicitly enables the guard."""
    ceiling = os.environ.get("FCV_PILOT_BUDGET_MICROUSD")
    path = os.environ.get("FCV_PILOT_BUDGET_DB")
    if not ceiling and not path:
        return {}
    if not ceiling or not path:
        raise ValueError("Both pilot budget settings are required")
    import httpx
    guard = PilotSpendGuard(Path(path), int(ceiling))
    return {"http_client": httpx.Client(event_hooks={"request": [guard]})}
