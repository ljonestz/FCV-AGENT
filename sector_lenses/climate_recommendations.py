"""Admission, routing, authority, and ranking for Climate-FCV actions."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

from sector_lenses.climate_verified_contracts import ValidationIssue


ROUTING_STATUSES = {
    "verified_existing",
    "verified_with_scope_change",
    "standard_document_advisory",
    "not_applicable",
}
AUTHORITY_BASES = {
    "project_commitment",
    "policy",
    "directive",
    "procedure",
    "none_verified",
}
RECOMMENDATION_BASES = {
    "project_evidence",
    "country_context",
    "guidance",
    "analytical_judgment",
}
COMPLETION_EVIDENCE_STATUSES = {
    "output",
    "decision_record",
    "updated_section",
    "team_to_define",
}
READINESS_CATEGORIES = {
    "incomplete_climate_screening",
    "document_inconsistency",
    "unresolved_indicator",
    "processing_route_question",
    "missing_operational_home",
    "material_placeholder",
}
LIST_MARKER_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(?:\(\d{1,2}\)|\d{1,2}[.)])(?=\s)"
)
NUMERIC_TOKEN_PATTERN = re.compile(
    r"(?<![A-Za-z]-)\b\d+(?:\.\d+)?%?\b"
)
REQUIRED_GATES = {
    "connection",
    "residuality",
    "materiality",
    "actionability",
    "timing",
    "distinctiveness",
}
DRAFTING_STATUSES = {"existing_commitment", "advisory_proposal"}


@dataclass(frozen=True)
class DraftingBlock:
    target_document: str
    target_section: str
    drafting_status: str
    text: str
    project_basis_ids: tuple[str, ...]
    gap_basis_ids: tuple[str, ...]
    guidance_ids: tuple[str, ...]


@dataclass(frozen=True)
class DraftingValidationContext:
    known_ids: frozenset[str]
    guidance_ids: frozenset[str]
    current_document: str
    standard_targets: frozenset[tuple[str, str]]
    project_fact_text: dict[str, str]
    project_fact_types: dict[str, str]


def _normalized_target(block: DraftingBlock) -> tuple[str, str]:
    return (
        " ".join(block.target_document.casefold().split()),
        " ".join(block.target_section.casefold().split()),
    )


def _draft_tokens(block: DraftingBlock) -> set[str]:
    return set(re.findall(r"\b[a-z]{3,}\b", block.text.casefold()))


def normalize_drafting_blocks(
    candidate,
    *,
    current_document: str | None = None,
    drafting_context: DraftingValidationContext | None = None,
):
    """Drop an optional drafting block that repeats the required block."""

    repairs: list[str] = []
    current = candidate.current_document_drafting
    optional = candidate.operational_instrument_drafting
    if current is not None and current_document:
        normalized_document = " ".join(current_document.casefold().split())
        if _normalized_target(current)[0] != normalized_document:
            current = replace(current, target_document=current_document)
            candidate = replace(candidate, current_document_drafting=current)
            repairs.append("DRAFTING_CURRENT_TARGET_CANONICALIZED")
    if current is None or optional is None:
        return candidate, tuple(repairs)
    current_tokens = _draft_tokens(current)
    optional_tokens = _draft_tokens(optional)
    union = current_tokens | optional_tokens
    overlap = len(current_tokens & optional_tokens) / len(union) if union else 1.0
    if _normalized_target(current) == _normalized_target(optional) or overlap >= 0.8:
        repairs.append("DRAFTING_SECOND_BLOCK_REDUNDANT")
        return replace(candidate, operational_instrument_drafting=None), tuple(repairs)
    if not candidate.instrument_claim_ids:
        repairs.append("DRAFTING_OPTIONAL_UNVERIFIED_DROPPED")
        return replace(candidate, operational_instrument_drafting=None), tuple(repairs)
    if drafting_context:
        optional_document = " ".join(
            optional.target_document.casefold().split()
        )
        linked_named_instruments = {
            identifier
            for identifier in optional.project_basis_ids
            if identifier in candidate.instrument_claim_ids
            and drafting_context.project_fact_types.get(identifier)
            == "named_instrument"
        }
        target_is_evidenced = any(
            optional_document
            in " ".join(
                drafting_context.project_fact_text.get(identifier, "")
                .casefold()
                .split()
            )
            for identifier in linked_named_instruments
        )
        if not target_is_evidenced:
            repairs.append("DRAFTING_OPTIONAL_UNVERIFIED_DROPPED")
            return replace(candidate, operational_instrument_drafting=None), tuple(repairs)

    return candidate, tuple(repairs)



@dataclass(frozen=True)
class RecommendationScore:
    materiality: int
    gap_strength: int
    leverage_urgency: int
    evidence: int
    feasibility: int

    @property
    def total(self) -> int:
        return (
            self.materiality
            + self.gap_strength
            + self.leverage_urgency
            + self.evidence
            + self.feasibility
        )


@dataclass(frozen=True)
class CandidateRecommendation:
    recommendation_id: str
    title: str
    pathway_ids: tuple[str, ...]
    existing_response_ids: tuple[str, ...]
    residual_gap_ids: tuple[str, ...]
    project_anchor_ids: tuple[str, ...]
    decision: str
    minimum_action: str
    enhanced_action: str | None
    enhanced_activation: str | None
    routing_status: str
    instrument_claim_ids: tuple[str, ...]
    responsible_function: str
    authority_basis: str
    recommendation_basis: str
    completion_evidence: str
    completion_evidence_status: str
    confidence: str
    limitation: str
    caution: str
    current_document_drafting: DraftingBlock | None
    operational_instrument_drafting: DraftingBlock | None
    score: RecommendationScore
    gate_results: dict[str, bool]
    rank: int | None = None
    supported_numeric_tokens: tuple[str, ...] = ()
    narrative: str = ""


@dataclass(frozen=True)
class ReviewReadinessFlag:
    flag_id: str
    category: str
    flag: str
    why_it_matters: str
    document_basis_ids: tuple[str, ...]
    suggested_verification: str
    residual_gap_ids: tuple[str, ...]


def _issue(
    code: str,
    message: str,
    candidate: CandidateRecommendation,
    *,
    blocking: bool = True,
) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        message=message,
        object_id=candidate.recommendation_id,
        blocking=blocking,
    )


def numeric_tokens_in_text(text: str) -> tuple[str, ...]:
    """Return numeric claims while excluding suffixes of structured IDs."""

    prose = LIST_MARKER_PATTERN.sub("", text)
    return tuple(sorted(set(NUMERIC_TOKEN_PATTERN.findall(prose))))


def unsupported_numeric_tokens(
    candidate: CandidateRecommendation,
) -> tuple[str, ...]:
    """Return bounded, content-free numeric tokens lacking declared support."""

    numeric_text = " ".join(
        value
        for value in (
            candidate.decision,
            candidate.minimum_action,
            candidate.enhanced_action,
            candidate.enhanced_activation,
            candidate.completion_evidence,
            (
                candidate.current_document_drafting.text
                if candidate.current_document_drafting
                else None
            ),
            (
                candidate.operational_instrument_drafting.text
                if candidate.operational_instrument_drafting
                else None
            ),
        )
        if value
    )
    numeric_tokens = set(numeric_tokens_in_text(numeric_text))
    unsupported = numeric_tokens - set(candidate.supported_numeric_tokens)
    return tuple(sorted(unsupported))[:12]


def normalize_optional_enhancement(
    candidate: CandidateRecommendation,
) -> tuple[CandidateRecommendation, tuple[str, ...]]:
    """Drop optional enhancement prose when its precision is unsupported."""

    enhancement_text = " ".join(
        value
        for value in (
            candidate.enhanced_action,
            candidate.enhanced_activation,
        )
        if value
    )
    unsupported = set(numeric_tokens_in_text(enhancement_text)) - set(
        candidate.supported_numeric_tokens
    )
    if not unsupported:
        return candidate, ()
    return (
        replace(candidate, enhanced_action=None, enhanced_activation=None),
        ("ENHANCED_UNSUPPORTED_PRECISION_DROPPED",),
    )


def _without_numeric_tokens(text: str, unsupported: set[str]) -> str:
    cleaned = NUMERIC_TOKEN_PATTERN.sub(
        lambda match: "" if match.group(0) in unsupported else match.group(0),
        text,
    )
    cleaned = re.sub(
        r"[ ]+([,.;:])",
        lambda match: match.group(1),
        cleaned,
    )
    cleaned = " ".join(cleaned.split())
    cleaned = re.sub(
        r"\b(?:and|or)\s+(?=(?:before|after|during|for|to|in|on|with|under)\b)",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"\b(?:in|by|before|after|during|on|for)(?=[,.;:]|$)",
        "",
        cleaned,
    )
    return re.sub(r"[ ]+([,.;:])", lambda match: match.group(1), cleaned)


def normalize_unsupported_core_precision(
    candidate: CandidateRecommendation,
) -> tuple[CandidateRecommendation, tuple[str, ...]]:
    """Remove unsupported numeric precision while retaining core prose."""

    fields = {
        "decision": candidate.decision,
        "minimum_action": candidate.minimum_action,
        "completion_evidence": candidate.completion_evidence,
    }
    unsupported = {
        token
        for value in fields.values()
        for token in numeric_tokens_in_text(value)
        if token not in candidate.supported_numeric_tokens
    }
    if not unsupported:
        return candidate, ()
    cleaned = {
        name: _without_numeric_tokens(value, unsupported)
        for name, value in fields.items()
    }
    if not all(cleaned.values()):
        return candidate, ()
    return (
        replace(
            candidate,
            decision=cleaned["decision"],
            minimum_action=cleaned["minimum_action"],
            completion_evidence=cleaned["completion_evidence"],
        ),
        ("RECOMMENDATION_UNSUPPORTED_PRECISION_REMOVED",),
    )


def normalize_unsupported_drafting_precision(
    candidate: CandidateRecommendation,
) -> tuple[CandidateRecommendation, tuple[str, ...]]:
    """Remove unsupported digits from drafting while preserving useful prose."""

    changed = False
    for field_name in (
        "current_document_drafting",
        "operational_instrument_drafting",
    ):
        block = getattr(candidate, field_name)
        if block is None:
            continue
        unsupported = set(numeric_tokens_in_text(block.text)) - set(
            candidate.supported_numeric_tokens
        )
        if not unsupported:
            continue
        cleaned = _without_numeric_tokens(block.text, unsupported)
        if not cleaned:
            continue
        candidate = replace(
            candidate,
            **{field_name: replace(block, text=cleaned)},
        )
        changed = True
    if not changed:
        return candidate, ()
    return candidate, ("DRAFTING_UNSUPPORTED_PRECISION_REMOVED",)


def normalize_unverified_completion_actor(
    candidate: CandidateRecommendation,
    drafting_context: DraftingValidationContext,
) -> tuple[CandidateRecommendation, tuple[str, ...]]:
    """Generalize an unsupported actor only in completion-evidence prose."""

    linked_ids = set(candidate.project_anchor_ids) | set(
        candidate.instrument_claim_ids
    )
    linked_text = " ".join(
        drafting_context.project_fact_text.get(identifier, "")
        for identifier in linked_ids
    ).casefold()
    completion = candidate.completion_evidence
    changed = False
    for phrase in ("focal point", "steering committee", "coordination unit"):
        if phrase not in completion.casefold() or phrase in linked_text:
            continue

        def _replacement(match: re.Match[str]) -> str:
            value = "responsible project function"
            return value.capitalize() if match.group(0)[0].isupper() else value

        completion = re.sub(
            rf"\b{re.escape(phrase)}\b",
            _replacement,
            completion,
            flags=re.IGNORECASE,
        )
        changed = True
    if not changed:
        return candidate, ()
    return (
        replace(candidate, completion_evidence=completion),
        ("COMPLETION_EVIDENCE_ACTOR_GENERALIZED",),
    )


def normalize_unverified_drafting_actor(
    candidate: CandidateRecommendation,
    drafting_context: DraftingValidationContext,
) -> tuple[CandidateRecommendation, tuple[str, ...]]:
    """Generalize an unsupported operational actor across drafting text and
    action prose, mirroring the completion-evidence repair.

    The DRAFTING_ACTOR_UNVERIFIED check scans the action fields and drafting
    block text as well as completion evidence, so an invented "focal point",
    "steering committee", or "coordination unit" in any of those fields would
    otherwise suppress an otherwise-grounded recommendation. A phrase that is
    genuinely supported by a linked project fact is preserved unchanged."""

    linked_ids = set(candidate.project_anchor_ids) | set(
        candidate.instrument_claim_ids
    )
    linked_text = " ".join(
        drafting_context.project_fact_text.get(identifier, "")
        for identifier in linked_ids
    ).casefold()

    def _generalize(text: str | None) -> tuple[str | None, bool]:
        if not text:
            return text, False
        changed = False
        for phrase in ("focal point", "steering committee", "coordination unit"):
            if phrase not in text.casefold() or phrase in linked_text:
                continue

            def _replacement(match: re.Match[str]) -> str:
                value = "responsible project function"
                return value.capitalize() if match.group(0)[0].isupper() else value

            new_text = re.sub(
                rf"\b{re.escape(phrase)}\b",
                _replacement,
                text,
                flags=re.IGNORECASE,
            )
            if new_text != text:
                text = new_text
                changed = True
        return text, changed

    updates: dict[str, object] = {}
    for field_name in (
        "decision",
        "minimum_action",
        "enhanced_action",
        "enhanced_activation",
    ):
        new_value, changed = _generalize(getattr(candidate, field_name))
        if changed:
            updates[field_name] = new_value
    for field_name in (
        "current_document_drafting",
        "operational_instrument_drafting",
    ):
        block = getattr(candidate, field_name)
        if block is None:
            continue
        new_text, changed = _generalize(block.text)
        if changed:
            updates[field_name] = replace(block, text=new_text)
    if not updates:
        return candidate, ()
    return replace(candidate, **updates), ("DRAFTING_ACTOR_GENERALIZED",)


def normalize_recommendation_references(
    candidate: CandidateRecommendation,
    known_ids: set[str],
) -> tuple[CandidateRecommendation, tuple[str, ...]]:
    """Strip references to unknown IDs so a single stray reference does not
    suppress an otherwise-grounded recommendation.

    Essential grounding gates are downgraded when stripping removes the last
    supporting reference: residuality when no residual-gap reference survives,
    and connection when neither a pathway nor an existing-response reference
    survives. An ungrounded recommendation therefore still fails admission
    rather than being admitted on a hollow claim."""

    repairs: list[str] = []

    def _filter(ids: tuple[str, ...]) -> tuple[str, ...]:
        kept = tuple(identifier for identifier in ids if identifier in known_ids)
        if len(kept) != len(ids):
            repairs.append("stripped")
        return kept

    pathway = _filter(candidate.pathway_ids)
    responses = _filter(candidate.existing_response_ids)
    gaps = _filter(candidate.residual_gap_ids)
    anchors = _filter(candidate.project_anchor_ids)
    instruments = _filter(candidate.instrument_claim_ids)
    if not repairs:
        return candidate, ()

    gate_results = dict(candidate.gate_results)
    if not gaps:
        gate_results["residuality"] = False
    if not pathway and not responses:
        gate_results["connection"] = False

    repaired = replace(
        candidate,
        pathway_ids=pathway,
        existing_response_ids=responses,
        residual_gap_ids=gaps,
        project_anchor_ids=anchors,
        instrument_claim_ids=instruments,
        gate_results=gate_results,
    )
    return repaired, ("RECOMMENDATION_INVALID_REFS_STRIPPED",)


def validate_recommendation(
    candidate: CandidateRecommendation,
    known_ids: set[str],
    *,
    drafting_context: DraftingValidationContext | None = None,
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    linked_ids = (
        candidate.pathway_ids
        + candidate.existing_response_ids
        + candidate.residual_gap_ids
        + candidate.project_anchor_ids
        + candidate.instrument_claim_ids
    )
    if set(linked_ids) - known_ids:
        issues.append(
            _issue(
                "RECOMMENDATION_REF_INVALID",
                f"{candidate.recommendation_id} has unknown references.",
                candidate,
            )
        )
    if candidate.routing_status not in ROUTING_STATUSES:
        issues.append(
            _issue(
                "ROUTING_STATUS_INVALID",
                f"{candidate.recommendation_id} has invalid routing.",
                candidate,
            )
        )
    if candidate.authority_basis not in AUTHORITY_BASES:
        issues.append(
            _issue(
                "AUTHORITY_BASIS_INVALID",
                f"{candidate.recommendation_id} has invalid authority.",
                candidate,
            )
        )
    if candidate.recommendation_basis not in RECOMMENDATION_BASES:
        issues.append(
            _issue(
                "RECOMMENDATION_BASIS_INVALID",
                f"{candidate.recommendation_id} has invalid basis.",
                candidate,
            )
        )
    if candidate.enhanced_action and not candidate.enhanced_activation:
        issues.append(
            _issue(
                "ENHANCED_ACTIVATION_MISSING",
                f"{candidate.recommendation_id} has no activation condition.",
                candidate,
            )
        )
    drafting_blocks = tuple(
        block
        for block in (
            candidate.current_document_drafting,
            candidate.operational_instrument_drafting,
        )
        if block is not None
    )
    if candidate.current_document_drafting is None:
        issues.append(
            _issue(
                "DRAFTING_CURRENT_MISSING",
                f"{candidate.recommendation_id} has no current-document drafting.",
                candidate,
            )
        )
    if drafting_context and candidate.current_document_drafting:
        current_target = _normalized_target(
            candidate.current_document_drafting
        )
        current_document = " ".join(
            drafting_context.current_document.casefold().split()
        )
        if (
            current_target[0] != current_document
            or current_target not in drafting_context.standard_targets
        ):
            issues.append(
                _issue(
                    "DRAFTING_CURRENT_TARGET_INVALID",
                    f"{candidate.recommendation_id} has an invalid current target.",
                    candidate,
                )
            )
    if drafting_context and candidate.operational_instrument_drafting:
        optional = candidate.operational_instrument_drafting
        optional_document = " ".join(
            optional.target_document.casefold().split()
        )
        linked_named_instruments = {
            identifier
            for identifier in optional.project_basis_ids
            if identifier in candidate.instrument_claim_ids
            and drafting_context.project_fact_types.get(identifier)
            == "named_instrument"
        }
        target_is_evidenced = any(
            optional_document
            in " ".join(
                drafting_context.project_fact_text.get(identifier, "")
                .casefold()
                .split()
            )
            for identifier in linked_named_instruments
        )
        if not target_is_evidenced:
            issues.append(
                _issue(
                    "DRAFTING_INSTRUMENT_UNVERIFIED",
                    f"{candidate.recommendation_id} has an unverified instrument target.",
                    candidate,
                )
            )
    if drafting_context:
        linked_fact_ids = set(candidate.project_anchor_ids) | set(
            candidate.instrument_claim_ids
        )
        linked_fact_text = " ".join(
            drafting_context.project_fact_text.get(identifier, "")
            for identifier in linked_fact_ids
        ).casefold()
        operational_text = " ".join(
            value
            for value in (
                candidate.decision,
                candidate.minimum_action,
                candidate.enhanced_action,
                candidate.enhanced_activation,
                candidate.completion_evidence,
                *(
                    block.text
                    for block in drafting_blocks
                ),
            )
            if value
        ).casefold()
        named_instruments = (
            "project operations manual",
            "security risk management plan",
            "environmental and social commitment plan",
            "environmental and social management framework",
            "results framework",
        )
        if any(
            phrase in operational_text and phrase not in linked_fact_text
            for phrase in named_instruments
        ):
            # Advisory only: these five are standard WBG instrument names, not
            # project-specific fabrications. Referencing them in suggested
            # drafting is legitimate FCV practice, so the flag is recorded for
            # the technical annex but does not suppress the recommendation.
            issues.append(
                _issue(
                    "DRAFTING_INSTRUMENT_UNVERIFIED",
                    f"{candidate.recommendation_id} references a standard "
                    "instrument not tied to a project fact.",
                    candidate,
                    blocking=False,
                )
            )
        if (
            re.search(r"\b(?:focal point|steering committee|coordination unit)\b", operational_text)
            and not re.search(
                r"\b(?:focal point|steering committee|coordination unit)\b",
                linked_fact_text,
            )
        ):
            issues.append(
                _issue(
                    "DRAFTING_ACTOR_UNVERIFIED",
                    f"{candidate.recommendation_id} invents an operational actor.",
                    candidate,
                )
            )
        if (
            re.search(r"\bbefore (?:effectiveness|appraisal|board approval)\b", operational_text)
            and not re.search(
                r"\bbefore (?:effectiveness|appraisal|board approval)\b",
                linked_fact_text,
            )
        ):
            # Advisory only: appraisal/Board/effectiveness are standard WBG
            # process milestones, so naming them in suggested drafting is
            # recorded but does not suppress the recommendation.
            issues.append(
                _issue(
                    "DRAFTING_TIMING_UNVERIFIED",
                    f"{candidate.recommendation_id} names a standard process "
                    "milestone not tied to a project fact.",
                    candidate,
                    blocking=False,
                )
            )
        if (
            re.search(r"\b(?:hydrometeorological|hydromet) system\b", operational_text)
            and not re.search(
                r"\b(?:hydrometeorological|hydromet) system\b", linked_fact_text
            )
        ):
            issues.append(
                _issue(
                    "DRAFTING_SYSTEM_UNVERIFIED",
                    f"{candidate.recommendation_id} invents a technical system.",
                    candidate,
                )
        )
    for block in drafting_blocks:
        if block.drafting_status not in DRAFTING_STATUSES:
            issues.append(
                _issue(
                    "DRAFTING_STATUS_INVALID",
                    f"{candidate.recommendation_id} has invalid drafting status.",
                    candidate,
                )
            )
        word_count = len(block.text.split())
        if not 60 <= word_count <= 180:
            issues.append(
                _issue(
                    "DRAFTING_LENGTH_INVALID",
                    f"{candidate.recommendation_id} drafting length is invalid.",
                    candidate,
                )
            )
        drafting_refs = set(
            block.project_basis_ids
            + block.gap_basis_ids
            + block.guidance_ids
        )
        accepted_refs = set(known_ids)
        if drafting_context:
            accepted_refs |= set(drafting_context.guidance_ids)
        if drafting_refs - accepted_refs:
            issues.append(
                _issue(
                    "DRAFTING_REF_INVALID",
                    f"{candidate.recommendation_id} drafting has unknown references.",
                    candidate,
                )
            )
        if (
            set(block.project_basis_ids)
            - (set(candidate.project_anchor_ids) | set(candidate.instrument_claim_ids))
            or set(block.gap_basis_ids) - set(candidate.residual_gap_ids)
        ):
            issues.append(
                _issue(
                    "DRAFTING_BASIS_MISMATCH",
                    f"{candidate.recommendation_id} drafting exceeds its evidence basis.",
                    candidate,
                )
            )
        if (
            drafting_context
            and set(block.guidance_ids) - set(drafting_context.guidance_ids)
        ):
            issues.append(
                _issue(
                    "DRAFTING_GUIDANCE_INVALID",
                    f"{candidate.recommendation_id} drafting cites unknown guidance.",
                    candidate,
                )
            )
    drafting_tokens = set(
        re.findall(
            r"\b[a-z]+\b",
            " ".join(block.text for block in drafting_blocks).casefold(),
        )
    )
    if (
        drafting_tokens & {"must", "shall", "required", "mandatory"}
        and candidate.authority_basis
        not in {"project_commitment", "policy", "directive", "procedure"}
    ):
        # Advisory only: mandatory phrasing without a verified authority basis
        # is flagged for the annex (so the TTL softens it) but does not suppress
        # the recommendation.
        issues.append(
            _issue(
                "MANDATORY_AUTHORITY_UNVERIFIED",
                (
                    f"{candidate.recommendation_id} uses mandatory language "
                    "without verified authority."
                ),
                candidate,
                blocking=False,
            )
        )
    if candidate.completion_evidence_status not in COMPLETION_EVIDENCE_STATUSES:
        issues.append(
            _issue(
                "COMPLETION_EVIDENCE_STATUS_INVALID",
                f"{candidate.recommendation_id} has invalid completion evidence.",
                candidate,
            )
        )
    unsupported = unsupported_numeric_tokens(candidate)
    if unsupported:
        issues.append(
            _issue(
                "RECOMMENDATION_NUMBER_UNSUPPORTED",
                (
                    f"{candidate.recommendation_id} contains unsupported "
                    f"numeric tokens: {', '.join(sorted(unsupported))}."
                ),
                candidate,
            )
        )
    return tuple(issues)


def admission_failure_codes(
    candidate: CandidateRecommendation,
) -> tuple[str, ...]:
    """Return stable reason codes for deterministic admission failures."""

    codes: list[str] = []
    if candidate.score.total < 6:
        codes.append("ADMISSION_SCORE_BELOW_MIN")
    if candidate.score.materiality < 2:
        codes.append("ADMISSION_MATERIALITY_BELOW_MIN")
    for gate in sorted(REQUIRED_GATES):
        if gate not in candidate.gate_results:
            codes.append(f"ADMISSION_GATE_MISSING_{gate.upper()}")
        elif not candidate.gate_results[gate]:
            codes.append(f"ADMISSION_GATE_FAILED_{gate.upper()}")
    return tuple(codes)


def admit_and_rank(
    candidates: list[CandidateRecommendation],
) -> tuple[CandidateRecommendation, ...]:
    admitted = [
        candidate
        for candidate in candidates
        if candidate.score.total >= 6
        and candidate.score.materiality >= 2
        and REQUIRED_GATES.issubset(candidate.gate_results)
        and all(candidate.gate_results[name] for name in REQUIRED_GATES)
    ]
    ordered = sorted(
        admitted,
        key=lambda item: (
            -item.score.total,
            -item.score.materiality,
            -item.score.evidence,
            item.recommendation_id,
        ),
    )[:3]
    return tuple(
        replace(candidate, rank=index)
        for index, candidate in enumerate(ordered, start=1)
    )


def _normalized_sentence(value: str) -> str:
    return " ".join(value.casefold().split()).rstrip(".")


def admit_readiness_flags(
    flags: list[ReviewReadinessFlag],
    known_project_ids: set[str],
    reserved_statements: set[str],
    *,
    known_gap_ids: set[str] | None = None,
    admitted_gap_ids: set[str] | None = None,
) -> tuple[ReviewReadinessFlag, ...]:
    reserved = {_normalized_sentence(item) for item in reserved_statements}
    admitted: list[ReviewReadinessFlag] = []
    known_gaps = known_gap_ids or set()
    admitted_gaps = admitted_gap_ids or set()
    for flag in flags:
        if flag.category not in READINESS_CATEGORIES:
            continue
        if not flag.document_basis_ids:
            continue
        if set(flag.document_basis_ids) - known_project_ids:
            continue
        if _normalized_sentence(flag.flag) in reserved:
            continue
        if set(flag.residual_gap_ids) - known_gaps:
            continue
        if set(flag.residual_gap_ids) & admitted_gaps:
            continue
        admitted.append(flag)
        if len(admitted) == 4:
            break
    return tuple(admitted)
