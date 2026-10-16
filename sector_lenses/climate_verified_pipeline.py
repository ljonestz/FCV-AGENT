"""Automatic, source-first orchestration for ``climate-verified-v2.1``.


The module deliberately accepts only structured model outputs.  Each stage is
normalized into the typed contracts, checked against stable IDs, and stripped
of invalid dependent objects before the next stage can use it.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import asdict, dataclass, replace
from typing import Protocol, Sequence

import climate_question_bank

from sector_lenses.climate_final_reader import (
    apply_reader_corrections, bind_same_passage_project_references, reader_support_records,
    reader_correction_allowed_numeric_date_tokens, validate_final_reader,
    reviewed_final_reader, normalize_reader_paragraphs,
)

from sector_lenses.climate_analysis import (
    ClimatePathway,
    ContextEvidenceRef,
    ExistingResponse,
    ResidualGap,
    validate_analysis_registers,
)
from sector_lenses.climate_judgments import (
    ClimateJudgments,
    Judgment,
    deterministic_summary,
    validate_judgments,
)
from sector_lenses.climate_operational_guidance import (
    GUIDANCE_REGISTRY_VERSION,
    select_operational_guidance,
)
from sector_lenses.climate_recommendations import (
    CandidateRecommendation,
    DraftingBlock,
    DraftingValidationContext,
    READINESS_CATEGORIES,
    RecommendationScore,
    ReviewReadinessFlag,
    _normalized_sentence,
    admit_and_rank,
    admission_failure_codes,
    admit_readiness_flags,
    normalize_drafting_blocks,
    numeric_tokens_in_text,
    normalize_unsupported_drafting_precision,
    normalize_optional_enhancement,
    normalize_recommendation_references,
    normalize_unverified_completion_actor,
    normalize_unverified_drafting_actor,
    normalize_unsupported_core_precision,
    unsupported_numeric_tokens,
    validate_recommendation,
)
from sector_lenses.climate_review_admission import reconcile_core_reviews
from sector_lenses.climate_run_manifest import RunManifest, safe_log_summary
from sector_lenses.climate_semantic_review import (
    ReviewRisk,
    semantic_review_required,
)
from sector_lenses.climate_source_blocks import SourceBlock, SourceDocument, cited_source_passages
from sector_lenses.climate_truth import (
    DerivedAssertion,
    ProjectFactClaim,
    normalize_fact_registry,
    validate_derived_assertions,
)
from sector_lenses.climate_verified_contracts import (
    CALL_BUDGETS,
    CLIMATE_VERIFIED_SCHEMA_VERSION,
    EpistemicStatus,
)
from sector_lenses.climate_verified_schemas import (
    SEMANTIC_REVIEW_REASON_CODES,
    validate_summary_fragment,
    validate_summary_overview,
)


# Document-integrity findings never use missing_operational_home (a design gap,
# not a document defect); align validation with the fact-stage prompt.
_INTEGRITY_CATEGORIES = READINESS_CATEGORIES - {"missing_operational_home"}

PROMPT_VERSIONS = {
    "fact_extraction": "climate-facts-v2.9",
    "bounded_analysis": "climate-analysis-v2.12",
    "judgment_review": "climate-judgments-v2.16",
    "recommendation_compiler": "climate-recommendations-v2.19",
    "conditional_review": "climate-review-v2.20",
    "drafting_compiler": "climate-drafting-v1.7",
    "reader_compiler": "climate-final-reader-v1.10",
    "reader_correction": "climate-reader-correction-v1.7",
    "reader_review": "climate-reader-review-v1.10",
}


class JsonClient(Protocol):
    def complete_json(
        self,
        *,
        stage: str,
        payload: dict[str, object],
        timeout_seconds: int,
        max_output_tokens: int,
        max_transient_retries: int,
    ) -> dict[str, object]: ...


@dataclass(frozen=True)
class PipelineClients:
    assessment: JsonClient
    reviewer: JsonClient


def _mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _diagnostic_snapshot(value: object) -> dict[str, object]:
    """Keep bounded replay evidence in the saved assessment, never application logs."""
    text = json.dumps(value, ensure_ascii=False)
    return {"json": text[:60000], "truncated": len(text) > 60000}


def _records(payload: dict[str, object], *names: str) -> list[dict[str, object]]:
    for name in names:
        value = payload.get(name)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _strings(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def _bounded_reason_codes(value: object) -> list[str]:
    codes: list[str] = []
    for item in _strings(value):
        code = item.upper()
        if (
            len(code) > 64
            or not code[0].isalpha()
            or not code.replace("_", "").isalnum()
        ):
            code = "SEMANTIC_REVIEW_REASON_INVALID"
        if code not in SEMANTIC_REVIEW_REASON_CODES:
            code = "SEMANTIC_REVIEW_REASON_INVALID"
        if code not in codes:
            codes.append(code)
        if len(codes) == 12:
            break
    return codes


def _valid_reader_revision(review: dict, final_reader: object) -> bool:
    """Reject incomplete diagnostics before spending the single text correction."""
    if review.get('verdict') != 'revise':
        return False
    issues, identifiers, codes = (review.get(key) for key in ('issues', 'object_ids', 'reason_codes'))
    if not all(isinstance(value, list) and 0 < len(value) <= 12
               for value in (issues, identifiers, codes)):
        return False
    if (not all(isinstance(identifier, str) for identifier in identifiers)
            or len(set(identifiers)) != len(identifiers)
            or not all(isinstance(code, str) and code in SEMANTIC_REVIEW_REASON_CODES for code in codes)):
        return False
    records = {}
    if isinstance(final_reader, dict):
        for record in (
            _records(final_reader, "summary_paragraphs")
            + _records(final_reader, "assessment_narratives")
        ):
            identifier = record.get("object_id")
            if isinstance(identifier, str):
                records[identifier] = record
    issue_ids, issue_codes = [], set()
    for issue in issues:
        if (not isinstance(issue, dict) or not isinstance(issue.get('object_id'), str)
                or not isinstance(issue.get('explanation'), str) or not issue['explanation'].strip()
                or not isinstance(issue.get('quoted_text'), str) or not issue['quoted_text'].strip()
                or not isinstance(issue.get('reason_codes'), list) or not issue['reason_codes']
                or not all(isinstance(code, str) and code in SEMANTIC_REVIEW_REASON_CODES
                           for code in issue['reason_codes'])):
            return False
        record = records.get(issue['object_id'])
        if record is None:
            return False
        texts = ([record.get('text')] if isinstance(record.get('text'), str)
                 else record.get('paragraphs'))
        if (not isinstance(texts, list)
                or not all(isinstance(text, str) for text in texts)
                or sum(issue['quoted_text'] in text for text in texts) != 1
                or not all(text.find(issue['quoted_text']) == text.rfind(issue['quoted_text'])
                           for text in texts)):
            return False
        issue_ids.append(issue['object_id'])
        issue_codes.update(issue['reason_codes'])
    return (len(set(issue_ids)) == len(issue_ids)
            and set(issue_ids) == set(identifiers) and issue_codes == set(codes))


def _text(value: object, default: str = "") -> str:
    cleaned = str(value or "").strip()
    return cleaned or default


def _as_record(value: object) -> dict[str, object]:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    return dict(value) if isinstance(value, dict) else {}



class PipelineCancelled(RuntimeError):
    """Cancellation is never converted into an optional-artifact fallback."""

def _call(
    client: JsonClient,
    stage: str,
    payload: dict[str, object],
    latency_ms: dict[str, int],
    *,
    cancel_event: object | None = None,
    deadline: float | None = None,
    optional: bool = False,
    repair_allowance: dict[str, int] | None = None,
) -> dict[str, object]:
    cancelled = getattr(cancel_event, "is_set", lambda: False)
    if cancelled():
        raise PipelineCancelled("Verified Climate-FCV pipeline cancelled")
    budget = CALL_BUDGETS[stage]
    remaining = (
        budget.timeout_seconds
        if deadline is None
        else min(budget.timeout_seconds, int(deadline - time.monotonic()))
    )
    if remaining < 1:
        if optional:
            return {'_optional_failure': 'TimeoutError'}
        raise TimeoutError("Verified Climate-FCV pipeline exceeded its wall-clock limit")
    output_tokens = budget.output_tokens
    if repair_allowance is not None:
        output_tokens = min(output_tokens, repair_allowance['remaining'])
        if output_tokens < 1:
            raise TimeoutError('Correction output-token allowance exhausted')
    started = time.monotonic()
    try:
        result = client.complete_json(
            stage=stage,
            payload=payload,
            timeout_seconds=remaining,
            max_output_tokens=output_tokens,
            max_transient_retries=0 if repair_allowance is not None else 1,
        )
    except Exception as error:
        if cancelled() or isinstance(error, PipelineCancelled) or (
            isinstance(error, RuntimeError) and str(error) == 'Verified Climate-FCV pipeline cancelled'
        ):
            raise PipelineCancelled('Verified Climate-FCV pipeline cancelled') from error
        if not optional:
            raise
        result = {'_optional_failure': type(error).__name__}
    finally:
        if repair_allowance is not None:
            used_tokens = getattr(client, 'last_output_tokens', None)
            # A production response supplies usage. An opaque client consumes the
            # full requested allowance conservatively; never invent a token estimate.
            charged = used_tokens if isinstance(used_tokens, int) and used_tokens >= 0 else output_tokens
            repair_allowance['remaining'] = max(0, repair_allowance['remaining'] - charged)

    latency_ms[stage] = latency_ms.get(stage, 0) + int((time.monotonic() - started) * 1000)
    if cancelled():
        raise PipelineCancelled("Verified Climate-FCV pipeline cancelled")
    if not isinstance(result, dict):
        raise ValueError(f"{stage} must return a JSON object")
    return result


def _fact(record: dict[str, object]) -> ProjectFactClaim:
    return ProjectFactClaim(
        claim_id=_text(record.get("claim_id")),
        claim_type=_text(record.get("claim_type"), "unresolved"),
        subject=_text(record.get("subject")),
        predicate=_text(record.get("predicate")),
        object_value=_text(record.get("object_value", record.get("object"))),
        epistemic_status=_text(
            record.get("epistemic_status", record.get("status")),
            EpistemicStatus.NOT_FOUND.value,
        ),
        source_block_ids=_strings(record.get("source_block_ids")),
        supporting_excerpt=(
            _text(record.get("supporting_excerpt")) or None
        ),
        confidence=_text(record.get("confidence"), "low"),
    )


def _assertion(record: dict[str, object]) -> DerivedAssertion:
    return DerivedAssertion(
        assertion_id=_text(record.get("assertion_id")),
        assertion_type=_text(record.get("assertion_type"), "analytical"),
        statement=_text(record.get("statement")),
        input_fact_ids=_strings(record.get("input_fact_ids")),
        derivation_method=_text(record.get("derivation_method"), "semantic"),
        explanation=_text(record.get("explanation")),
        confidence=_text(record.get("confidence"), "low"),
        validation_status=_text(record.get("validation_status"), "unreviewed"),
    )


def _response(record: dict[str, object]) -> ExistingResponse:
    return ExistingResponse(
        response_id=_text(record.get("response_id")),
        project_fact_ids=_strings(record.get("project_fact_ids")),
        pathway_ids=_strings(record.get("pathway_ids")),
        description=_text(record.get("description")),
        limitation=_text(record.get("limitation")),
    )


def _pathway(record: dict[str, object]) -> ClimatePathway:
    return ClimatePathway(
        pathway_id=_text(record.get("pathway_id")),
        direction=_text(record.get("direction")),
        chain=_strings(record.get("chain")),
        project_anchor_ids=_strings(record.get("project_anchor_ids")),
        evidence_ids=_strings(record.get("evidence_ids")),
        confidence=_text(record.get("confidence"), "low"),
    )


def _gap(record: dict[str, object]) -> ResidualGap:
    return ResidualGap(
        gap_id=_text(record.get("gap_id")),
        gap_type=_text(record.get("gap_type"), "evidence_gap"),
        statement=_text(record.get("statement")),
        pathway_ids=_strings(record.get("pathway_ids")),
        project_anchor_ids=_strings(record.get("project_anchor_ids")),
        existing_response_ids=_strings(record.get("existing_response_ids")),
        evidence_ids=_strings(record.get("evidence_ids")),
        confidence=_text(record.get("confidence"), "low"),
    )


def _judgment(record: object, fallback: str) -> Judgment:
    item = _mapping(record)
    return Judgment(
        value=_text(item.get("value"), fallback),
        evidence_ids=_strings(item.get("evidence_ids")),
        rationale=_text(item.get("rationale"), "Evidence remains insufficient."),
    )


def _judgments(payload: dict[str, object]) -> ClimateJudgments:
    source = _mapping(payload.get("judgments")) or payload
    return ClimateJudgments(
        relevance=_judgment(source.get("relevance"), "unclear"),
        sensitivity=_judgment(source.get("sensitivity"), "unclear"),
        responsiveness=_judgment(source.get("responsiveness"), "unclear"),
        operationalization=_judgment(
            source.get("operationalization"), "unclear"
        ),
    )

_summary_overview_paragraphs = validate_summary_overview


_CORE_QUESTION_CAP = 7


def _core_question_signals(facts: list) -> list[str]:
    """Build a lowercase-able signal list from verified facts for bank triggering."""
    signals: list[str] = []
    for item in facts:
        record = asdict(item) if hasattr(item, "__dataclass_fields__") else _mapping(item)
        for value in record.values():
            if isinstance(value, str) and value:
                signals.append(value)
            elif isinstance(value, (list, tuple)):
                signals.extend(v for v in value if isinstance(v, str) and v)
    return signals


def _core_questions_to_answer(facts: list) -> list[dict[str, str]]:
    """Pose triggered core-question-bank items plus deeper driver questions.

    Combines up to six triggered core-bank candidates with the triggered
    driver-depth questions (deduped by id) so the deeper political-economy probes
    surface alongside the climate-interaction questions.
    """
    signals = _core_question_signals(facts)
    plan = climate_question_bank.build_question_plan(signals)
    candidates = list((plan.get("supplementary_candidates") or [])[:6])
    candidates += climate_question_bank.select_triggered_drivers(signals)
    posed: list[dict[str, str]] = []
    seen: set[str] = set()
    for question in candidates:
        question_id = _text(question.get("id"))
        if not question_id or question_id in seen:
            continue
        seen.add(question_id)
        posed.append({
            "id": question_id,
            "theme": _text(question.get("theme")),
            "question": _text(question.get("question")),
            "source": _text(question.get("source")),
        })
    return posed


def _admit_core_questions(
    payload: dict[str, object],
    allowed_ids: set[str],
    known_ids: set[str],
) -> list[dict[str, object]]:
    """Keep only evidence-grounded answers to the posed core questions.

    Evidence-gated: an answer survives only when its question_id was actually
    posed and at least one cited evidence_id resolves to a known register ID.
    Drops duplicates and caps the reader-facing set.
    """
    admitted: list[dict[str, object]] = []
    seen: set[str] = set()
    for record in _records(payload, "core_questions"):
        question_id = _text(record.get("question_id"))
        summary = _text(record.get("summary"))
        if not question_id or question_id not in allowed_ids or question_id in seen:
            continue
        if not summary:
            continue
        evidence_ids = [e for e in _strings(record.get("evidence_ids")) if e in known_ids]
        if not evidence_ids:
            continue
        seen.add(question_id)
        admitted.append({
            "question_id": question_id,
            "theme": _text(record.get("theme")),
            "question": _text(record.get("question")),
            "source": _text(record.get("source")),
            "summary": summary,
            "evidence_ids": evidence_ids,
            "watch": _text(record.get("watch")),
        })
        if len(admitted) >= _CORE_QUESTION_CAP:
            break
    return admitted


def _admit_minor_climate_points(
    payload: dict[str, object],
    known_gap_ids: set[str],
    admitted_gap_ids: set[str],
    reserved_texts: set[str],
) -> list[dict[str, object]]:
    """Keep smaller climate/FCV points tied to a non-admitted residual gap.

    Evidence-gated: each point must cite at least one residual_gap_id that exists
    and is not already covered by an admitted priority. Deduped against reserved
    texts (priority titles and readiness-flag text) and capped at three.
    """
    admitted: list[dict[str, object]] = []
    seen: set[str] = set()
    for record in _records(payload, "minor_climate_points"):
        point = _text(record.get("point"))
        if not point:
            continue
        normalized = _normalized_sentence(point)
        if normalized in reserved_texts or normalized in seen:
            continue
        gap_ids = [
            gap_id
            for gap_id in _strings(record.get("residual_gap_ids"))
            if gap_id in known_gap_ids and gap_id not in admitted_gap_ids
        ]
        if not gap_ids:
            continue
        seen.add(normalized)
        admitted.append({
            "point": point,
            "why": _text(record.get("why")),
            "how_to_check": _text(record.get("how_to_check")),
            "residual_gap_ids": gap_ids,
        })
        if len(admitted) >= 3:
            break
    return admitted


def _score(record: object) -> RecommendationScore:
    item = _mapping(record)
    return RecommendationScore(
        materiality=int(item.get("materiality") or 0),
        gap_strength=int(item.get("gap_strength") or 0),
        leverage_urgency=int(item.get("leverage_urgency") or 0),
        evidence=int(item.get("evidence") or 0),
        feasibility=int(item.get("feasibility") or 0),
    )


def _drafting_block(record: object) -> DraftingBlock | None:
    item = _mapping(record)
    if not item:
        return None
    return DraftingBlock(
        target_document=_text(item.get("target_document")),
        target_section=_text(item.get("target_section")),
        drafting_status=_text(item.get("drafting_status")),
        text=_text(item.get("text")),
        project_basis_ids=_strings(item.get("project_basis_ids")),
        gap_basis_ids=_strings(item.get("gap_basis_ids")),
        guidance_ids=_strings(item.get("guidance_ids")),
    )


def _candidate_drafting_blocks(
    record: dict[str, object],
) -> tuple[DraftingBlock | None, DraftingBlock | None]:
    """Map compact transport blocks to the stable domain fields."""

    if "drafting_blocks" not in record:
        return (
            _drafting_block(record.get("current_document_drafting")),
            _drafting_block(record.get("operational_instrument_drafting")),
        )

    raw_blocks = record.get("drafting_blocks")
    if not isinstance(raw_blocks, list):
        raise ValueError("drafting_blocks must be a list")
    current = None
    operational = None
    for raw_block in raw_blocks:
        item = _mapping(raw_block)
        role = _text(item.get("drafting_role"))
        block = _drafting_block(item)
        if block is None:
            raise ValueError("drafting block is empty")
        if role == "current_document":
            if current is not None:
                raise ValueError("duplicate current-document drafting block")
            current = block
        elif role == "operational_instrument":
            if operational is not None:
                raise ValueError("duplicate operational drafting block")
            operational = block
        else:
            raise ValueError("unsupported drafting role")
    return current, operational


def _candidate(record: dict[str, object]) -> CandidateRecommendation:
    current_drafting, operational_drafting = _candidate_drafting_blocks(record)
    return CandidateRecommendation(
        recommendation_id=_text(record.get("recommendation_id")),
        title=_text(record.get("title")),
        pathway_ids=_strings(record.get("pathway_ids")),
        existing_response_ids=_strings(record.get("existing_response_ids")),
        residual_gap_ids=_strings(record.get("residual_gap_ids")),
        project_anchor_ids=_strings(record.get("project_anchor_ids")),
        decision=_text(record.get("decision")),
        minimum_action=_text(record.get("minimum_action")),
        enhanced_action=_text(record.get("enhanced_action")) or None,
        enhanced_activation=_text(record.get("enhanced_activation")) or None,
        routing_status=_text(record.get("routing_status"), "not_applicable"),
        instrument_claim_ids=_strings(record.get("instrument_claim_ids")),
        responsible_function=_text(
            record.get("responsible_function"), "Task team to confirm"
        ),
        authority_basis=_text(record.get("authority_basis"), "none_verified"),
        recommendation_basis=_text(
            record.get("recommendation_basis"), "analytical_judgment"
        ),
        completion_evidence=_text(
            record.get("completion_evidence"), "Task team to define"
        ),
        completion_evidence_status=_text(
            record.get("completion_evidence_status"), "team_to_define"
        ),
        confidence=_text(record.get("confidence"), "low"),
        limitation=_text(record.get("limitation")),
        caution=_text(record.get("caution")),
        current_document_drafting=current_drafting,
        operational_instrument_drafting=operational_drafting,
        score=_score(record.get("score")),
        gate_results={
            str(key): bool(value)
            for key, value in _mapping(record.get("gate_results")).items()
        },
        supported_numeric_tokens=_strings(record.get("supported_numeric_tokens")),
        narrative=_text(record.get("narrative")),
    )


def _source_linked_numeric_tokens(
    candidate: CandidateRecommendation,
    facts: list[ProjectFactClaim],
) -> tuple[str, ...]:
    """Return numeric tokens present in project facts linked by the candidate."""

    linked_fact_ids = set(candidate.project_anchor_ids) | set(
        candidate.instrument_claim_ids
    )
    numeric_tokens: set[str] = set()
    for fact in facts:
        if fact.claim_id not in linked_fact_ids:
            continue
        fact_text = " ".join(
            value
            for value in (
                fact.subject,
                fact.predicate,
                fact.object_value,
                fact.supporting_excerpt,
            )
            if value
        )
        numeric_tokens.update(numeric_tokens_in_text(fact_text))
    return tuple(sorted(numeric_tokens))


def _unsupported_numeric_fields(
    candidate: CandidateRecommendation,
) -> list[dict[str, object]]:
    supported = set(candidate.supported_numeric_tokens)
    fields: list[dict[str, object]] = []
    values = (
        "decision",
        "minimum_action",
        "enhanced_action",
        "enhanced_activation",
        "completion_evidence",
    )
    field_values = [(name, getattr(candidate, name)) for name in values]
    field_values.extend((
        ("current_document_drafting.text", candidate.current_document_drafting.text)
        if candidate.current_document_drafting else ("current_document_drafting.text", ""),
        ("operational_instrument_drafting.text", candidate.operational_instrument_drafting.text)
        if candidate.operational_instrument_drafting else ("operational_instrument_drafting.text", ""),
    ))
    for name, value in field_values:
        tokens = sorted(
            set(numeric_tokens_in_text(value or "")) - supported
        )[:12]
        if tokens:
            fields.append({"field": name, "tokens": tokens})
    return fields

def _unsupported_precision_fields(
    candidate: CandidateRecommendation,
    issue_codes: set[str],
) -> list[dict[str, str]]:
    """Return bounded field paths and reason codes without logging prose."""

    patterns = {
        "DRAFTING_INSTRUMENT_UNVERIFIED": re.compile(
            r"\b(?:project operations manual|security risk management plan|"
            r"environmental and social commitment plan|environmental and social "
            r"management framework|results framework)\b",
            re.IGNORECASE,
        ),
        "DRAFTING_ACTOR_UNVERIFIED": re.compile(
            r"\b(?:focal point|steering committee|coordination unit)\b",
            re.IGNORECASE,
        ),
        "DRAFTING_TIMING_UNVERIFIED": re.compile(
            r"\bbefore (?:effectiveness|appraisal|board approval)\b",
            re.IGNORECASE,
        ),
        "DRAFTING_SYSTEM_UNVERIFIED": re.compile(
            r"\b(?:hydrometeorological|hydromet) system\b",
            re.IGNORECASE,
        ),
    }
    field_values = (
        ("decision", candidate.decision),
        ("minimum_action", candidate.minimum_action),
        ("enhanced_action", candidate.enhanced_action or ""),
        ("enhanced_activation", candidate.enhanced_activation or ""),
        ("completion_evidence", candidate.completion_evidence),
        (
            "current_document_drafting.text",
            candidate.current_document_drafting.text
            if candidate.current_document_drafting else "",
        ),
        (
            "operational_instrument_drafting.target_document",
            candidate.operational_instrument_drafting.target_document
            if candidate.operational_instrument_drafting else "",
        ),
        (
            "operational_instrument_drafting.text",
            candidate.operational_instrument_drafting.text
            if candidate.operational_instrument_drafting else "",
        ),
    )
    return [
        {"field": field, "reason_code": code}
        for code, pattern in patterns.items()
        if code in issue_codes
        for field, value in field_values
        if pattern.search(value)
    ][:12]



def _readiness_flag(record: dict[str, object]) -> ReviewReadinessFlag:
    return ReviewReadinessFlag(
        flag_id=_text(record.get("flag_id")),
        category=_text(record.get("category")),
        flag=_text(record.get("flag")),
        why_it_matters=_text(record.get("why_it_matters")),
        document_basis_ids=_strings(record.get("document_basis_ids")),
        suggested_verification=_text(record.get("suggested_verification")),
        residual_gap_ids=_strings(record.get("residual_gap_ids")),
    )


def _reviewed_readiness_flags(
    flags: Sequence[ReviewReadinessFlag], review: dict[str, object],
) -> list[ReviewReadinessFlag]:
    """Admit only explicit, well-formed, uncontested flag acceptances."""
    accepted = review.get("passed_readiness_ids")
    known_ids = {item.flag_id for item in flags}
    if (review.get("verdict") not in {"pass", "revise", "block"}
            or not isinstance(accepted, list)
            or any(not isinstance(item, str) or not item.strip() for item in accepted)
            or len(set(accepted)) != len(accepted)
            or len(known_ids) != len(flags)
            or set(accepted) - known_ids):
        return []
    if review.get("verdict") == "pass" and any(
        review.get(key) for key in ("object_ids", "reason_codes", "issues")
    ):
        return []
    disputed = set(_strings(review.get("object_ids"))) | {
        _text(item.get("object_id")) for item in _records(review, "issues")
    }
    if set(accepted) & disputed:
        return []
    return [item for item in flags if item.flag_id in accepted]


def _integrity_readiness_flags(
    fact_payload: dict[str, object],
    known_block_ids: set[str],
) -> list[ReviewReadinessFlag]:
    """Convert fact-stage document-integrity findings to readiness flags.

    Kept only when the category is valid and every document_basis_id is a real
    source block. These checks establish provenance only; semantic acceptance
    is required separately before a finding can reach the reader.
    """
    kept: list[ReviewReadinessFlag] = []
    for record in _records(fact_payload, "document_integrity_findings"):
        try:
            flag = _readiness_flag(record)
        except (TypeError, ValueError):
            continue
        if flag.category not in _INTEGRITY_CATEGORIES:
            continue
        if not flag.document_basis_ids:
            continue
        if set(flag.document_basis_ids) - known_block_ids:
            continue
        kept.append(replace(flag, residual_gap_ids=()))
    return kept


def _merge_readiness_flags(
    integrity: list[ReviewReadinessFlag],
    model: tuple[ReviewReadinessFlag, ...],
    *,
    cap: int = 4,
) -> tuple[ReviewReadinessFlag, ...]:
    """Merge deterministic integrity findings ahead of model flags.

    Integrity findings take priority (they are the confirm-before-gate items),
    duplicates are collapsed by (category, normalised flag text), and the total
    is capped to preserve the existing "no more than four" reader contract.
    """
    merged: list[ReviewReadinessFlag] = []
    seen: set[tuple[str, str]] = set()
    for flag in [*integrity, *model]:
        if len(merged) == cap:
            break
        key = (flag.category, _normalized_sentence(flag.flag))
        if key in seen:
            continue
        seen.add(key)
        merged.append(flag)
    # Suppression accounting counts a model flag deduped by an equivalent
    # integrity flag as suppressed; the point still surfaces via the integrity flag.
    return tuple(merged)


def _bounded_pathways(
    pathways: list[ClimatePathway],
) -> tuple[list[ClimatePathway], int]:
    kept: list[ClimatePathway] = []
    counts: dict[str, int] = {}
    for pathway in pathways:
        count = counts.get(pathway.direction, 0)
        if count >= 3:
            continue
        kept.append(pathway)
        counts[pathway.direction] = count + 1
    return kept, len(pathways) - len(kept)


def _validate_analysis(
    responses: list[ExistingResponse],
    pathways: list[ClimatePathway],
    gaps: list[ResidualGap],
    known_fact_ids: set[str],
    known_context_ids: set[str],
    confirmed_absences: set[str],
) -> tuple[list[ExistingResponse], list[ClimatePathway], list[ResidualGap], list[str]]:
    reasons: list[str] = []
    for _ in range(4):
        issues = validate_analysis_registers(
            responses,
            pathways,
            gaps,
            known_fact_ids,
            known_context_ids,
            confirmed_absences,
        )
        if not issues:
            break
        reasons.extend(issue.code for issue in issues)
        invalid = {issue.object_id for issue in issues if issue.blocking}
        next_responses = [item for item in responses if item.response_id not in invalid]
        next_pathways = [item for item in pathways if item.pathway_id not in invalid]
        next_gaps = [item for item in gaps if item.gap_id not in invalid]
        if (next_responses, next_pathways, next_gaps) == (
            responses,
            pathways,
            gaps,
        ):
            break
        responses, pathways, gaps = next_responses, next_pathways, next_gaps
    return responses, pathways, gaps, reasons


def _risk(candidates: tuple[CandidateRecommendation, ...]) -> ReviewRisk:
    drafting = any(
        item.current_document_drafting
        or item.operational_instrument_drafting
        for item in candidates
    )
    mandatory = any(
        any(
            word in " ".join(
                block.text
                for block in (
                    item.current_document_drafting,
                    item.operational_instrument_drafting,
                )
                if block
            ).casefold().split()
            for word in ("must", "shall", "required", "mandatory")
        )
        for item in candidates
    )
    return ReviewRisk(
        mandatory_language=mandatory,
        drafting_language=drafting,
        verified_scope_change=any(
            item.routing_status == "verified_with_scope_change"
            for item in candidates
        ),
        unresolved_routing=False,
        high_materiality_moderate_evidence=any(
            item.score.materiality >= 3 and item.score.evidence <= 1
            for item in candidates
        ),
    )


def _applicability_fingerprint(documents: list[SourceDocument]) -> str:
    data = [
        {
            "id": item.document_id,
            "applicability": item.applicability.value,
            "relationship": item.relationship,
            "version": item.version_status,
        }
        for item in documents
    ]
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def run_verified_climate_pipeline(
    *,
    source_documents: list[SourceDocument],
    source_blocks: list[SourceBlock],
    context_evidence: list[ContextEvidenceRef],
    clients: PipelineClients,
    bank_release_id: str | None,
    run_id: str,
    cancel_event: object | None = None,
    doc_type: str = "Unknown",
    instrument_type: str = "Unknown",
    operation_context: dict[str, object] | None = None,
    wall_clock_seconds: int = 14 * 60,
) -> dict[str, object]:
    """Run the automatic pipeline and return only validated reader objects."""
    if wall_clock_seconds < 1:
        raise ValueError("wall_clock_seconds must be positive")
    deadline = time.monotonic() + wall_clock_seconds
    metric_starts = {role: len(getattr(client, 'call_metrics', []))
                     for role, client in (('assessment', clients.assessment), ('reviewer', clients.reviewer))}
    latency_ms: dict[str, int] = {}
    repair_allowance = {"remaining": CALL_BUDGETS["recommendation_compiler"].output_tokens}
    reasons: list[str] = []
    repairs: list[str] = []
    suppressed = {
        "facts": 0,
        "derived_assertions": 0,
        "responses": 0,
        "pathways": 0,
        "gaps": 0,
        "recommendations": 0,
        "readiness_flags": 0,
    }
    resolved_context = dict(operation_context or {})
    resolved_context.setdefault("document_type", doc_type)
    resolved_context.setdefault("instrument_type", instrument_type)
    resolved_context.setdefault("country_scope", "single")
    resolved_context.setdefault("is_mpa", False)
    resolved_context.setdefault("has_ipf_component", False)
    resolved_context.setdefault("preparation_regime", "unresolved_policy_source")
    resolved_context.setdefault("processing_model", "unknown")
    resolved_context.setdefault("es_regime", "UNRESOLVED")
    resolved_context.setdefault("warning_codes", [])
    guidance = select_operational_guidance(
        doc_type=doc_type,
        instrument_type=instrument_type,
        is_mpa=bool(resolved_context.get("is_mpa")),
    )
    if not guidance:
        reasons.append("OPERATIONAL_GUIDANCE_WITHHELD")
    document_records = [_as_record(item) for item in source_documents]
    block_records = [_as_record(item) for item in source_blocks]
    context_records = [_as_record(item) for item in context_evidence]
    known_block_ids = {block.block_id for block in source_blocks}

    fact_payload = _call(
        clients.assessment,
        "fact_extraction",
        {
            "documents": document_records,
            "source_blocks": block_records,
            "operation_context": resolved_context,
        },
        latency_ms,
        cancel_event=cancel_event,
        deadline=deadline,
    )
    raw_facts = _records(fact_payload, "facts", "project_fact_registry")
    facts: list[ProjectFactClaim] = []
    for record in raw_facts:
        try:
            facts.append(_fact(record))
        except (TypeError, ValueError):
            suppressed["facts"] += 1
            reasons.append("FACT_MALFORMED")
    fact_result = normalize_fact_registry(facts, source_blocks)
    reasons.extend(issue.code for issue in fact_result.blocking_issues)
    invalid_fact_ids = {
        issue.object_id for issue in fact_result.blocking_issues if issue.blocking
    }
    facts = [item for item in facts if item.claim_id not in invalid_fact_ids]
    suppressed["facts"] += len(invalid_fact_ids)

    raw_assertions = _records(
        fact_payload, "derived_assertions", "derived_assertion_register"
    )
    assertions: list[DerivedAssertion] = []
    for record in raw_assertions:
        try:
            assertions.append(_assertion(record))
        except (TypeError, ValueError):
            suppressed["derived_assertions"] += 1
            reasons.append("DERIVATION_MALFORMED")
    assertion_issues = validate_derived_assertions(
        assertions, {item.claim_id for item in facts}
    )
    reasons.extend(issue.code for issue in assertion_issues)
    invalid_assertions = {
        issue.object_id for issue in assertion_issues if issue.blocking
    }
    assertions = [
        item for item in assertions if item.assertion_id not in invalid_assertions
    ]
    suppressed["derived_assertions"] += len(invalid_assertions)

    source_passages = cited_source_passages([asdict(item) for item in facts], source_blocks)

    analysis_payload = _call(
        clients.assessment,
        "bounded_analysis",
        {
            "facts": [asdict(item) for item in facts],
            "source_passages": source_passages,
            "derived_assertions": [asdict(item) for item in assertions],
            "context_evidence": context_records,
            "operation_context": resolved_context,
        },
        latency_ms,
        cancel_event=cancel_event,
        deadline=deadline,
    )
    responses = [
        _response(item)
        for item in _records(
            analysis_payload, "existing_responses", "existing_response_register"
        )
    ]
    pathways = [
        _pathway(item)
        for item in _records(
            analysis_payload, "pathways", "climate_fcv_pathway_register"
        )
    ]
    gaps = [
        _gap(item)
        for item in _records(
            analysis_payload, "residual_gaps", "residual_gap_register"
        )
    ]
    pathways, pathway_overflow = _bounded_pathways(pathways)
    if pathway_overflow:
        suppressed["pathways"] += pathway_overflow
        reasons.append("PATHWAY_LIMIT_EXCEEDED")
    if len(gaps) > 8:
        suppressed["gaps"] += len(gaps) - 8
        gaps = gaps[:8]
        reasons.append("GAP_LIMIT_EXCEEDED")
    original_counts = (len(responses), len(pathways), len(gaps))
    fact_ids = {item.claim_id for item in facts}
    confirmed_absences = {
        item.claim_id
        for item in facts
        if item.epistemic_status == EpistemicStatus.CONFIRMED_ABSENCE.value
    }
    responses, pathways, gaps, analysis_reasons = _validate_analysis(
        responses,
        pathways,
        gaps,
        fact_ids,
        {item.evidence_id for item in context_evidence},
        confirmed_absences,
    )
    reasons.extend(analysis_reasons)
    suppressed["responses"] += original_counts[0] - len(responses)
    suppressed["pathways"] += original_counts[1] - len(pathways)
    suppressed["gaps"] += original_counts[2] - len(gaps)
    analysis_record = {
        "existing_responses": [asdict(item) for item in responses],
        "pathways": [asdict(item) for item in pathways],
        "residual_gaps": [asdict(item) for item in gaps],
        "opportunities_and_unintended_consequences": analysis_payload.get(
            "opportunities_and_unintended_consequences", []
        ),
        "evidence_limitations": analysis_payload.get("evidence_limitations", []),
    }

    posed_core_questions = _core_questions_to_answer(facts)
    judgment_payload = _call(
        clients.assessment,
        "judgment_review",
        {
            "facts": [asdict(item) for item in facts],
            "source_passages": source_passages,
            "analysis": analysis_record,
            "core_questions_to_answer": posed_core_questions,
            "operation_context": resolved_context,
        },
        latency_ms,
        cancel_event=cancel_event,
        deadline=deadline,
    )
    judgments = _judgments(judgment_payload)
    executive_readout = _text(judgment_payload.get("executive_readout"))
    overview_summary = _text(judgment_payload.get("overview_summary"))

    known_ids = (
        fact_ids
        | {item.assertion_id for item in assertions}
        | {item.response_id for item in responses}
        | {item.pathway_id for item in pathways}
        | {item.gap_id for item in gaps}
        | {item.evidence_id for item in context_evidence}
    )
    core_questions = _admit_core_questions(
        judgment_payload,
        {question["id"] for question in posed_core_questions},
        known_ids,
    )
    judgment_issues = validate_judgments(judgments, known_ids)
    if judgment_issues:
        reasons.extend(issue.code for issue in judgment_issues)
        for dimension in {
            issue.object_id for issue in judgment_issues if issue.object_id
        }:
            judgments = replace(
                judgments,
                **{
                    dimension: Judgment(
                        value="unclear",
                        evidence_ids=(),
                        rationale="Automated checks found insufficient support.",
                    )
                },
            )
            repairs.append(f"normalize_{dimension}_to_unclear")

    raw_summary_overview = judgment_payload.get("summary_overview")
    canonical_summary_text = [
        asdict(item)
        for item in (*facts, *assertions, *responses, *pathways, *gaps)
    ]
    canonical_summary_text.extend(
        (overview_summary, asdict(judgments), core_questions, context_records)
    )
    summary_diagnostics: dict[str, object] = {}
    summary_overview_paragraphs = _summary_overview_paragraphs(
        raw_summary_overview,
        executive_readout=executive_readout,
        canonical_text=canonical_summary_text,
        diagnostics=summary_diagnostics,
    )
    final_reader_required = judgment_payload.get("reader_contract") == "final-reader-v1"
    if final_reader_required:
        summary_overview_status = "pending"
    elif raw_summary_overview is None:
        summary_overview_status = "fallback"
        reasons.append("SUMMARY_OVERVIEW_FALLBACK_REQUIRED")
    elif not summary_overview_paragraphs:
        summary_overview_status = "fallback"
        reasons.append("SUMMARY_OVERVIEW_INVALID")
    else:
        summary_overview_status = "generated"

    recommendation_payload = _call(
        clients.assessment,
        "recommendation_compiler",
        {
            "facts": [asdict(item) for item in facts],
            "source_passages": source_passages,
            "analysis": analysis_record,
            "judgments": asdict(judgments),
            "operation_context": resolved_context,
            "guidance_registry_version": GUIDANCE_REGISTRY_VERSION,
            "operational_guidance": [item.as_record() for item in guidance],
        },
        latency_ms,
        cancel_event=cancel_event,
        deadline=deadline,
    )
    raw_candidates = _records(
        recommendation_payload,
        "recommendation_candidates",
        "priorities",
    )
    candidates_missing_drafting = [
        record
        for record in raw_candidates
        if not any(
            key in record
            for key in (
                "drafting_blocks",
                "current_document_drafting",
                "operational_instrument_drafting",
            )
        )
    ]
    if candidates_missing_drafting:
        drafting_payload = _call(
            clients.assessment,
            "drafting_compiler",
            {
                "facts": [asdict(item) for item in facts],
                "source_passages": source_passages,
                "analysis": analysis_record,
                "judgments": asdict(judgments),
                "recommendation_candidates": candidates_missing_drafting,
                "current_document": doc_type,
                "instrument_type": instrument_type,
                "operation_context": resolved_context,
                "guidance_registry_version": GUIDANCE_REGISTRY_VERSION,
                "operational_guidance": [
                    item.as_record() for item in guidance
                ],
            },
            latency_ms,
            cancel_event=cancel_event,
            deadline=deadline - CALL_BUDGETS["conditional_review"].timeout_seconds,
            optional=True,
        )
        if drafting_payload.get('_optional_failure'):
            reasons.append('DRAFTING_GENERATION_UNAVAILABLE')
        blocks_by_recommendation: dict[str, object] = {}
        duplicate_drafting_ids: set[str] = set()
        for drafting_set in _records(drafting_payload, "drafting_sets"):
            recommendation_id = _text(
                drafting_set.get("recommendation_id")
            )
            if not recommendation_id:
                continue
            if recommendation_id in blocks_by_recommendation:
                duplicate_drafting_ids.add(recommendation_id)
                blocks_by_recommendation.pop(recommendation_id, None)
                continue
            if recommendation_id not in duplicate_drafting_ids:
                blocks_by_recommendation[recommendation_id] = (
                    drafting_set.get("drafting_blocks")
                )
        for record in candidates_missing_drafting:
            recommendation_id = _text(record.get("recommendation_id"))
            if recommendation_id in blocks_by_recommendation:
                record["drafting_blocks"] = blocks_by_recommendation[
                    recommendation_id
                ]
    recommendation_reasons: list[str] = []
    unsupported_numbers: list[str] = []
    candidate_suppressions: list[dict[str, object]] = []
    drafting_suppressions: list[dict[str, object]] = []
    parsed_candidate_count = 0
    candidates: list[CandidateRecommendation] = []
    def normalize_candidate(candidate):
        candidate, drafting_repairs = normalize_drafting_blocks(
            candidate,
            current_document=doc_type,
        )
        repairs.extend(drafting_repairs)
        source_numeric_tokens = _source_linked_numeric_tokens(candidate, facts)
        candidate = replace(
            candidate,
            supported_numeric_tokens=source_numeric_tokens,
        )
        candidate, enhancement_repairs = normalize_optional_enhancement(candidate)
        repairs.extend(enhancement_repairs)
        candidate, precision_repairs = normalize_unsupported_core_precision(candidate)
        repairs.extend(precision_repairs)
        candidate, drafting_precision_repairs = (
            normalize_unsupported_drafting_precision(candidate)
        )
        repairs.extend(drafting_precision_repairs)
        drafting_context = DraftingValidationContext(
            known_ids=frozenset(known_ids),
            guidance_ids=frozenset(item.guidance_id for item in guidance),
            current_document=doc_type,
            standard_targets=frozenset(
                target for item in guidance for target in item.permitted_targets
            ),
            project_fact_text={
                item.claim_id: " ".join(
                    (item.subject, item.predicate, item.object_value)
                ) for item in facts
            },
            project_fact_types={item.claim_id: item.claim_type for item in facts},
            guidance_targets={
                item.guidance_id: item.permitted_targets
                for item in guidance
            },
            instrument_type=instrument_type,
            has_ipf_component=bool(resolved_context.get("has_ipf_component")),
        )
        candidate, actor_repairs = normalize_unverified_completion_actor(
            candidate,
            drafting_context,
        )
        repairs.extend(actor_repairs)
        candidate, drafting_actor_repairs = normalize_unverified_drafting_actor(
            candidate,
            drafting_context,
        )
        repairs.extend(drafting_actor_repairs)
        candidate, evidence_repairs = normalize_drafting_blocks(
            candidate,
            current_document=doc_type,
            drafting_context=drafting_context,
        )
        repairs.extend(evidence_repairs)
        candidate, ref_repairs = normalize_recommendation_references(
            candidate, known_ids
        )
        repairs.extend(ref_repairs)
        issues = validate_recommendation(
            candidate, known_ids, drafting_context=drafting_context,
            include_drafting=False,
        )
        # Validate each artifact separately, using the same authority and source
        # checks. A draft defect does not change the core decision's admission.
        for field in ("current_document_drafting", "operational_instrument_drafting"):
            block = getattr(candidate, field)
            if block is None:
                continue
            isolated = replace(candidate, **{
                "current_document_drafting": block if field == "current_document_drafting" else None,
                "operational_instrument_drafting": block if field == "operational_instrument_drafting" else None,
            })
            artifact_issues = validate_recommendation(
                isolated, known_ids, drafting_context=drafting_context,
                require_current_drafting=False,
            )
            core_codes = {issue.code for issue in issues if issue.blocking}
            failures = sorted({issue.code for issue in artifact_issues
                               if issue.blocking and issue.code not in core_codes})
            if failures:
                drafting_suppressions.append({"recommendation_id": candidate.recommendation_id,
                                               "artifact": field, "reason_codes": failures})
                candidate = replace(candidate, **{field: None})
        return candidate, issues

    for record in raw_candidates:
        try:
            core_record = {key: value for key, value in record.items() if key not in
                           {'drafting_blocks', 'current_document_drafting', 'operational_instrument_drafting'}}
            candidate = _candidate(core_record)
            try:
                candidate = _candidate(record)
            except (TypeError, ValueError):
                drafting_suppressions.append({'recommendation_id': candidate.recommendation_id,
                                               'reason_codes': ['DRAFTING_MALFORMED']})
        except (TypeError, ValueError):
            suppressed["recommendations"] += 1
            reasons.append("RECOMMENDATION_MALFORMED")
            recommendation_reasons.append("RECOMMENDATION_MALFORMED")
            if len(candidate_suppressions) < 3:
                candidate_suppressions.append(
                    {
                        "recommendation_id": _text(
                            record.get("recommendation_id"),
                            "unresolved_candidate",
                        ),
                        "stage": "parsing",
                        "reason_codes": ["RECOMMENDATION_MALFORMED"],
                        "unsupported_numeric_fields": [],
                    }
                )
            continue
        parsed_candidate_count += 1
        candidate, issues = normalize_candidate(candidate)
        for token in unsupported_numeric_tokens(candidate):
            if token not in unsupported_numbers and len(unsupported_numbers) < 12:
                unsupported_numbers.append(token)
        # Only blocking issues suppress a recommendation. Advisory issues
        # (e.g. references to standard WBG instruments, process milestones, or
        # mandatory phrasing) are recorded for the technical annex but do not
        # drop an otherwise-grounded recommendation.
        blocking_issues = [issue for issue in issues if issue.blocking]
        if blocking_issues:
            suppressed["recommendations"] += 1
            reasons.extend(issue.code for issue in blocking_issues)
            recommendation_reasons.extend(
                issue.code for issue in blocking_issues
            )
            if len(candidate_suppressions) < 3:
                candidate_suppressions.append(
                    {
                        "recommendation_id": candidate.recommendation_id,
                        "stage": "validation",
                        "reason_codes": list(
                            dict.fromkeys(
                                issue.code for issue in blocking_issues
                            )
                        )[:12],
                        "unsupported_numeric_fields": (
                            _unsupported_numeric_fields(candidate)
                        ),
                    }
                )
                precision_fields = _unsupported_precision_fields(
                    candidate,
                    {issue.code for issue in blocking_issues},
                )
                if precision_fields:
                    candidate_suppressions[-1][
                        "unsupported_precision_fields"
                    ] = precision_fields
            continue
        candidates.append(candidate)

    admitted_count = 0
    for candidate in candidates:
        failure_codes = admission_failure_codes(candidate)
        if failure_codes:
            recommendation_reasons.extend(failure_codes)
            reasons.extend(failure_codes)
            if len(candidate_suppressions) < 3:
                candidate_suppressions.append(
                    {
                        "recommendation_id": candidate.recommendation_id,
                        "stage": "admission",
                        "reason_codes": list(failure_codes)[:12],
                        "unsupported_numeric_fields": [],
                    }
                )
        else:
            admitted_count += 1
    priorities = admit_and_rank(candidates)
    suppressed["recommendations"] += len(candidates) - len(priorities)
    if admitted_count > len(priorities):
        recommendation_reasons.append("ADMISSION_PRIORITY_CAP")
        reasons.append("ADMISSION_PRIORITY_CAP")

    raw_flags = _records(recommendation_payload, "readiness_flags")
    flags: list[ReviewReadinessFlag] = []
    for record in raw_flags:
        try:
            flags.append(_readiness_flag(record))
        except (TypeError, ValueError):
            reasons.append("READINESS_FLAG_MALFORMED")
    model_readiness = admit_readiness_flags(
        flags,
        fact_ids,
        {item.statement for item in gaps},
        known_gap_ids={item.gap_id for item in gaps},
        admitted_gap_ids={
            gap_id for item in priorities for gap_id in item.residual_gap_ids
        },
    )
    integrity_flags = _integrity_readiness_flags(fact_payload, known_block_ids)
    readiness = _merge_readiness_flags(integrity_flags, model_readiness, cap=4)
    suppressed["readiness_flags"] += (
        len(raw_flags) + len(integrity_flags) - len(readiness)
    )
    # Reserve even rejected flag wording so it cannot reappear unreviewed as a minor point.
    minor_climate_points = _admit_minor_climate_points(
        judgment_payload,
        {item.gap_id for item in gaps},
        {gap_id for item in priorities for gap_id in item.residual_gap_ids},
        {_normalized_sentence(item.title) for item in priorities}
        | {_normalized_sentence(flag.flag) for flag in readiness},
    )

    review_status = "passed"
    reviewer_invoked = False
    reviewer_verdict = "not_invoked"
    semantic_review_object_ids: list[str] = []
    correction_trace: dict[str, object] = {}
    review: dict[str, object] = {}
    review_input: dict[str, object] = {}
    if priorities:
        reviewer_invoked = True
        review_input = {
            "readiness_flags": [asdict(item) for item in readiness],
            "source_blocks": block_records,
            "facts": [asdict(item) for item in facts],
            "analysis": analysis_record,
            "context_evidence": context_records,
            "judgments": asdict(judgments),
            "recommendations": [asdict(replace(item, current_document_drafting=None,
                                              operational_instrument_drafting=None)) for item in priorities],
            "drafting_artifacts": [
                {"object_id": f"{item.recommendation_id}::{role}",
                 "recommendation_id": item.recommendation_id, "block": asdict(block)}
                for item in priorities
                for role, block in (("current_document", item.current_document_drafting),
                                    ("operational_instrument", item.operational_instrument_drafting))
                if block is not None
            ],
            "operation_context": resolved_context,
            "current_document": doc_type,
            "guidance_registry_version": GUIDANCE_REGISTRY_VERSION,
            "operational_guidance": [item.as_record() for item in guidance],
        }
        review = _call(
            clients.reviewer,
            "conditional_review",
            review_input,
            latency_ms,
            cancel_event=cancel_event,
            deadline=deadline,
        )
        reviewer_verdict = _text(review.get("verdict"), "block").casefold()
        review_reasons = _bounded_reason_codes(review.get("reason_codes"))
        priority_ids = {item.recommendation_id for item in priorities}
        core_admission = reconcile_core_reviews(
            review,
            (item.recommendation_id for item in priorities),
            (item["block_id"] for item in block_records),
        )
        review_reasons.extend(core_admission.reason_codes)
        readiness_ids = {item.flag_id for item in readiness}
        disputed_readiness_ids = readiness_ids & (
            set(_strings(review.get("object_ids")))
            | {_text(item.get("object_id")) for item in _records(review, "issues")}
        )
        artifact_ids = {item["object_id"] for item in review_input["drafting_artifacts"]}
        semantic_review_object_ids = list(
            dict.fromkeys(
                list(object_id for object_id in _strings(review.get("object_ids"))
                     if object_id in priority_ids | artifact_ids)
                + list(core_admission.affected_core_ids)
            )
        )[:15]
        if reviewer_verdict == 'pass' and (
            review.get('object_ids') or review.get('reason_codes')
            or review.get('issues') or core_admission.affected_core_ids
        ):
            reviewer_verdict = 'block'
            review_reasons.append('SEMANTIC_REVIEW_VERDICT_INVALID')
            if not semantic_review_object_ids and not disputed_readiness_ids:
                semantic_review_object_ids = sorted(priority_ids)
        if reviewer_verdict not in {"pass", "revise", "block"}:
            reviewer_verdict = "block"
            review_reasons.append("SEMANTIC_REVIEW_VERDICT_INVALID")
            semantic_review_object_ids = sorted(priority_ids)
        if set(_strings(review.get("object_ids"))) - (priority_ids | artifact_ids | readiness_ids):
            reviewer_verdict = "block"
            review_reasons.append("SEMANTIC_REVIEW_TARGET_UNRESOLVED")
            semantic_review_object_ids = sorted(priority_ids)
        if core_admission.invalid_core_ids:
            review_reasons.append('SEMANTIC_REVIEW_TARGET_UNRESOLVED')
        if (reviewer_verdict != "pass" and not semantic_review_object_ids
                and not disputed_readiness_ids):
            review_reasons.append("SEMANTIC_REVIEW_TARGET_UNRESOLVED")
            semantic_review_object_ids = sorted(priority_ids)
        reasons.extend(review_reasons)
        recommendation_reasons.extend(review_reasons)
        if reviewer_verdict != "pass":
            affected_ids = set(semantic_review_object_ids) & priority_ids
            affected_artifacts = set(semantic_review_object_ids) & artifact_ids
            reviewed_priorities = priorities
            # Only explicitly targeted wording is withheld. Parent IDs remain
            # core defects, including legacy reviewer responses.
            priorities = tuple(replace(item, **{
                field: None if f"{item.recommendation_id}::{role}" in affected_artifacts
                else getattr(item, field)
                for role, field in (("current_document", "current_document_drafting"),
                                    ("operational_instrument", "operational_instrument_drafting"))
            }) for item in priorities)
            drafting_suppressions.extend({"object_id": identifier, "stage": "semantic_review",
                                           "reason_codes": review_reasons} for identifier in sorted(affected_artifacts))
            # Correct only explicitly explained revise targets; block never retries.
            issues_by_id = {
                _text(issue.get("object_id")): issue
                for issue in _records(review, "issues")
                if _text(issue.get("explanation"))
            }
            issues_by_id.update({
                issue["object_id"]: issue
                for issue in core_admission.synthesized_issues
                if issue["object_id"] not in issues_by_id
            })
            repair_ids = (
                (affected_ids - set(core_admission.invalid_core_ids))
                & issues_by_id.keys()
                if reviewer_verdict == "revise"
                else set()
            )
            recovered = {}
            if repair_ids:
                originals = {item.recommendation_id: item for item in priorities
                             if item.recommendation_id in repair_ids}
                correction_trace = {"attempted_ids": sorted(repair_ids), "recovered_ids": []}
                try:
                    correction_payload = _call(
                        clients.assessment, "recommendation_compiler",
                        {**review_input, "readiness_flags": [], "recommendations": [asdict(item) for item in originals.values()],
                         "bounded_correction": [issues_by_id[key] for key in sorted(repair_ids)], "call_scope": "core_correction"},
                        latency_ms, cancel_event=cancel_event, deadline=deadline, repair_allowance=repair_allowance,
                    )
                    correction_trace["response"] = _diagnostic_snapshot(correction_payload)
                    records = _records(correction_payload, "recommendation_candidates")
                    corrected = []
                    correction_rejections = []
                    correction_trace["rejections"] = correction_rejections
                    ids = [_text(record.get("recommendation_id")) for record in records]
                    reference_fields = ("pathway_ids", "existing_response_ids", "residual_gap_ids",
                                        "project_anchor_ids", "instrument_claim_ids")
                    for record in records:
                        identifier = _text(record.get("recommendation_id"))
                        if identifier not in originals or ids.count(identifier) != 1:
                            correction_rejections.append({"recommendation_id": identifier,
                                                          "reason_codes": ["CORRECTION_ID_INVALID"]})
                            continue
                        original = originals[identifier]
                        try:
                            # Compiler corrections cannot carry old or invented
                            # drafting fields: its native schema describes decisions.
                            candidate = replace(_candidate(record), current_document_drafting=None,
                                                operational_instrument_drafting=None)
                            if any(not set(getattr(candidate, field)) <= set(getattr(original, field))
                                   for field in reference_fields):
                                correction_rejections.append({"recommendation_id": identifier,
                                                              "reason_codes": ["CORRECTION_EVIDENCE_EXPANDED"]})
                                continue
                            candidate, candidate_issues = normalize_candidate(candidate)
                        except (TypeError, ValueError):
                            correction_rejections.append({"recommendation_id": identifier,
                                                          "reason_codes": ["RECOMMENDATION_MALFORMED"]})
                            continue
                        failure_codes = list(dict.fromkeys(
                            [issue.code for issue in candidate_issues if issue.blocking]
                            + list(admission_failure_codes(candidate))
                        ))
                        if failure_codes:
                            correction_rejections.append({"recommendation_id": identifier,
                                                          "reason_codes": failure_codes})
                            continue
                        # Repair cannot inflate importance or replace the original ranking.
                        candidate = replace(candidate, score=original.score, rank=original.rank,
                                            gate_results=original.gate_results)
                        corrected.append(candidate)
                    if corrected:
                        correction_review = _call(
                            clients.reviewer, "conditional_review",
                            {**review_input, "readiness_flags": [], "recommendations": [asdict(item) for item in corrected],
                             "drafting_artifacts": [], "call_scope": "core_correction"},
                            latency_ms, cancel_event=cancel_event, deadline=deadline, repair_allowance=repair_allowance,
                        )
                        correction_trace["review"] = _diagnostic_snapshot(correction_review)
                        verdict = _text(correction_review.get("verdict")).casefold()
                        corrected_ids = {item.recommendation_id for item in corrected}
                        correction_admission = reconcile_core_reviews(
                            correction_review,
                            (item.recommendation_id for item in corrected),
                            (item["block_id"] for item in block_records),
                        )
                        correction_trace["review_reconciliation"] = {
                            "passed_core_ids": list(correction_admission.passed_core_ids),
                            "affected_core_ids": list(correction_admission.affected_core_ids),
                            "invalid_core_ids": list(correction_admission.invalid_core_ids),
                            "reason_codes": list(correction_admission.reason_codes),
                        }
                        raw_targets = correction_review.get("object_ids")
                        raw_issues = correction_review.get("issues")
                        raw_codes = correction_review.get("reason_codes")
                        raw_core_reviews = correction_review.get("core_reviews")
                        known_targets = (
                            isinstance(raw_targets, list)
                            and all(isinstance(item, str) and item in corrected_ids
                                    for item in raw_targets)
                            and isinstance(raw_issues, list)
                            and all(isinstance(item, dict)
                                    and isinstance(item.get("object_id"), str)
                                    and item["object_id"] in corrected_ids
                                    for item in raw_issues)
                            and isinstance(raw_codes, list)
                            and isinstance(raw_core_reviews, list)
                            and all(isinstance(item, dict)
                                    and isinstance(item.get("recommendation_id"), str)
                                    and item["recommendation_id"] in corrected_ids
                                    for item in raw_core_reviews)
                        )
                        pass_is_clean = not (
                            verdict == "pass"
                            and (raw_targets or raw_issues or raw_codes)
                        )
                        verdict_is_coherent = (
                            (verdict == "pass" and pass_is_clean)
                            or (verdict in {"revise", "block"}
                                and bool(correction_admission.affected_core_ids))
                        )
                        if known_targets and verdict_is_coherent:
                            passed = set(correction_admission.passed_core_ids)
                            recovered = {item.recommendation_id: item for item in corrected
                                         if item.recommendation_id in passed}
                    correction_trace["recovered_ids"] = sorted(recovered)
                except PipelineCancelled:
                    raise
                except Exception as error:
                    # Optional repair must preserve already accepted actions; cancellation propagates.
                    correction_trace["failure"] = type(error).__name__
                affected_ids -= recovered.keys()
                priorities = tuple(recovered.get(item.recommendation_id, item) for item in priorities)
                correction_trace["withheld_ids"] = sorted(repair_ids - recovered.keys())
            draft_repair_ids = (affected_artifacts & issues_by_id.keys()
                                if reviewer_verdict == "revise" else set())
            draft_repair_ids = {identifier for identifier in draft_repair_ids
                                if identifier.split("::")[0] not in set(semantic_review_object_ids)}
            if draft_repair_ids:
                draft_trace = {"attempted_ids": sorted(draft_repair_ids), "recovered_ids": []}
                correction_trace["drafting"] = draft_trace
                parents = {item.recommendation_id: item for item in reviewed_priorities
                           if any(identifier.startswith(item.recommendation_id + "::")
                                  for identifier in draft_repair_ids)}
                try:
                    payload = _call(
                        clients.assessment, "drafting_compiler",
                        {**review_input, "readiness_flags": [], "recommendation_candidates": [asdict(item) for item in parents.values()],
                         "bounded_correction": [issues_by_id[key] for key in sorted(draft_repair_ids)], "call_scope": "draft_correction"},
                        latency_ms, cancel_event=cancel_event, deadline=deadline, repair_allowance=repair_allowance,
                    )
                    draft_trace["response"] = _diagnostic_snapshot(payload)
                    sets = _records(payload, "drafting_sets")
                    proposed = {}
                    artifacts = []
                    for drafting_set in sets:
                        parent_id = _text(drafting_set.get("recommendation_id"))
                        if parent_id not in parents or sum(_text(item.get("recommendation_id")) == parent_id for item in sets) != 1:
                            continue
                        original = parents[parent_id]
                        record = {**asdict(original), "current_document_drafting": None,
                                  "operational_instrument_drafting": None,
                                  "drafting_blocks": drafting_set.get("drafting_blocks")}
                        candidate, core_issues = normalize_candidate(_candidate(record))
                        if any(issue.blocking for issue in core_issues):
                            continue
                        for role, field in (("current_document", "current_document_drafting"),
                                            ("operational_instrument", "operational_instrument_drafting")):
                            identifier = f"{parent_id}::{role}"
                            block = getattr(candidate, field)
                            if identifier in draft_repair_ids and block is not None:
                                proposed[identifier] = block
                                artifacts.append({"object_id": identifier, "recommendation_id": parent_id,
                                                  "block": asdict(block)})
                    if artifacts:
                        second_review = _call(
                            clients.reviewer, "conditional_review",
                            {**review_input, "readiness_flags": [], "drafting_artifacts": artifacts, "call_scope": "draft_correction",
                             "recommendations": [asdict(replace(item, current_document_drafting=None,
                                                                operational_instrument_drafting=None))
                                                 for item in priorities if item.recommendation_id in parents]}, latency_ms,
                            cancel_event=cancel_event, deadline=deadline, repair_allowance=repair_allowance,
                        )
                        draft_trace["review"] = _diagnostic_snapshot(second_review)
                        reviewed_parent_ids = {
                            item.recommendation_id for item in priorities
                            if item.recommendation_id in parents
                        }
                        draft_admission = reconcile_core_reviews(
                            second_review,
                            reviewed_parent_ids,
                            (item["block_id"] for item in block_records),
                        )
                        draft_trace["review_reconciliation"] = {
                            "passed_core_ids": list(draft_admission.passed_core_ids),
                            "affected_core_ids": list(draft_admission.affected_core_ids),
                            "invalid_core_ids": list(draft_admission.invalid_core_ids),
                            "unsupported_core_ids": list(draft_admission.unsupported_core_ids),
                            "reason_codes": list(draft_admission.reason_codes),
                        }
                        draft_verdict = _text(second_review.get("verdict")).casefold()
                        raw_draft_targets = second_review.get("object_ids")
                        raw_draft_issues = second_review.get("issues")
                        draft_envelope_valid = (
                            isinstance(raw_draft_targets, list)
                            and all(isinstance(identifier, str)
                                    for identifier in raw_draft_targets)
                            and isinstance(raw_draft_issues, list)
                            and all(
                                isinstance(issue, dict)
                                and isinstance(issue.get("object_id"), str)
                                and isinstance(issue.get("explanation"), str)
                                and bool(issue["explanation"].strip())
                                and isinstance(issue.get("reason_codes"), list)
                                and bool(issue["reason_codes"])
                                and all(isinstance(code, str)
                                        and code in SEMANTIC_REVIEW_REASON_CODES
                                        for code in issue["reason_codes"])
                                for issue in raw_draft_issues
                            )
                        )
                        issue_targets = {
                            _text(issue.get("object_id"))
                            for issue in raw_draft_issues
                        } if draft_envelope_valid else set()
                        review_targets = (
                            set(raw_draft_targets) | issue_targets
                            if draft_envelope_valid else set()
                        )
                        known_review_targets = reviewed_parent_ids | set(proposed)
                        target_envelope_valid = (
                            draft_envelope_valid
                            and review_targets <= known_review_targets
                        )
                        draft_verdict_coherent = (
                            (draft_verdict == "pass"
                             and not review_targets
                             and not second_review.get("reason_codes"))
                            or (draft_verdict in {"revise", "block"}
                                and bool(review_targets))
                        )
                        # Only a valid, targeted, explicit unsupported premise can
                        # overturn the independently accepted parent decision.
                        newly_affected = (
                            set(draft_admission.unsupported_core_ids)
                            if target_envelope_valid and draft_verdict_coherent
                            else set()
                        )
                        affected_ids.update(newly_affected)
                        draft_premise_codes = _bounded_reason_codes([
                            code
                            for item in _records(second_review, "core_reviews")
                            if item.get("recommendation_id") in newly_affected
                            for code in _strings(item.get("reason_codes"))
                        ])
                        review_reasons.extend(code for code in draft_premise_codes
                                              if code not in review_reasons)
                        recommendation_reasons.extend(
                            code for code in draft_premise_codes
                            if code not in recommendation_reasons
                        )
                        reasons.extend(code for code in draft_premise_codes if code not in reasons)
                        if target_envelope_valid and draft_verdict_coherent:
                            passed_parents = set(draft_admission.passed_core_ids)
                            rejected_artifacts = review_targets
                            recoverable = {
                                identifier: block for identifier, block in proposed.items()
                                if identifier.split("::", 1)[0] in passed_parents
                                and identifier not in rejected_artifacts
                            }
                            priorities = tuple(replace(item, **{
                                field: recoverable.get(f"{item.recommendation_id}::{role}", getattr(item, field))
                                for role, field in (("current_document", "current_document_drafting"),
                                                    ("operational_instrument", "operational_instrument_drafting"))
                            }) for item in priorities)
                            draft_trace["recovered_ids"] = sorted(recoverable)
                except PipelineCancelled:
                    raise
                except Exception as error:
                    draft_trace["failure"] = type(error).__name__
            affected = [
                candidate
                for candidate in priorities
                if candidate.recommendation_id in affected_ids
            ]
            for candidate in affected:
                if len(candidate_suppressions) == 3:
                    break
                candidate_suppressions.append(
                    {
                        "recommendation_id": candidate.recommendation_id,
                        "stage": "semantic_review",
                        "reason_codes": review_reasons[:12],
                        "unsupported_numeric_fields": [],
                    }
                )
            suppressed["recommendations"] += len(affected)
            priorities = tuple(
                candidate
                for candidate in priorities
                if candidate.recommendation_id not in affected_ids
            )
            review_status = "attention"

    accepted_readiness = _reviewed_readiness_flags(readiness, review)
    if len(accepted_readiness) < len(readiness):
        suppressed["readiness_flags"] += len(readiness) - len(accepted_readiness)
        reasons.append("READINESS_FLAGS_NOT_ACCEPTED")
    readiness = accepted_readiness

    final_reader = {}
    reader_review = {}
    reader_trace = {'prechecks': [], 'meaning_reviews': []}
    assessment_narratives = _records(judgment_payload, 'assessment_narratives')
    if final_reader_required:
        # Reader generation is downstream of action admission and independent
        # review. Editorial/reader failures never alter accepted action count.
        reader_assessment = {
            'facts': [asdict(item) for item in facts],
            'derived_assertions': [asdict(item) for item in assertions],
            'analysis': analysis_record, 'context_evidence': context_records,
            'judgments': asdict(judgments), 'executive_readout': executive_readout,
            'priorities': [asdict(replace(item, current_document_drafting=None,
                                        operational_instrument_drafting=None)) for item in priorities],
        }
        support_records = reader_support_records(reader_assessment)
        reader_input = {
            'support_records': support_records, 'judgments': asdict(judgments),
            'source_passages': source_passages,
            'executive_readout': executive_readout,
            'accepted_recommendation_ids': [item.recommendation_id for item in priorities],
            'operation_context': resolved_context,
        }
        summary_overview_paragraphs, assessment_narratives = [], []
        summary_overview_status = 'fallback'
        try:
            final_reader = _call(clients.assessment, 'reader_compiler', reader_input, latency_ms,
                                 cancel_event=cancel_event, deadline=deadline)
            reader_trace['initial'] = _diagnostic_snapshot(final_reader)
            final_reader = normalize_reader_paragraphs(final_reader)
            final_reader, reference_repairs = bind_same_passage_project_references(final_reader, reader_assessment)
            if reference_repairs:
                repairs.append(f'FINAL_READER_SAME_PASSAGE_REFERENCES:{reference_repairs}')
            review_input_reader = reader_input
            for attempt in range(2):
                precheck_issues = []
                proposed_summary, _ = validate_final_reader(final_reader, reader_assessment, issues=precheck_issues)
                reader_trace['prechecks'].append({'attempt': attempt, 'issues': precheck_issues})
                reader_review = {}
                # Repairable text defects must not hide meaning defects from the
                # one available correction. Invalid evidence/structure still blocks.
                records_list = (final_reader.get('summary_paragraphs', [])
                                + final_reader.get('assessment_narratives', []))
                reviewable = all(
                    isinstance(record, dict)
                    and isinstance(record.get('evidence_ids'), list)
                    and record['evidence_ids']
                    and all(isinstance(ref, str) and ref in support_records
                            for ref in record['evidence_ids'])
                    for record in records_list)
                repairable_codes = {'SUMMARY_WORD_COUNT', 'READER_WORD_COUNT',
                                    'SUMMARY_DATE_UNSUPPORTED', 'SUMMARY_NUMBER_UNSUPPORTED',
                                    'SUMMARY_MARKUP', 'SUMMARY_EXECUTIVE_COPY',
                                    'SUMMARY_SENTENCE_INCOMPLETE'}
                reviewable = reviewable and all(
                    set(issue.get('reason_codes', [])) <= repairable_codes
                    for issue in precheck_issues)
                if proposed_summary or (not attempt and reviewable):
                    reader_review = _call(clients.reviewer, 'reader_review',
                        {**review_input_reader, 'final_reader': final_reader}, latency_ms,
                        cancel_event=cancel_event, deadline=deadline,
                        repair_allowance=repair_allowance if attempt else None)
                    reader_trace['meaning_reviews'].append(_diagnostic_snapshot(reader_review))
                    summary_overview_paragraphs, assessment_narratives = reviewed_final_reader(
                        final_reader, reader_review, reader_assessment)
                if summary_overview_paragraphs or attempt:
                    break
                # One targeted repair shares the existing correction allowance and
                # deadline. A block, unknown target or provider failure stays withheld.
                semantic_issues = reader_review.get('issues')
                verdict = reader_review.get('verdict')
                clean_pass = (verdict == 'pass' and semantic_issues == []
                              and reader_review.get('object_ids') == []
                              and reader_review.get('reason_codes') == [])
                valid_revision = _valid_reader_revision(reader_review, final_reader)
                if not (clean_pass or valid_revision):
                    reader_trace['unrepairable_issues'] = precheck_issues
                    reasons.extend(code for issue in precheck_issues for code in issue['reason_codes'])
                    break
                correction_issues = precheck_issues + (semantic_issues if valid_revision else [])
                records = {record['object_id']: record for record in records_list}
                issue_ids = {issue.get('object_id') for issue in correction_issues}
                if (not correction_issues or not issue_ids <= records.keys()
                        or any(set(issue.get('reason_codes', [])) & {'READER_EVIDENCE_INVALID', 'READER_STRUCTURE_INVALID'}
                               for issue in correction_issues)):
                    reader_trace['unrepairable_issues'] = correction_issues
                    reasons.extend(code for issue in correction_issues for code in issue.get('reason_codes', []))
                    break
                target_records = [records[key] for key in sorted(issue_ids)]
                refs = {ref for record in target_records for ref in record['evidence_ids']}
                correction_input = {
                    **reader_input, 'call_scope': 'reader_correction',
                    'support_records': {ref: support_records[ref] for ref in refs},
                    'source_passages': cited_source_passages(
                        [support_records[ref] for ref in refs if ref.startswith('PF-')], source_blocks),
                    'records_to_correct': target_records, 'bounded_correction': correction_issues,
                    'allowed_numeric_date_tokens_by_id': {
                        record['object_id']: reader_correction_allowed_numeric_date_tokens(record)
                        for record in target_records
                    },
                    'untargeted_summary_words': sum(len(record['text'].split())
                        for record in final_reader['summary_paragraphs'] if record['object_id'] not in issue_ids),
                }
                if any('SUMMARY_WORD_COUNT' in issue.get('reason_codes', [])
                       for issue in correction_issues):
                    summary_ids = [record['object_id'] for record in final_reader['summary_paragraphs']
                                   if record['object_id'] in issue_ids]
                    # Leave room below the admission ceiling; unchanged prose counts.
                    budget = max(0, 220 - correction_input['untargeted_summary_words'])
                    ceiling, remainder = divmod(budget, len(summary_ids))
                    correction_input['summary_max_words_by_id'] = {
                        identifier: ceiling + (index < remainder)
                        for index, identifier in enumerate(summary_ids)}
                correction = {'target_ids': sorted(issue_ids), 'issues': []}
                reader_trace['correction'] = correction
                repairs.append('FINAL_READER_TARGETED_CORRECTION_ATTEMPTED')
                response = _call(clients.assessment, 'reader_correction', correction_input, latency_ms,
                                 cancel_event=cancel_event, deadline=deadline, repair_allowance=repair_allowance)
                correction['response'] = _diagnostic_snapshot(response)
                merged = apply_reader_corrections(final_reader, response, issue_ids, issues=correction['issues'])
                if merged is None:
                    reasons.append('FINAL_READER_CORRECTION_SCOPE_INVALID')
                    reasons.extend(code for issue in correction['issues'] for code in issue['reason_codes'])
                    break
                final_reader = merged
                review_input_reader = {**reader_input, 'correction_originals': target_records}
            if summary_overview_paragraphs:
                summary_overview_status = 'generated'
            else:
                reasons.append('FINAL_READER_WITHHELD')
        except PipelineCancelled:
            raise
        except Exception as error:
            reasons.append('FINAL_READER_UNAVAILABLE')
            reader_review = {'failure': type(error).__name__}
            reader_trace['failure'] = type(error).__name__
        reader_trace['admission_status'] = summary_overview_status

    if parsed_candidate_count > 0 and not priorities:
        reasons.append("RECOMMENDATIONS_ALL_SUPPRESSED")
        recommendation_reasons.append("RECOMMENDATIONS_ALL_SUPPRESSED")
        review_status = "attention"

    unique_reasons = tuple(dict.fromkeys(reasons))
    if unique_reasons and review_status == "passed":
        review_status = "attention"
    applicability = _applicability_fingerprint(source_documents)
    call_metrics = tuple({**item, 'role': role}
                         for role, client in (('assessment', clients.assessment), ('reviewer', clients.reviewer))
                         for item in getattr(client, 'call_metrics', [])[metric_starts[role]:])
    token_usage = {}
    model_aliases = {'assessment': 'configured', 'reviewer': 'configured'}
    for item in call_metrics:
        if item.get('model'):
            model_aliases[item['role']] = item['model']
        for name, value in item.get('usage', {}).items():
            token_usage[name] = token_usage.get(name, 0) + value
    manifest = RunManifest(
        run_id=run_id,
        schema_version=CLIMATE_VERIFIED_SCHEMA_VERSION,
        prompt_versions=PROMPT_VERSIONS,
        reviewer_version="climate-review-v2.2",
        extraction_version="source-blocks-v3",
        normalization_version="climate-normalization-v2.13",
        renderer_version="climate-reader-v2.19",
        model_aliases=model_aliases,
        sampling={"max_transient_retries": 1,
                  "correction_transient_retries": 0,
                  "correction_output_token_allowance": CALL_BUDGETS["recommendation_compiler"].output_tokens,
                  "correction_output_token_remaining": repair_allowance["remaining"]},
        source_fingerprints=tuple(item.sha256 for item in source_documents),
        applicability_fingerprint=applicability,
        bank_release_id=bank_release_id,
        live_research_timestamps=tuple(
            item.source_ref.rsplit("retrieved=", 1)[-1]
            for item in context_evidence
            if item.source_ref.startswith("live:") and "retrieved=" in item.source_ref
        ),
        validation_reason_codes=unique_reasons,
        repair_actions=tuple(repairs),
        suppressed_counts=suppressed,
        accepted_live_evidence_ids=tuple(
            sorted({
                item.evidence_id for item in context_evidence
                if item.evidence_id.startswith("CE-LIVE-")
            })
        ),
        latency_ms=latency_ms,
        token_usage=token_usage,
        call_metrics=call_metrics,
        cache_state={"scope": "assessment", "status": "not_shared"},
    )
    preview = any(
        item.preview_status == "preview; not approved"
        for item in context_evidence
    )
    return {
        "schema_version": CLIMATE_VERIFIED_SCHEMA_VERSION,
        "run_id": run_id,
        "bank_release_id": bank_release_id,
        "evidence_status": "preview; not approved" if preview else "approved",
        "operation_context": resolved_context,
        "facts": [asdict(item) for item in facts],
        "derived_assertions": [asdict(item) for item in assertions],
        "analysis": analysis_record,
        "context_evidence": context_records,
        "judgments": asdict(judgments),
        "judgment_summary": deterministic_summary(judgments),
        "summary_overview": {"paragraphs": summary_overview_paragraphs},
        "summary_overview_status": summary_overview_status,
        "diagnostic_trace": {
            "summary_overview": _diagnostic_snapshot(raw_summary_overview),
            "summary_validation": summary_diagnostics,
            "recommendation_candidates": _diagnostic_snapshot(raw_candidates[:5]),
            "review_input": _diagnostic_snapshot(review_input),
            "reviewed_recommendations": _diagnostic_snapshot(review_input.get("recommendations", [])),
            "semantic_review": _diagnostic_snapshot(review),
            "recommendation_correction": correction_trace,
            "drafting_suppressions": drafting_suppressions,
            "final_reader": reader_trace,
        },
        "executive_readout": (
            executive_readout or deterministic_summary(judgments)
        ),
        "overview_summary": overview_summary,
        "core_questions": core_questions,
        "assessment_narratives": assessment_narratives,
        "reader_contract": "final-reader-v1" if final_reader_required else "legacy",
        "final_reader": final_reader,
        "reader_review": reader_review,
        "priorities": [asdict(item) for item in priorities],
        "review_readiness_flags": [asdict(item) for item in readiness],
        "minor_climate_points": minor_climate_points,
        "validation": {
            "status": review_status,
            "reason_codes": list(unique_reasons),
        },
        "recommendation_diagnostics": {
            "raw_candidate_count": len(raw_candidates),
            "parsed_candidate_count": parsed_candidate_count,
            "valid_candidate_count": len(candidates),
            "admitted_count": admitted_count,
            "final_priority_count": len(priorities),
            "reviewer_invoked": reviewer_invoked,
            "reviewer_verdict": reviewer_verdict,
            "reason_codes": list(dict.fromkeys(recommendation_reasons))[:12],
            "unsupported_numeric_tokens": unsupported_numbers,
            "semantic_review_object_ids": semantic_review_object_ids,
            "candidate_suppressions": candidate_suppressions,
        },
        "manifest": safe_log_summary(manifest),
    }
