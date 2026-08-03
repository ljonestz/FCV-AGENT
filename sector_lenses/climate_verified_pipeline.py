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
from typing import Protocol

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
    RecommendationScore,
    ReviewReadinessFlag,
    admit_and_rank,
    admission_failure_codes,
    admit_readiness_flags,
    normalize_drafting_blocks,
    numeric_tokens_in_text,
    normalize_optional_enhancement,
    normalize_unsupported_core_precision,
    unsupported_numeric_tokens,
    validate_recommendation,
)
from sector_lenses.climate_run_manifest import RunManifest, safe_log_summary
from sector_lenses.climate_semantic_review import (
    ReviewRisk,
    semantic_review_required,
)
from sector_lenses.climate_source_blocks import SourceBlock, SourceDocument
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


PROMPT_VERSIONS = {
    "fact_extraction": "climate-facts-v2.2",
    "bounded_analysis": "climate-analysis-v2.2",
    "judgment_review": "climate-judgments-v2.3",
    "recommendation_compiler": "climate-recommendations-v2.4",
    "conditional_review": "climate-review-v2.4",
    "drafting_compiler": "climate-drafting-v1.0",
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
        if code not in codes:
            codes.append(code)
        if len(codes) == 12:
            break
    return codes


def _text(value: object, default: str = "") -> str:
    cleaned = str(value or "").strip()
    return cleaned or default


def _as_record(value: object) -> dict[str, object]:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    return dict(value) if isinstance(value, dict) else {}


def _call(
    client: JsonClient,
    stage: str,
    payload: dict[str, object],
    latency_ms: dict[str, int],
    *,
    cancel_event: object | None = None,
    deadline: float | None = None,
) -> dict[str, object]:
    cancelled = getattr(cancel_event, "is_set", lambda: False)
    if cancelled():
        raise RuntimeError("Verified Climate-FCV pipeline cancelled")
    budget = CALL_BUDGETS[stage]
    remaining = (
        budget.timeout_seconds
        if deadline is None
        else min(budget.timeout_seconds, int(deadline - time.monotonic()))
    )
    if remaining < 1:
        raise TimeoutError("Verified Climate-FCV pipeline exceeded its wall-clock limit")
    started = time.monotonic()
    result = client.complete_json(
        stage=stage,
        payload=payload,
        timeout_seconds=remaining,
        max_output_tokens=budget.output_tokens,
        max_transient_retries=1,
    )
    latency_ms[stage] = int((time.monotonic() - started) * 1000)
    if cancelled():
        raise RuntimeError("Verified Climate-FCV pipeline cancelled")
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
    wall_clock_seconds: int = 14 * 60,
) -> dict[str, object]:
    """Run the automatic pipeline and return only validated reader objects."""
    if wall_clock_seconds < 1:
        raise ValueError("wall_clock_seconds must be positive")
    deadline = time.monotonic() + wall_clock_seconds
    latency_ms: dict[str, int] = {}
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
    guidance = select_operational_guidance(
        doc_type=doc_type,
        instrument_type=instrument_type,
    )
    document_records = [_as_record(item) for item in source_documents]
    block_records = [_as_record(item) for item in source_blocks]
    context_records = [_as_record(item) for item in context_evidence]

    fact_payload = _call(
        clients.assessment,
        "fact_extraction",
        {"documents": document_records, "source_blocks": block_records},
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

    analysis_payload = _call(
        clients.assessment,
        "bounded_analysis",
        {
            "facts": [asdict(item) for item in facts],
            "derived_assertions": [asdict(item) for item in assertions],
            "context_evidence": context_records,
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

    judgment_payload = _call(
        clients.assessment,
        "judgment_review",
        {
            "facts": [asdict(item) for item in facts],
            "analysis": analysis_record,
        },
        latency_ms,
        cancel_event=cancel_event,
        deadline=deadline,
    )
    judgments = _judgments(judgment_payload)
    executive_readout = _text(judgment_payload.get("executive_readout"))
    known_ids = (
        fact_ids
        | {item.assertion_id for item in assertions}
        | {item.response_id for item in responses}
        | {item.pathway_id for item in pathways}
        | {item.gap_id for item in gaps}
        | {item.evidence_id for item in context_evidence}
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

    recommendation_payload = _call(
        clients.assessment,
        "recommendation_compiler",
        {
            "facts": [asdict(item) for item in facts],
            "analysis": analysis_record,
            "judgments": asdict(judgments),
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
                "analysis": analysis_record,
                "judgments": asdict(judgments),
                "recommendation_candidates": candidates_missing_drafting,
                "current_document": doc_type,
                "instrument_type": instrument_type,
                "guidance_registry_version": GUIDANCE_REGISTRY_VERSION,
                "operational_guidance": [
                    item.as_record() for item in guidance
                ],
            },
            latency_ms,
            cancel_event=cancel_event,
            deadline=deadline,
        )
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
    parsed_candidate_count = 0
    candidates: list[CandidateRecommendation] = []
    for record in raw_candidates:
        try:
            candidate = _candidate(record)
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
        )
        candidate, evidence_repairs = normalize_drafting_blocks(
            candidate,
            current_document=doc_type,
            drafting_context=drafting_context,
        )
        repairs.extend(evidence_repairs)
        for token in unsupported_numeric_tokens(candidate):
            if token not in unsupported_numbers and len(unsupported_numbers) < 12:
                unsupported_numbers.append(token)
        issues = validate_recommendation(
            candidate, known_ids, drafting_context=drafting_context
        )
        if issues:
            suppressed["recommendations"] += 1
            reasons.extend(issue.code for issue in issues)
            recommendation_reasons.extend(issue.code for issue in issues)
            if len(candidate_suppressions) < 3:
                candidate_suppressions.append(
                    {
                        "recommendation_id": candidate.recommendation_id,
                        "stage": "validation",
                        "reason_codes": list(
                            dict.fromkeys(issue.code for issue in issues)
                        )[:12],
                        "unsupported_numeric_fields": (
                            _unsupported_numeric_fields(candidate)
                        ),
                    }
                )
                precision_fields = _unsupported_precision_fields(
                    candidate,
                    {issue.code for issue in issues},
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
    readiness = admit_readiness_flags(
        flags,
        fact_ids,
        {item.statement for item in gaps},
        known_gap_ids={item.gap_id for item in gaps},
        admitted_gap_ids={
            gap_id for item in priorities for gap_id in item.residual_gap_ids
        },
    )
    suppressed["readiness_flags"] += len(raw_flags) - len(readiness)

    review_status = "passed"
    reviewer_invoked = False
    reviewer_verdict = "not_invoked"
    semantic_review_object_ids: list[str] = []
    if priorities and semantic_review_required(_risk(priorities)):
        reviewer_invoked = True
        review = _call(
            clients.reviewer,
            "conditional_review",
            {
                "source_blocks": block_records,
                "facts": [asdict(item) for item in facts],
                "analysis": analysis_record,
                "judgments": asdict(judgments),
                "recommendations": [asdict(item) for item in priorities],
            },
            latency_ms,
            cancel_event=cancel_event,
            deadline=deadline,
        )
        reviewer_verdict = _text(review.get("verdict"), "block").casefold()
        review_reasons = _bounded_reason_codes(review.get("reason_codes"))
        priority_ids = {item.recommendation_id for item in priorities}
        semantic_review_object_ids = list(
            dict.fromkeys(
                object_id
                for object_id in _strings(review.get("object_ids"))
                if object_id in priority_ids
            )
        )[:12]
        if reviewer_verdict not in {"pass", "revise", "block"}:
            reviewer_verdict = "block"
            review_reasons.append("SEMANTIC_REVIEW_VERDICT_INVALID")
        if reviewer_verdict != "pass" and not semantic_review_object_ids:
            review_reasons.append("SEMANTIC_REVIEW_TARGET_UNRESOLVED")
            semantic_review_object_ids = sorted(priority_ids)
        reasons.extend(review_reasons)
        recommendation_reasons.extend(review_reasons)
        if reviewer_verdict != "pass":
            affected_ids = set(semantic_review_object_ids)
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

    unique_reasons = tuple(dict.fromkeys(reasons))
    if unique_reasons and review_status == "passed":
        review_status = "attention"
    applicability = _applicability_fingerprint(source_documents)
    manifest = RunManifest(
        run_id=run_id,
        schema_version=CLIMATE_VERIFIED_SCHEMA_VERSION,
        prompt_versions=PROMPT_VERSIONS,
        reviewer_version="climate-review-v2.1",
        extraction_version="source-blocks-v2.1",
        normalization_version="climate-normalization-v2.1",
        renderer_version="climate-reader-v2.2",
        model_aliases={"assessment": "configured", "reviewer": "configured"},
        sampling={"temperature": 0, "max_transient_retries": 1},
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
        token_usage={},
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
        "facts": [asdict(item) for item in facts],
        "derived_assertions": [asdict(item) for item in assertions],
        "analysis": analysis_record,
        "judgments": asdict(judgments),
        "judgment_summary": deterministic_summary(judgments),
        "executive_readout": (
            executive_readout or deterministic_summary(judgments)
        ),
        "priorities": [asdict(item) for item in priorities],
        "review_readiness_flags": [asdict(item) for item in readiness],
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
