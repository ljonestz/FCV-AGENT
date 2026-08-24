"""Native JSON schemas for verified Climate-FCV model stages.

The schemas constrain transport shape only. Deterministic domain validation,
reference checks, recommendation admission, and semantic review remain the
authoritative analytical controls.
"""

from __future__ import annotations

from copy import deepcopy
import re


_SUMMARY_DIMENSION_SIGNALS = {
    "relevance": ("relevance",),
    "sensitivity": ("sensitivity",),
    "responsiveness": ("responsiveness",),
    "operationalization": ("operationalization", "operationalisation"),
}
_SUMMARY_GENERIC_ENTITIES = {"task team", "project team", "implementation team"}
_SUMMARY_CONNECTIVE_TOKENS = {
    "however", "therefore", "while", "although", "together", "already",
    "partly", "largely", "clearly", "still", "broadly", "similarly",
    "additionally", "but", "yet", "also", "instead", "generally",
    "often", "typically", "notably", "meanwhile", "despite",
}
_SUMMARY_ALLOWED_SINGLE_WORDS = {
    "the", "this", "overall", "project", "climate", "fcv", "relevance",
    "sensitivity", "responsiveness", "operationalization", "operationalisation",
    "assessment", "finding", "practical", "remaining", "four", "first",
    "second", "third", "verdict", "foundation", "takeaway", "credible",
    "recognizes", "recognises", "shows", "demonstrates",
}
_SUMMARY_ACTION_STEM_RE = re.compile(
    r"\b(?P<stem>approv|requir|monitor|implement|adopt|ensur|establish|"
    r"creat|launch|form|appoint|mandat|commit|fund|build|develop|strengthen|"
    r"revis|updat|integrat|incorporat|designat|allocat|caus|reduc|prevent|lead)"
    r"[a-z-]*\b",
    re.IGNORECASE,
)
_SUMMARY_ALLOWED_TOKENS = {
    "climate", "fcv", "project", "design", "risk", "risks", "overall",
    "takeaway", "credible", "recognizes", "recognises", "interaction",
    "verdict", "foundation", "assessment", "practical", "implication",
    "confirm", "confirmed", "check", "checks", "clarify", "clarifies",
    "review", "reviews", "assess", "assesses", "consider", "considers",
    "note", "notes", "next", "priorities", "priority", "bridge",
    "material", "residual", "gap", "gaps", "relevance", "sensitivity",
    "responsiveness", "operationalization", "operationalisation", "do",
    "harm", "resilience", "inclusion", "roles", "indicators", "follows",
    "supports", "sets", "four-dimensional", "climate-fcv", "new", "ranked",
    "criteria",
}
_SUMMARY_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "in", "is", "it", "its", "of", "on", "or", "that", "the",
    "their", "them", "this", "to", "was", "what", "will", "with", "where",
}
_SUMMARY_MONTHS = (
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december",
)
_SUMMARY_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9'/-]*")
_SUMMARY_CAPITALIZED_RE = re.compile(r"\b[A-Z][a-z]{2,}\b")
_SUMMARY_ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,}\b")
_SUMMARY_ENTITY_RE = re.compile(
    r"\b(?:[A-Z][a-z]+(?:[-'][A-Za-z]+)?(?:\s+[A-Z][a-z]+(?:[-'][A-Za-z]+)?)+)\b"
)
_SUMMARY_MARKUP_RE = re.compile(
    r"<[^>]+>|`|\*\*|__|~~|\[[^\]]+\]\([^)]+\)|(?:^|\n)[#>*-]\s+[^\n]*|(?:^|\n)\d+\.\s|(?:^|\s)_[^_]+_|(?:^|\s)\*[^*]+\*"
)


def _summary_strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _summary_strings(item)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            yield from _summary_strings(item)


def _summary_normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def _summary_sentences(value: str) -> list[str]:
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", _summary_normalize(value))
        if sentence.strip() and sentence.strip()[-1:] in ".?!"
    ]


def _summary_words(value: str) -> set[str]:
    return {
        word.casefold()
        for word in _SUMMARY_WORD_RE.findall(value)
        if word.casefold() not in _SUMMARY_STOPWORDS and len(word) >= 3
    }


_SUMMARY_MORPH_SUFFIXES = (
    ("ation", ""), ("tion", ""), ("sion", ""), ("ment", ""),
    ("ness", ""), ("ence", ""), ("ing", ""), ("ied", "y"),
    ("ies", "y"), ("ed", ""), ("es", ""), ("ly", ""),
    ("ent", ""), ("ive", ""), ("al", ""), ("er", ""), ("s", ""),
 )


def _summary_morphology_supported(word: str, canonical_words: set[str]) -> bool:
    def forms(value: str) -> set[str]:
        variants = {value}
        for suffix, replacement in _SUMMARY_MORPH_SUFFIXES:
            if value.endswith(suffix) and len(value) - len(suffix) >= 5:
                variants.add(value[:-len(suffix)] + replacement)
        return variants
    return any(
        forms(word) & forms(candidate)
        for candidate in canonical_words
    )


def validate_summary_overview(
    value: object,
    *,
    executive_readout: object = "",
    canonical_text: object = (),
) -> list[str]:
    """Admit only a grounded, plain-text two/three-paragraph synthesis."""
    raw = value.get("paragraphs") if isinstance(value, dict) else None
    if not isinstance(raw, list) or len(raw) not in {2, 3}:
        return []
    if any(not isinstance(item, str) or not item.strip() for item in raw):
        return []
    if any(_SUMMARY_MARKUP_RE.search(item) for item in raw):
        return []
    paragraphs = [_summary_normalize(item) for item in raw]
    if not 160 <= sum(len(item.split()) for item in paragraphs) <= 230:
        return []
    if any(_SUMMARY_MARKUP_RE.search(item) for item in paragraphs):
        return []
    combined = " ".join(paragraphs).casefold()
    if not all(
        any(signal in combined for signal in signals)
        for signals in _SUMMARY_DIMENSION_SIGNALS.values()
    ):
        return []
    if not any(
        signal in paragraphs[0].casefold()
        for signal in ("verdict", "foundation", "overall", "credible", "takeaway", "recognizes", "recognises", "shows", "demonstrates", "assessment", "finding")
    ):
        return []
    if not any(
        signal in combined
        for signal in ("practical implication", "ranked priorities", "confirm", "next", "priority", "priorities", "attention", "follow-up", "follow up", "decision", "remaining")
    ):
        return []
    executive = " ".join(_summary_strings(executive_readout))
    executive_normalized = _summary_normalize(executive).casefold()
    if executive_normalized:
        for paragraph in paragraphs:
            normalized = paragraph.casefold()
            if normalized in executive_normalized or executive_normalized in normalized:
                return []
    for paragraph in paragraphs:
        if not validate_summary_fragment(
            paragraph,
            canonical_text=canonical_text,
        ):
            return []
    return paragraphs


def validate_summary_fragment(
    text: object,
    *,
    canonical_text: object = (),
) -> bool:
    """Validate grounding controls for one plain-text summary fragment."""
    if not isinstance(text, str) or not text.strip():
        return False
    if _SUMMARY_MARKUP_RE.search(text):
        return False
    fragment = _summary_normalize(text)
    if not _summary_sentences(fragment):
        return False
    canonical = " ".join(_summary_strings(canonical_text))
    canonical_casefold = canonical.casefold()
    canonical_words = _summary_words(canonical)
    canonical_numbers = set(
        re.findall(r"\b\d+(?:[.,]\d+)?%?\b", canonical)
    )
    for number in re.findall(r"\b\d+(?:[.,]\d+)?%?\b", fragment):
        if number not in canonical_numbers:
            return False
    for month in _SUMMARY_MONTHS:
        date_pattern = (
            rf"\b{month}\s+\d{{4}}\b|"
            rf"\b\d{{1,2}}\s+{month}\b"
        )
        for date in re.findall(date_pattern, fragment.casefold()):
            if date not in canonical_casefold:
                return False
    if canonical_casefold:
        for match in _SUMMARY_ENTITY_RE.finditer(fragment):
            entity = match.group(0).casefold()
            if entity.startswith("the "):
                entity = entity[4:]
            if entity not in canonical_casefold and entity not in _SUMMARY_GENERIC_ENTITIES:
                return False
        for match in _SUMMARY_CAPITALIZED_RE.finditer(fragment):
            token = match.group(0).casefold()
            if token in _SUMMARY_ALLOWED_SINGLE_WORDS | _SUMMARY_CONNECTIVE_TOKENS:
                continue
            if token not in canonical_words:
                return False
        for match in _SUMMARY_ACRONYM_RE.finditer(fragment):
            token = match.group(0).casefold()
            if token in _SUMMARY_ALLOWED_SINGLE_WORDS:
                continue
            if token not in canonical_words:
                return False
    for match in _SUMMARY_ACTION_STEM_RE.finditer(fragment.casefold()):
        if match.group("stem") not in canonical_casefold:
            return False
    if canonical_words:
        for sentence in _summary_sentences(fragment):
            words = _summary_words(sentence)
            unsupported_words = (
                words
                - canonical_words
                - _SUMMARY_ALLOWED_TOKENS
                - _SUMMARY_CONNECTIVE_TOKENS
            )
            if any(
                not _summary_morphology_supported(word, canonical_words)
                for word in unsupported_words
            ):
                return False
    return True


def _object(properties: dict[str, object]) -> dict[str, object]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def _string(description: str = "") -> dict[str, object]:
    schema: dict[str, object] = {"type": "string"}
    if description:
        schema["description"] = description
    return schema


def _nullable_string(description: str = "") -> dict[str, object]:
    schema: dict[str, object] = {"type": ["string", "null"]}
    if description:
        schema["description"] = description
    return schema


def _enum(values: tuple[str, ...]) -> dict[str, object]:
    return {"type": "string", "enum": list(values)}


def _strings(description: str = "") -> dict[str, object]:
    schema: dict[str, object] = {
        "type": "array",
        "items": {"type": "string"},
    }
    if description:
        schema["description"] = description
    return schema


CONFIDENCE = ("high", "medium", "low")
SEMANTIC_REVIEW_REASON_CODES = (
    "PROJECT_FACT_UNSUPPORTED",
    "EXISTING_MITIGATION_MISREPRESENTED",
    "RESIDUAL_GAP_UNSUPPORTED",
    "RECOMMENDATION_DISPROPORTIONATE",
    "ROUTING_SCOPE_UNVERIFIED",
    "TIMING_UNSUPPORTED",
    "AUTHORITY_UNSUPPORTED",
    "DRAFTING_TARGET_UNVERIFIED",
    "DRAFTING_SCOPE_UNSUPPORTED",
    "DRAFTING_DUPLICATIVE",
    "DRAFTING_TECHNICAL_PRECISION_UNSUPPORTED",
    "UNINTENDED_CONSEQUENCE_UNADDRESSED",
    "RATING_INCOHERENT",
    "RECOMMENDATION_DUPLICATIVE",
)


FACT_SCHEMA = _object(
    {
        "claim_id": _string(),
        "claim_type": _string("Short atomic fact type."),
        "subject": _string("45 words or fewer."),
        "predicate": _string("45 words or fewer."),
        "object": _string("45 words or fewer."),
        "epistemic_status": _enum(
            (
                "explicit",
                "confirmed_absence",
                "not_found",
                "not_yet_specified",
                "contradictory",
                "not_applicable",
            )
        ),
        "source_block_ids": _strings(),
        "supporting_excerpt": _nullable_string(
            "A short verbatim excerpt of 60 words or fewer, or null."
        ),
        "confidence": _enum(CONFIDENCE),
    }
)

ASSERTION_SCHEMA = _object(
    {
        "assertion_id": _string(),
        "assertion_type": _string(),
        "statement": _string("45 words or fewer."),
        "input_fact_ids": _strings(),
        "derivation_method": _enum(("deterministic", "semantic")),
        "explanation": _string("45 words or fewer."),
        "confidence": _enum(CONFIDENCE),
        "validation_status": _string(),
    }
)

RESPONSE_SCHEMA = _object(
    {
        "response_id": _string(),
        "project_fact_ids": _strings(),
        "pathway_ids": _strings(),
        "description": _string("45 words or fewer."),
        "limitation": _string("45 words or fewer."),
    }
)

PATHWAY_SCHEMA = _object(
    {
        "pathway_id": _string(),
        "direction": _enum(("climate_to_fcv", "fcv_to_climate")),
        "chain": _strings("Exactly three short elements."),
        "project_anchor_ids": _strings(),
        "evidence_ids": _strings(),
        "confidence": _enum(CONFIDENCE),
    }
)

GAP_SCHEMA = _object(
    {
        "gap_id": _string(),
        "gap_type": _enum(
            (
                "confirmed_omission",
                "partial_response",
                "not_yet_specified",
                "contradictory",
                "evidence_gap",
            )
        ),
        "statement": _string("45 words or fewer."),
        "pathway_ids": _strings(),
        "project_anchor_ids": _strings(),
        "existing_response_ids": _strings(),
        "evidence_ids": _strings(),
        "confidence": _enum(CONFIDENCE),
    }
)


def _judgment(values: tuple[str, ...]) -> dict[str, object]:
    return _object(
        {
            "value": _enum(values),
            "evidence_ids": _strings(),
            "rationale": _string("75 words or fewer."),
        }
    )


CORE_QUESTION_SCHEMA = _object(
    {
        "question_id": _string("Bank question id, for example cq2-infra-horizon."),
        "theme": _string("One of the six core climate-FCV themes."),
        "question": _string("The plain-language question, restated for the reader."),
        "source": _string("Short source-framework attribution."),
        "summary": _string(
            "Evidence-grounded answer of roughly 120 to 220 words in one or two "
            "short paragraphs separated by a blank line, distinct from the "
            "executive readout; a design question to resolve, never a promise."
        ),
        "evidence_ids": _strings(),
        "watch": _string("One short line naming what to check. 30 words or fewer."),
    }
)


SCORE_SCHEMA = _object(
    {
        "materiality": {"type": "integer"},
        "gap_strength": {"type": "integer"},
        "leverage_urgency": {"type": "integer"},
        "evidence": {"type": "integer"},
        "feasibility": {"type": "integer"},
    }
)

GATE_SCHEMA = _object(
    {
        "connection": {"type": "boolean"},
        "residuality": {"type": "boolean"},
        "materiality": {"type": "boolean"},
        "actionability": {"type": "boolean"},
        "timing": {"type": "boolean"},
        "distinctiveness": {"type": "boolean"},
    }
)

DRAFTING_SCHEMA = _object(
    {
        "target_document": _string("Document or verified instrument name."),
        "target_section": _string("Specific section or provision."),
        "drafting_status": _enum(
            ("existing_commitment", "advisory_proposal")
        ),
        "text": _string("Ready-to-adapt drafting of 90 to 160 words."),
        "project_basis_ids": _strings(),
        "gap_basis_ids": _strings(),
        "guidance_ids": _strings(),
    }
)

DRAFTING_BLOCK_SCHEMA = _object(
    {
        "drafting_role": _enum(
            ("current_document", "operational_instrument")
        ),
        **DRAFTING_SCHEMA["properties"],
    }
)

CANDIDATE_SCHEMA = _object(
    {
        "recommendation_id": _string(),
        "title": _string("45 words or fewer."),
        "pathway_ids": _strings(),
        "existing_response_ids": _strings(),
        "residual_gap_ids": _strings(),
        "project_anchor_ids": _strings(),
        "decision": _string("45 words or fewer."),
        "minimum_action": _string("45 words or fewer."),
        "enhanced_action": _nullable_string("45 words or fewer, or null."),
        "enhanced_activation": _nullable_string("45 words or fewer, or null."),
        "routing_status": _enum(
            (
                "verified_existing",
                "verified_with_scope_change",
                "standard_document_advisory",
                "not_applicable",
            )
        ),
        "instrument_claim_ids": _strings(),
        "responsible_function": _string("45 words or fewer."),
        "authority_basis": _enum(
            ("project_commitment", "policy", "directive", "procedure", "none_verified")
        ),
        "recommendation_basis": _enum(
            ("project_evidence", "country_context", "guidance", "analytical_judgment")
        ),
        "completion_evidence": _string("45 words or fewer."),
        "completion_evidence_status": _enum(
            ("output", "decision_record", "updated_section", "team_to_define")
        ),
        "confidence": _enum(CONFIDENCE),
        "limitation": _string("45 words or fewer."),
        "caution": _string("45 words or fewer."),
        "narrative": _string(
            "Two or three short plain-prose paragraphs telling the story; "
            "no new claims or digits."
        ),
        "supported_numeric_tokens": _strings(),
        "score": SCORE_SCHEMA,
        "gate_results": GATE_SCHEMA,
    }
)


DRAFTING_SET_SCHEMA = _object(
    {
        "recommendation_id": _string(),
        "drafting_blocks": {
            "type": "array",
            "items": DRAFTING_BLOCK_SCHEMA,
        },
    }
)

READINESS_SCHEMA = _object(
    {
        "flag_id": _string(),
        "category": _enum(
            (
                "incomplete_climate_screening",
                "document_inconsistency",
                "unresolved_indicator",
                "processing_route_question",
                "missing_operational_home",
                "material_placeholder",
            )
        ),
        "flag": _string("45 words or fewer."),
        "why_it_matters": _string("45 words or fewer."),
        "document_basis_ids": _strings(),
        "suggested_verification": _string("45 words or fewer."),
        "residual_gap_ids": _strings(),
    }
)


MINOR_CLIMATE_POINT_SCHEMA = _object(
    {
        "point": _string("20 words or fewer."),
        "why": _string("45 words or fewer."),
        "how_to_check": _string("45 words or fewer."),
        "residual_gap_ids": _strings(),
    }
)


STAGE_OUTPUT_SCHEMAS: dict[str, dict[str, object]] = {
    "fact_extraction": _object(
        {
            "schema_version": _enum(("climate-verified-v2.1",)),
            "facts": {
                "type": "array",
                "items": FACT_SCHEMA,
                "description": "No more than 100 atomic project facts.",
            },
            "derived_assertions": {
                "type": "array",
                "items": ASSERTION_SCHEMA,
                "description": "Only essential derived assertions.",
            },
            "document_integrity_findings": {
                "type": "array",
                "items": READINESS_SCHEMA,
                "description": (
                    "Verifiable defects in the uploaded document itself; "
                    "empty array when none are present."
                ),
            },
        }
    ),
    "bounded_analysis": _object(
        {
            "existing_responses": {
                "type": "array",
                "items": RESPONSE_SCHEMA,
                "description": "No more than 12 material existing responses.",
            },
            "pathways": {
                "type": "array",
                "items": PATHWAY_SCHEMA,
                "description": "No more than three pathways in each direction.",
            },
            "residual_gaps": {
                "type": "array",
                "items": GAP_SCHEMA,
                "description": "No more than eight residual gaps.",
            },
            "opportunities_and_unintended_consequences": _strings(
                "No more than four concise items, each 45 words or fewer."
            ),
            "evidence_limitations": _strings(
                "No more than four concise items, each 45 words or fewer."
            ),
        }
    ),
    "judgment_review": _object(
        {
            "executive_readout": _string("Between 500 and 800 words."),
            "overview_summary": _string(
                "A three-to-four sentence plain-language overall summary for the "
                "top-of-report overview, distinct from and shorter than the "
                "executive_readout."
            ),
            "summary_overview": {
                "type": "object",
                "properties": {
                    "paragraphs": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                        "minItems": 1,
                        # The application validator enforces the upper bound.
                        "description": (
                            "Exactly two or three non-empty plain-text paragraphs, "
                            "totalling 160 to 230 words."
                        ),
                    }
                },
                "required": ["paragraphs"],
                "additionalProperties": False,
            },
            "relevance": _judgment(("high", "medium", "low", "unclear")),
            "sensitivity": _judgment(
                ("very_strong", "strong", "moderate", "limited",
                 "very_limited", "unclear")
            ),
            "responsiveness": _judgment(
                ("strong", "emerging", "limited", "not_expected", "unclear")
            ),
            "operationalization": _judgment(
                ("embedded", "partial", "early", "not_evidenced", "unclear")
            ),
            "core_questions": {
                "type": "array",
                "items": CORE_QUESTION_SCHEMA,
                "description": (
                    "Three to seven evidence-grounded answers to the supplied "
                    "triggered core climate-FCV questions, each distinct from the "
                    "executive readout. Empty array if none can be evidenced."
                ),
            },
            "minor_climate_points": {
                "type": "array",
                "items": MINOR_CLIMATE_POINT_SCHEMA,
                "description": (
                    "Up to three smaller climate/FCV points tied to a residual "
                    "gap that may not warrant a full recommendation. Empty if none."
                ),
            },
        }
    ),
    "recommendation_compiler": _object(
        {
            "recommendation_candidates": {
                "type": "array",
                "items": CANDIDATE_SCHEMA,
                "description": "No more than five admitted candidates.",
            },
            "readiness_flags": {
                "type": "array",
                "items": READINESS_SCHEMA,
                "description": "No more than four source-linked readiness flags.",
            },
        }
    ),
    "drafting_compiler": _object(
        {
            "drafting_sets": {
                "type": "array",
                "items": DRAFTING_SET_SCHEMA,
                "description": "One set for each supplied recommendation.",
            },
        }
    ),
    "conditional_review": _object(
        {
            "verdict": _enum(("pass", "revise", "block")),
            "reason_codes": {
                "type": "array",
                "items": _enum(SEMANTIC_REVIEW_REASON_CODES),
                "description": (
                    "No more than 12 recommendation-defect reason codes."
                ),
            },
            "object_ids": _strings("No more than 12 affected object IDs."),
        }
    ),
}


def stage_output_schema(stage: str) -> dict[str, object]:
    """Return an isolated native output schema for one verified stage."""

    try:
        schema = STAGE_OUTPUT_SCHEMAS[stage]
    except KeyError as error:
        raise ValueError(f"Unsupported verified Climate stage: {stage}") from error
    return deepcopy(schema)
