"""Conservative prepaid reservations for explicitly enabled preview calls.

The legacy text-only campaign retains its original no-refund reservation behavior.
The separate web-search mode is opt-in, ticketed, and settles only complete,
validated non-streaming responses. The SQLite ledger is local to this deployment;
operators must reconstruct and subtract prior charges/holds from logs after redeploy.
"""
from contextlib import closing
from pathlib import Path
import json
import os
import sqlite3
import uuid


LEGACY_LIMIT_MICROUSD = 6_000_000
WEB_LIMIT_MICROUSD = 15_000_000
WEB_CONTEXT_TOKENS = 1_000_000
# shortcut: reserve for the documented 10-iteration default; recheck after API or tool-loop changes.
WEB_MAX_ITERATIONS = 10  # https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons
WEB_MAX_INPUT_BYTES = 1_000_000

LEGACY_ALLOWED_FIELDS = {
    "model", "max_tokens", "messages", "system", "stream", "thinking",
    "output_config", "temperature", "top_p", "top_k", "stop_sequences",
    "metadata", "service_tier", "inference_geo",
}
WEB_ALLOWED_FIELDS = LEGACY_ALLOWED_FIELDS | {"tools", "tool_choice"}
TEXT_RATES = {
    "claude-sonnet-5-5": (20, 100),
    "claude-haiku-5-5": (5, 25),
    "claude-opus-5-5": (40, 200),
}  # tenths of a microdollar per token


class PilotBudgetExceeded(RuntimeError):
    """Request was not sent because its cost could not be safely reserved."""


class PilotSpendGuard:
    def __init__(self, path: Path, limit_microusd: int, *, allow_web_search: bool = False):
        self.allow_web_search = allow_web_search
        self.mode = "web" if allow_web_search else "legacy"
        maximum = WEB_LIMIT_MICROUSD if allow_web_search else LEGACY_LIMIT_MICROUSD
        if (type(limit_microusd) is not int or not 0 < limit_microusd <= maximum
                or type(allow_web_search) is not bool):
            raise ValueError(f"Pilot allowance must be positive and at most USD{maximum / 1_000_000:g}")
        self.path = Path(path)
        self._initialize_ledger(limit_microusd)

    def _initialize_ledger(self, limit_microusd: int):
        with closing(sqlite3.connect(self.path, timeout=30)) as db:
            db.execute("BEGIN IMMEDIATE")
            exists = db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='budget'"
            ).fetchone()
            if not exists:
                db.execute(
                    "CREATE TABLE budget (id INTEGER PRIMARY KEY CHECK(id=1), "
                    "ceiling INTEGER NOT NULL, reserved INTEGER NOT NULL, "
                    "mode TEXT NOT NULL, blocked INTEGER NOT NULL DEFAULT 0)"
                )
                db.execute(
                    "INSERT INTO budget (id, ceiling, reserved, mode, blocked) "
                    "VALUES (1, ?, 0, ?, 0)",
                    (limit_microusd, self.mode),
                )
            else:
                columns = {row[1] for row in db.execute("PRAGMA table_info(budget)")}
                # The historical ledger has no mode marker. It may be safely
                # upgraded for legacy use, but must never be treated as fresh web funds.
                if "mode" not in columns:
                    if self.allow_web_search:
                        raise ValueError("A legacy ledger cannot be opened in web-search mode")
                    db.execute(
                        "ALTER TABLE budget ADD COLUMN mode TEXT NOT NULL DEFAULT 'legacy'"
                    )
                    columns.add("mode")
                if "blocked" not in columns:
                    db.execute(
                        "ALTER TABLE budget ADD COLUMN blocked INTEGER NOT NULL DEFAULT 0"
                    )
                row = db.execute(
                    "SELECT ceiling, mode FROM budget WHERE id=1"
                ).fetchone()
                if row is None or row[0] != limit_microusd:
                    raise ValueError("Existing campaign allowance differs; do not reset the ledger")
                if row[1] != self.mode:
                    raise ValueError("Existing campaign mode differs; use a fresh ledger")

            if self.allow_web_search:
                db.execute(
                    "CREATE TABLE IF NOT EXISTS web_tickets ("
                    "ticket_id TEXT PRIMARY KEY, held INTEGER NOT NULL, "
                    "max_uses INTEGER NOT NULL, status TEXT NOT NULL, actual INTEGER)"
                )
            db.commit()

    def reserved_microusd(self):
        with closing(sqlite3.connect(self.path)) as db:
            return db.execute("SELECT reserved FROM budget WHERE id=1").fetchone()[0]

    def __call__(self, request):
        # Only the first-party Messages API is in scope.
        if request.url.host != "api.anthropic.com" or request.url.path != "/v1/messages":
            raise PilotBudgetExceeded("Pilot permits only first-party Messages requests")
        try:
            raw = request.read()
            body = json.loads(raw)
        except Exception as exc:
            raise PilotBudgetExceeded("Cannot inspect provider request") from exc
        if not isinstance(body, dict):
            raise PilotBudgetExceeded("Unknown request fields are not budgeted")

        if self.allow_web_search and ("tools" in body or "tool_choice" in body):
            self._reserve_web_request(request, raw, body)
            return
        self._reserve_text_request(raw, body)

    def _reserve_text_request(self, raw: bytes, body: dict):
        if set(body) - LEGACY_ALLOWED_FIELDS:
            raise PilotBudgetExceeded("Unknown request fields are not budgeted")
        model = body.get("model")
        output = body.get("max_tokens")
        if (model not in TEXT_RATES or type(output) is not int or not 0 < output <= 128000
                or body.get("tools") or body.get("service_tier", "auto") != "auto"
                or body.get("inference_geo", "global") != "global"
                or b'"cache_control"' in raw or b'"speed"' in raw):
            raise PilotBudgetExceeded("Unbounded or unsupported pilot request pricing")

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
                or any(not isinstance(message, dict) or set(message) != {"role", "content"}
                       or message["role"] not in {"user", "assistant"}
                       or not text_only(message["content"]) for message in messages)):
            raise PilotBudgetExceeded("Only text inputs are allowed in the pilot")

        input_rate, output_rate = TEXT_RATES[model]
        reserve = (2 * (len(raw) + 4096) * input_rate + output * output_rate + 9) // 10
        ceiling, used = self._reserve_ledger(reserve)
        print(
            f"PILOT_BUDGET charged_delta_microusd={reserve} "
            f"reserved_microusd={used + reserve} ceiling_microusd={ceiling}",
            flush=True,
        )

    def _reserve_web_request(self, request, raw: bytes, body: dict):
        if not self.allow_web_search:
            raise PilotBudgetExceeded("Web search is disabled for this pilot ledger")
        if set(body) - WEB_ALLOWED_FIELDS:
            raise PilotBudgetExceeded("Unknown request fields are not budgeted")
        if (b'"cache_control"' in raw or body.get("model") != "claude-haiku-5-5"
                or type(body.get("max_tokens")) is not int
                or not 0 < body["max_tokens"] <= 128000
                or body.get("stream", False) is not False
                or body.get("service_tier", "auto") != "auto"
                or body.get("inference_geo", "global") != "global"
                or len(raw) > WEB_MAX_INPUT_BYTES):
            raise PilotBudgetExceeded("Web search requires bounded non-streaming Haiku requests")
        beta = request.headers.get("anthropic-beta")
        if beta not in (None, "web-search-2025-03-05"):
            raise PilotBudgetExceeded("Unknown Anthropic beta features are not budgeted")

        # Haiku 5.5 supports adaptive or disabled thinking. In particular,
        # between_tools is unsupported and cannot be accepted as a billable call.
        thinking = body.get("thinking")
        if thinking is not None and (
                not isinstance(thinking, dict) or set(thinking) != {"type"}
                or thinking["type"] not in {"adaptive", "disabled"}):
            raise PilotBudgetExceeded("Unsupported Haiku thinking configuration")

        tools = body.get("tools")
        if not isinstance(tools, list) or len(tools) != 1 or not isinstance(tools[0], dict):
            raise PilotBudgetExceeded("Exactly one native web_search tool is permitted")
        tool = tools[0]
        if set(tool) - {"type", "name", "max_uses", "allowed_domains"}:
            raise PilotBudgetExceeded("Unknown web-search tool fields are not budgeted")
        max_uses = tool.get("max_uses")
        domains = tool.get("allowed_domains")
        if (tool.get("type") != "web_search_20250305" or tool.get("name") != "web_search"
                or type(max_uses) is not int or not 1 <= max_uses <= 3
                or (domains is not None and (not isinstance(domains, list)
                                             or any(not isinstance(domain, str) for domain in domains)))):
            raise PilotBudgetExceeded("Unsupported web-search tool configuration")
        choice = body.get("tool_choice")
        if choice is not None and (not isinstance(choice, dict) or choice != {"type": "auto"}):
            raise PilotBudgetExceeded("Only automatic native tool selection is budgeted")
        if not self._valid_web_messages(body):
            raise PilotBudgetExceeded("Web requests may contain only text and native web-search continuations")

        # Input can be reprocessed when server tools append results. Reserve for
        # ten full model contexts and maximum output on every iteration, plus the
        # separately priced server search uses. Rates are conservative Haiku 5.5
        # ceilings: $0.50/M input and $2.50/M output, represented in tenths of a
        # microdollar per token. Integer ceiling avoids rounding down.
        reserve = (
            (WEB_MAX_ITERATIONS * WEB_CONTEXT_TOKENS * 5
             + WEB_MAX_ITERATIONS * body["max_tokens"] * 25 + 9) // 10
            + max_uses * 10_000
        )
        ticket_id = uuid.uuid4().hex
        ceiling, used = self._reserve_ledger(
            reserve, ticket=(ticket_id, max_uses)
        )
        request.extensions["pilot_web_ticket"] = ticket_id
        print(
            f"PILOT_WEB_HOLD ticket_id={ticket_id} held_microusd={reserve} "
            f"reserved_microusd={used + reserve} ceiling_microusd={ceiling}",
            flush=True,
        )

    def _valid_web_messages(self, body: dict) -> bool:
        if not self._text_content(body.get("system", "")):
            return False
        messages = body.get("messages")
        if not isinstance(messages, list) or not messages:
            return False
        for message in messages:
            if (not isinstance(message, dict) or set(message) != {"role", "content"}
                    or message["role"] not in {"user", "assistant"}):
                return False
            if message["role"] == "user":
                if not self._text_content(message["content"]):
                    return False
            elif not self._assistant_content(message["content"]):
                return False
        return True

    @staticmethod
    def _text_content(content):
        if isinstance(content, str):
            return True
        return isinstance(content, list) and all(
            isinstance(block, dict) and set(block) == {"type", "text"}
            and block["type"] == "text" and isinstance(block["text"], str)
            for block in content
        )

    @classmethod
    def _assistant_content(cls, content):
        if isinstance(content, str):
            return True
        return isinstance(content, list) and all(cls._assistant_block(block) for block in content)

    @classmethod
    def _assistant_block(cls, block):
        if not isinstance(block, dict):
            return False
        kind = block.get("type")
        if kind == "text":
            return isinstance(block.get("text"), str)
        if kind == "thinking":
            return isinstance(block.get("thinking"), str)
        if kind == "redacted_thinking":
            return isinstance(block.get("data"), str)
        if kind == "server_tool_use":
            return (isinstance(block.get("id"), str)
                    and block.get("name") == "web_search"
                    and isinstance(block.get("input"), dict)
                    and set(block["input"]) == {"query"}
                    and isinstance(block["input"].get("query"), str))
        if kind == "web_search_tool_result":
            content = block.get("content")
            return (
                isinstance(block.get("tool_use_id"), str)
                and ((isinstance(content, dict)
                      and content.get("type") == "web_search_tool_result_error")
                     or (isinstance(content, list)
                         and all(isinstance(result, dict)
                                 and result.get("type") == "web_search_result"
                                 for result in content)))
            )
        return False

    def _reserve_ledger(self, reserve: int, ticket=None):
        with closing(sqlite3.connect(self.path, timeout=30)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            ceiling, used, blocked = db.execute(
                "SELECT ceiling, reserved, blocked FROM budget WHERE id=1"
            ).fetchone()
            if blocked:
                raise PilotBudgetExceeded("Pilot ledger is blocked after a pricing-bound breach")
            if used + reserve > ceiling:
                raise PilotBudgetExceeded("Pilot budget exhausted before provider request")
            db.execute("UPDATE budget SET reserved=reserved+? WHERE id=1", (reserve,))
            if ticket:
                db.execute(
                    "INSERT INTO web_tickets (ticket_id, held, max_uses, status, actual) "
                    "VALUES (?, ?, ?, 'held', NULL)",
                    (ticket[0], reserve, ticket[1]),
                )
        return ceiling, used

    def response_hook(self, response):
        """Settle only complete, validated web responses; all other holds remain."""
        request = response.request
        ticket_id = request.extensions.get("pilot_web_ticket")
        if not ticket_id or response.status_code != 200:
            return
        try:
            response.read()
            message = json.loads(response.content)
        except Exception:
            return
        content = message.get("content") if isinstance(message, dict) else None
        if (not isinstance(message, dict) or message.get("type") != "message"
                or not isinstance(message.get("id"), str)
                or message.get("role") != "assistant"
                or message.get("model") != "claude-haiku-5-5"
                or message.get("stop_reason") not in {
                    "end_turn", "max_tokens", "pause_turn", "stop_sequence",
                    "tool_use", "refusal", "model_context_window_exceeded",
                }
                or not isinstance(content, list)
                or not self._assistant_content(content)):
            return
        has_search_call = any(
            block.get("type") == "server_tool_use" and block.get("name") == "web_search"
            for block in content
        )
        usage = message.get("usage")
        if not isinstance(usage, dict):
            return
        allowed_usage = {
            "input_tokens", "output_tokens", "cache_creation",
            "cache_creation_input_tokens", "cache_read_input_tokens", "inference_geo",
            "output_tokens_details", "server_tool_use", "service_tier", "speed",
        }
        if set(usage) - allowed_usage:
            return
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        cache_fields = ("cache_creation_input_tokens", "cache_read_input_tokens")
        if (type(input_tokens) is not int or input_tokens < 0
                or type(output_tokens) is not int or output_tokens < 0
                or any(usage.get(field) is not None
                       and (type(usage[field]) is not int or usage[field] != 0)
                       for field in cache_fields)
                or usage.get("service_tier") not in {None, "standard", "auto"}
                or usage.get("inference_geo") not in {None, "global"}
                or usage.get("speed") not in {None, "standard"}):
            return
        cache_creation = usage.get("cache_creation")
        if (cache_creation is not None
                and (not isinstance(cache_creation, dict)
                     or set(cache_creation) - {"ephemeral_5m_input_tokens", "ephemeral_1h_input_tokens"}
                     or any(type(tokens) is not int or tokens != 0
                            for tokens in cache_creation.values()))):
            return
        output_details = usage.get("output_tokens_details")
        if (output_details is not None
                and (not isinstance(output_details, dict)
                     or set(output_details) - {"thinking_tokens"}
                     or type(output_details.get("thinking_tokens", 0)) is not int
                     or output_details.get("thinking_tokens", 0) < 0)):
            return
        server_usage = usage.get("server_tool_use")
        if server_usage is None:
            searches = fetches = 0
        elif (not isinstance(server_usage, dict)
              or set(server_usage) - {"web_search_requests", "web_fetch_requests"}):
            return
        else:
            searches = server_usage.get("web_search_requests", 0)
            fetches = server_usage.get("web_fetch_requests", 0)
        if (type(searches) is not int or searches < 0
                or type(fetches) is not int or fetches != 0
                or (has_search_call and searches == 0)):
            return

        with closing(sqlite3.connect(self.path, timeout=30)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            ticket = db.execute(
                "SELECT held, max_uses, status FROM web_tickets WHERE ticket_id=?",
                (ticket_id,),
            ).fetchone()
            if ticket is None or ticket[2] != "held":
                return
            held, max_uses, _status = ticket
            if searches > max_uses:
                return
            # Haiku 5.5 high-tier input/output rates, rounded up to a microdollar;
            # each performed web search adds its separately priced $0.01 charge.
            actual = (input_tokens * 5 + output_tokens * 25 + 9) // 10 + searches * 10_000
            reserved = db.execute("SELECT reserved FROM budget WHERE id=1").fetchone()[0]
            if actual <= held:
                new_reserved = reserved - (held - actual)
                db.execute("UPDATE budget SET reserved=? WHERE id=1", (new_reserved,))
                db.execute(
                    "UPDATE web_tickets SET status='settled', actual=? WHERE ticket_id=?",
                    (actual, ticket_id),
                )
                ceiling = db.execute("SELECT ceiling FROM budget WHERE id=1").fetchone()[0]
                print(
                    f"PILOT_WEB_SETTLED ticket_id={ticket_id} charged_microusd={actual} "
                    f"reserved_microusd={new_reserved} ceiling_microusd={ceiling}",
                    flush=True,
                )
                return

            new_reserved = reserved + (actual - held)
            db.execute(
                "UPDATE budget SET reserved=?, blocked=1 WHERE id=1", (new_reserved,)
            )
            db.execute(
                "UPDATE web_tickets SET status='overrun', actual=? WHERE ticket_id=?",
                (actual, ticket_id),
            )
            ceiling = db.execute("SELECT ceiling FROM budget WHERE id=1").fetchone()[0]
            print(
                f"PILOT_WEB_BREACH ticket_id={ticket_id} held_microusd={held} "
                f"charged_microusd={actual} reserved_microusd={new_reserved} "
                f"ceiling_microusd={ceiling}",
                flush=True,
            )
        raise PilotBudgetExceeded("Reported web usage exceeded its reserved pricing bound")


def pilot_http_client():
    """Return SDK kwargs only when the operator explicitly enables the guard."""
    web_setting = os.environ.get("FCV_PILOT_ALLOW_WEB_SEARCH")
    if web_setting not in (None, "0", "1"):
        raise ValueError("FCV_PILOT_ALLOW_WEB_SEARCH must be unset, 0, or 1")
    allow_web = web_setting == "1"
    ceiling = os.environ.get("FCV_PILOT_BUDGET_MICROUSD")
    path = os.environ.get("FCV_PILOT_BUDGET_DB")
    if not ceiling and not path:
        if allow_web:
            raise ValueError("Web-search opt-in requires both pilot budget settings")
        return {}
    if not ceiling or not path or not ceiling.isdigit():
        raise ValueError("Both pilot budget settings are required and the ceiling must be an integer")

    import httpx
    guard = PilotSpendGuard(Path(path), int(ceiling), allow_web_search=allow_web)
    hooks = {"request": [guard]}
    if allow_web:
        hooks["response"] = [guard.response_hook]
    return {"http_client": httpx.Client(event_hooks=hooks)}
