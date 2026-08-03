"""Bounded, non-authoritative drafting guidance for Climate-FCV outputs.

The registry contains concise workflow propositions already represented in
repository guidance. It is not a policy corpus and does not establish project
facts, formal requirements, or instrument existence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


GUIDANCE_REGISTRY_VERSION = "climate-guidance-v1"
MAX_GUIDANCE_PACKET_SIZE = 6


@dataclass(frozen=True)
class GuidanceEntry:
    guidance_id: str
    title: str
    document_types: tuple[str, ...]
    instrument_types: tuple[str, ...]
    permitted_targets: tuple[tuple[str, str], ...]
    application_rule: str
    authority_class: str
    prohibited_overstatements: tuple[str, ...]

    def as_record(self) -> dict[str, object]:
        return asdict(self)


_PCN_PAD = ("pcn", "pad")
_IPF = ("ipf",)


OPERATIONAL_GUIDANCE = (
    GuidanceEntry(
        guidance_id="GUIDE-PCN-DESIGN",
        title="Stage-appropriate project design",
        document_types=_PCN_PAD,
        instrument_types=_IPF,
        permitted_targets=(
            ("pcn", "project description"),
            ("pcn", "implementation arrangements"),
            ("pad", "project description"),
            ("pad", "implementation arrangements"),
        ),
        application_rule=(
            "Place a material design improvement in the current concept or "
            "appraisal document and describe it as an advisory proposal when "
            "the uploaded project evidence does not show an existing commitment."
        ),
        authority_class="operational_guidance",
        prohibited_overstatements=(
            "Do not present proposed text as an agreed project commitment.",
            "Do not invent a separate implementation vehicle.",
        ),
    ),
    GuidanceEntry(
        guidance_id="GUIDE-RESULTS-MEASUREMENT",
        title="Results and measurement",
        document_types=_PCN_PAD,
        instrument_types=_IPF,
        permitted_targets=(
            ("pcn", "results framework"),
            ("pad", "results framework"),
            ("pad", "monitoring and evaluation"),
        ),
        application_rule=(
            "Use the Results Framework or monitoring section for a measurable "
            "result, indicator, disaggregation, or verification improvement "
            "that follows from the supported project gap."
        ),
        authority_class="operational_guidance",
        prohibited_overstatements=(
            "Do not invent baselines, targets, dates, or data systems.",
        ),
    ),
    GuidanceEntry(
        guidance_id="GUIDE-RISK-TREATMENT",
        title="Concept-stage risk treatment",
        document_types=_PCN_PAD,
        instrument_types=_IPF,
        permitted_targets=(
            ("pcn", "concept note risk section"),
            ("pad", "risk section"),
        ),
        application_rule=(
            "Place a supported risk-treatment improvement in the stage-appropriate "
            "risk section without prescribing a rating or formal condition."
        ),
        authority_class="reviewer_judgment",
        prohibited_overstatements=(
            "Do not prescribe a SORT rating.",
            "Do not convert analytical advice into a formal condition.",
        ),
    ),
    GuidanceEntry(
        guidance_id="GUIDE-ADAPTIVE-MANAGEMENT",
        title="Adaptive management and decision triggers",
        document_types=_PCN_PAD,
        instrument_types=_IPF,
        permitted_targets=(
            ("pcn", "implementation arrangements"),
            ("pad", "implementation arrangements"),
            ("pad", "monitoring and evaluation"),
        ),
        application_rule=(
            "Describe a proportionate review point or decision trigger when the "
            "evidence supports adaptation but not a fixed threshold or date."
        ),
        authority_class="reviewer_judgment",
        prohibited_overstatements=(
            "Do not invent numeric thresholds, deadlines, or approval gates.",
        ),
    ),
    GuidanceEntry(
        guidance_id="GUIDE-ES-INSTRUMENT-ROUTING",
        title="Environmental and social instrument routing",
        document_types=_PCN_PAD,
        instrument_types=_IPF,
        permitted_targets=(
            ("pcn", "environmental and social overview"),
            ("pad", "environmental and social section"),
        ),
        application_rule=(
            "Route detailed drafting to an environmental or social instrument "
            "only when the uploaded project evidence names that instrument and "
            "supports its relevant scope."
        ),
        authority_class="operational_guidance",
        prohibited_overstatements=(
            "Do not infer that a named instrument covers an unstated topic.",
        ),
    ),
    GuidanceEntry(
        guidance_id="GUIDE-FCV-CONTINUITY",
        title="FCV operational continuity and access",
        document_types=_PCN_PAD,
        instrument_types=_IPF,
        permitted_targets=(
            ("pcn", "implementation arrangements"),
            ("pad", "implementation arrangements"),
            ("pad", "risk section"),
        ),
        application_rule=(
            "Describe proportionate continuity, access, inclusion, or delivery "
            "adaptation where the supported Climate-FCV pathway affects project "
            "implementation."
        ),
        authority_class="reviewer_judgment",
        prohibited_overstatements=(
            "Do not invent actors, plans, systems, or security arrangements.",
        ),
    ),
)


def select_operational_guidance(
    *,
    doc_type: str,
    instrument_type: str,
) -> tuple[GuidanceEntry, ...]:
    """Return a deterministic, bounded packet for the project stage."""

    document = str(doc_type or "").strip().casefold()
    instrument = str(instrument_type or "").strip().casefold()
    selected = tuple(
        entry
        for entry in OPERATIONAL_GUIDANCE
        if document in entry.document_types
        and (
            instrument in entry.instrument_types
            or instrument in {"", "unknown"}
        )
    )
    return selected[:MAX_GUIDANCE_PACKET_SIZE]
