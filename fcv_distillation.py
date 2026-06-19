"""Secondary-document distillation for the FCV Project Screener.

Primary project documents are still read through the normal Stage 1 path. This
module only handles secondary package/context documents by turning each one into
a compact, traceable card before Stage 1 receives it.
"""
from __future__ import annotations

import concurrent.futures
import json
import time
from typing import Any


CARD_CHARS_2A = 2_800
CARD_CHARS_2B = 1_200
CARD_CHARS_CONTEXT = 1_800

SECONDARY_CARD_BUDGET_CHARS = 32_000
CONTEXT_RESERVE_CHARS = 7_000

DISTILL_MAX_TOKENS = 900
DISTILL_TIMEOUT_SECONDS = 22
DISTILL_MAX_WORKERS = 4
DISTILL_POLL_SECONDS = 2
CONFIDENCE_FLOOR = 0.65

HAIKU_MODEL = "claude-haiku-4-5-20251001"

TIER_2A_TYPES = {
    "policy_matrix",
    "dli_matrix",
    "sort",
    "escp",
    "sep",
    "results_framework",
}
PACKAGE_TYPES = TIER_2A_TYPES | {"package_other"}
CONTEXT_TYPES = {"rra", "cpf", "other_context"}

TYPE_LABELS = {
    "policy_matrix": "Policy Matrix / Prior Actions",
    "dli_matrix": "DLI Matrix / PAP",
    "sort": "SORT",
    "escp": "ESCP / ESRS",
    "sep": "SEP",
    "results_framework": "Results Framework",
    "package_other": "Project Package (other)",
    "rra": "RRA",
    "cpf": "CPF / CEN",
    "other_context": "Context (other)",
}


def _schema_instructions(role: str) -> str:
    if role == "context":
        allowed = "rra, cpf, other_context"
        schema = (
            "Then extract by detected_type:\n"
            "- rra: `drivers` = ranked top conflict drivers as short strings; "
            "`at_risk` = at-risk groups and geographies as short strings.\n"
            "- cpf: `pillars` = core pillars, focus areas, or higher-level "
            "objectives as short strings.\n"
            "- other_context: `key_facts` = 5-8 FCV-relevant facts as short "
            "strings, or ['No FCV-relevant content found'].\n"
        )
    else:
        allowed = (
            "policy_matrix, dli_matrix, sort, escp, sep, "
            "results_framework, package_other"
        )
        schema = (
            "Then extract by detected_type:\n"
            "- policy_matrix: `items` = prior actions or triggers as "
            "'<policy area>: <one-line description>'; prefix '[FCV] ' when a "
            "distributional, exclusion, or conflict-sensitivity angle is present.\n"
            "- dli_matrix: `items` = DLIs as '<indicator> | target: <t> | "
            "verification: <v>'; add FCV-relevant PAP actions prefixed '[PAP] '.\n"
            "- sort: `ratings` = '<risk category>: <rating>' strings, quoting "
            "political and governance, security, and FCV/fragility ratings; "
            "`notes` = one line per high/substantial rating where rationale is given.\n"
            "- escp: `commitments` = key E&S commitments; `sea_sh` = SEA/SH "
            "risk rating and mitigation commitments; include security-of-personnel "
            "and labour-influx items when present.\n"
            "- sep: `grm` = grievance mechanism design and accessibility; "
            "`inclusion` = vulnerable/excluded-group engagement provisions; "
            "`access` = stakeholder-access constraints.\n"
            "- results_framework: `indicators` = PDO-level and FCV-sensitive "
            "intermediate indicators with baselines/targets where present.\n"
            "- package_other: `key_facts` = 5-8 FCV-relevant facts as short "
            "strings, or ['No FCV-relevant content found'].\n"
        )

    return (
        "You are distilling ONE supporting document for an FCV screening tool. "
        "Do not assess the document. Extract only what is present in the text. "
        "Do not invent, infer beyond the text, or use outside knowledge.\n\n"
        f"First classify `detected_type` as one of: {allowed}. "
        "Also return `confidence` from 0.0 to 1.0 for that classification.\n\n"
        f"{schema}\n"
        "Return ONLY one JSON object with keys: detected_type, confidence, and "
        "the extraction fields named above for that type. No prose and no "
        "markdown fences."
    )


def _card_cap_for_tier(tier: str) -> int:
    return {
        "2A": CARD_CHARS_2A,
        "2B": CARD_CHARS_2B,
        "context": CARD_CHARS_CONTEXT,
    }.get(tier, CARD_CHARS_2B)


def _role_for(dp: dict[str, Any]) -> str:
    return "context" if dp.get("label") == "CONTEXT DOCUMENT" else "package"


def _normalise_type(detected_type: str, role: str, confidence: float) -> str:
    detected_type = (detected_type or "").strip().lower()
    if role == "context":
        if detected_type not in CONTEXT_TYPES or confidence < CONFIDENCE_FLOOR:
            return "other_context"
        return detected_type
    if detected_type not in PACKAGE_TYPES:
        return "package_other"
    if detected_type in TIER_2A_TYPES and confidence < CONFIDENCE_FLOOR:
        return "package_other"
    return detected_type


def _tier_for(detected_type: str, role: str) -> str:
    if role == "context":
        return "context"
    if detected_type in TIER_2A_TYPES:
        return "2A"
    return "2B"


def _coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _render_card(name: str, detected_type: str, tier: str, fields: dict[str, Any]) -> str:
    label = TYPE_LABELS.get(detected_type, detected_type or "Document")
    lines = [f"Source: {name}", f"[Detected: {label}]"]

    def add_bullets(title: str, items: Any) -> None:
        values = _coerce_list(items)
        if not values:
            return
        lines.append(f"{title}:")
        for item in values:
            lines.append(f"  - {item}")

    add_bullets("CONFLICT DRIVERS", fields.get("drivers"))
    add_bullets("AT-RISK GROUPS / GEOGRAPHIES", fields.get("at_risk"))
    add_bullets("CPF PILLARS", fields.get("pillars"))
    if detected_type in {"policy_matrix", "dli_matrix"}:
        add_bullets("PRIOR ACTIONS / TRIGGERS", fields.get("items"))
    add_bullets("RISK RATINGS", fields.get("ratings"))
    add_bullets("RATING NOTES", fields.get("notes"))
    add_bullets("E&S COMMITMENTS", fields.get("commitments"))
    add_bullets("SEA/SH", fields.get("sea_sh"))
    add_bullets("GRM", fields.get("grm"))
    add_bullets("INCLUSION", fields.get("inclusion"))
    add_bullets("STAKEHOLDER ACCESS", fields.get("access"))
    add_bullets("FCV-SENSITIVE INDICATORS", fields.get("indicators"))
    add_bullets("KEY FACTS", fields.get("key_facts"))

    if len(lines) == 2:
        lines.append("KEY FACTS:")
        lines.append("  - No structured content extracted.")

    text = "\n".join(lines).strip()
    cap = _card_cap_for_tier(tier)
    if len(text) > cap:
        text = text[:cap].rstrip() + "\n  - [card truncated to fit budget]"
    return text


def _parse_json_response(raw: str) -> dict[str, Any]:
    raw = (raw or "").strip()
    if raw.startswith("```"):
        raw = raw.strip("`").strip()
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end < start:
        return {}
    return json.loads(raw[start:end + 1])


def _distill_one(dp: dict[str, Any], api_client: Any) -> dict[str, Any]:
    role = _role_for(dp)
    name = dp.get("name", "document")
    snippet = (dp.get("raw_text") or "")[:24_000]
    try:
        response = api_client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=DISTILL_MAX_TOKENS,
            messages=[{
                "role": "user",
                "content": (
                    _schema_instructions(role) +
                    "\n\n--- DOCUMENT START ---\n" +
                    snippet
                ),
            }],
        )
        raw = response.content[0].text.strip()
        data = _parse_json_response(raw)
        try:
            confidence = float(data.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0
        detected_type = _normalise_type(
            str(data.get("detected_type", "")), role, confidence
        )
        tier = _tier_for(detected_type, role)
        card = _render_card(name, detected_type, tier, data)
        return {
            "name": name,
            "role": role,
            "detected_type": detected_type,
            "confidence": confidence,
            "tier": tier,
            "card": card,
            "chars": len(card),
            "failed": False,
        }
    except Exception as exc:  # noqa: BLE001 - one failed doc must not sink Stage 1.
        return _failure_result(dp, str(exc)[:200])


def _failure_result(dp: dict[str, Any], error: str) -> dict[str, Any]:
    return {
        "name": dp.get("name", "document"),
        "role": _role_for(dp),
        "detected_type": "other_context" if _role_for(dp) == "context" else "package_other",
        "confidence": 0.0,
        "tier": "context" if _role_for(dp) == "context" else "2B",
        "card": None,
        "chars": 0,
        "failed": True,
        "error": error,
    }


def _apply_budget(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    context = [r for r in results if r["role"] == "context"]
    package_2a = [r for r in results if r["role"] == "package" and r["tier"] == "2A"]
    package_2b = [r for r in results if r["role"] == "package" and r["tier"] == "2B"]

    spent_total = 0
    spent_context = 0

    def keep_or_mark(result: dict[str, Any], reserve_context: bool = False) -> None:
        nonlocal spent_context, spent_total
        if result["failed"]:
            result["overflow_reason"] = "distillation_failed"
            return
        if reserve_context and spent_context + result["chars"] <= CONTEXT_RESERVE_CHARS:
            spent_context += result["chars"]
            spent_total += result["chars"]
            result["overflow_reason"] = None
            return
        if spent_total + result["chars"] <= SECONDARY_CARD_BUDGET_CHARS:
            spent_total += result["chars"]
            result["overflow_reason"] = None
            return
        result["overflow_reason"] = "budget_reached"

    for result in context:
        keep_or_mark(result, reserve_context=True)
    for result in package_2a:
        keep_or_mark(result)
    for result in package_2b:
        keep_or_mark(result)
    return results


def _sse(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def _mark_result_on_doc_part(result: dict[str, Any], dp: dict[str, Any]) -> dict[str, Any] | None:
    reason = result.get("overflow_reason")
    dp["detected_type"] = result["detected_type"]
    dp["tier"] = result["tier"]
    dp["distilled"] = True
    dp["char_limit"] = _card_cap_for_tier(result["tier"])
    dp["overflow_reason"] = reason
    if reason == "distillation_failed":
        dp["raw_text"] = (
            "[Could not distill this document automatically - "
            f"included by name only: {result['name']}]"
        )
        return {"name": result["name"], "reason": "distillation_failed"}
    if reason == "budget_reached":
        dp["raw_text"] = (
            "[Uploaded, not distilled (secondary-document budget reached): "
            f"{result['name']}]"
        )
        return {"name": result["name"], "reason": "budget_reached"}
    dp["raw_text"] = result["card"] or f"[No content extracted: {result['name']}]"
    return None


def _collect_distillation_results(
    dps: list[dict[str, Any]],
    api_client: Any,
) -> list[dict[str, Any]]:
    max_workers = max(1, min(DISTILL_MAX_WORKERS, len(dps)))
    results_by_id: dict[int, dict[str, Any]] = {}
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    try:
        future_to_dp = {pool.submit(_distill_one, dp, api_client): dp for dp in dps}
        start_times = {future: time.monotonic() for future in future_to_dp}
        pending = set(future_to_dp)
        while pending:
            done, _ = concurrent.futures.wait(
                pending,
                timeout=DISTILL_POLL_SECONDS,
                return_when=concurrent.futures.FIRST_COMPLETED,
            )
            for future in done:
                pending.remove(future)
                dp = future_to_dp[future]
                try:
                    result = future.result()
                except Exception as exc:  # noqa: BLE001
                    result = _failure_result(dp, str(exc)[:200])
                results_by_id[id(dp)] = result

            now = time.monotonic()
            for future in list(pending):
                if now - start_times[future] >= DISTILL_TIMEOUT_SECONDS:
                    dp = future_to_dp[future]
                    future.cancel()
                    pending.remove(future)
                    results_by_id[id(dp)] = _failure_result(
                        dp, f"timed out after {DISTILL_TIMEOUT_SECONDS}s"
                    )
    finally:
        pool.shutdown(wait=False, cancel_futures=True)

    results = []
    for dp in dps:
        result = results_by_id.get(id(dp))
        if result is None:
            result = _failure_result(dp, "no distillation result")
        result["_dp"] = dp
        results.append(result)
    return results


def distill_doc_parts_stream(secondary_dps: list[dict[str, Any]], api_client: Any, executor: Any):
    """Distill secondary doc_parts in place, yielding SSE-ready progress events.

    The `executor` argument is accepted for compatibility with app.py integration.
    A private bounded pool is used internally so an assessment worker cannot
    starve the shared assessment executor while waiting for its own subtasks.
    """
    del executor
    dps = list(secondary_dps or [])
    if not dps:
        return

    yield _sse({
        "status": "preprocessing",
        "preprocessing": {"phase": "distilling", "total": len(dps)},
    })

    results = _collect_distillation_results(dps, api_client)
    for index, result in enumerate(results, start=1):
        yield _sse({
            "status": "preprocessing",
            "preprocessing": {
                "phase": "distilled_one",
                "name": result["name"],
                "detected_type": result["detected_type"],
                "done": index,
                "total": len(dps),
            },
        })

    _apply_budget(results)
    overflow = []
    for result in results:
        overflow_item = _mark_result_on_doc_part(result, result["_dp"])
        if overflow_item:
            overflow.append(overflow_item)

    yield _sse({
        "status": "preprocessing",
        "preprocessing": {
            "phase": "complete",
            "distilled": sum(1 for result in results if not result.get("overflow_reason")),
            "overflow": overflow,
        },
    })
