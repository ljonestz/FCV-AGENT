"""Runtime bridge from uploaded document parts to ``climate-verified-v2.1``.

Only project and package-instrument uploads can establish project facts.
Context uploads and the country bank cross the boundary as contextual evidence.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from dataclasses import dataclass

import regime_router

from sector_lenses.climate_analysis import ContextEvidenceRef
from sector_lenses.climate_context_adapter import adapt_grounding_evidence
from sector_lenses.climate_source_blocks import (
    DocumentApplicability,
    SourceBlock,
    SourceDocument,
    normalize_block_text,
)
from sector_lenses.climate_verified_pipeline import (
    PipelineClients,
    run_verified_climate_pipeline,
)
from sector_lenses.climate_verified_render import (
    attach_provenance,
    build_reader_model,
    validate_reader_model,
)
from sector_lenses.pipeline import normalize_climate_assessment


DEFAULT_MAXIMUM_SOURCE_CHARS = 85_000
DEFAULT_MAXIMUM_CONTEXT_CHARS = 15_000
_BLOCK_CHARS = 1_800
_ALLOWED_LABELS = {"PROJECT DOCUMENT", "PACKAGE INSTRUMENT"}
_OPERATIONAL_TERMS = (
    "project operations manual",
    "operations manual",
    "escp",
    "esmf",
    "esrs",
    "results framework",
    "security risk management plan",
    "feasibility study",
    "procurement",
    "co-management",
    "indicator",
    "adaptive trigger",
    "site selection",
    "climate",
    "conflict",
    "fragility",
    "flood",
    "drought",
    "displacement",
    "cerc",
)


@dataclass(frozen=True)
class PreparedClimateSources:
    documents: tuple[SourceDocument, ...]
    blocks: tuple[SourceBlock, ...]
    warning_codes: tuple[str, ...]


@dataclass(frozen=True)
class VerifiedOperationContext:
    document_type: str = "Unknown"
    instrument_type: str = "Unknown"
    country_scope: str = "single"
    is_mpa: bool = False
    has_ipf_component: bool = False
    preparation_regime: str = "unresolved_policy_source"
    processing_model: str = "unknown"
    es_regime: str = "UNRESOLVED"
    warning_codes: tuple[str, ...] = ()
    evidence_notes: tuple[str, ...] = ()

    def as_record(self) -> dict[str, object]:
        return {
            "document_type": self.document_type,
            "instrument_type": self.instrument_type,
            "country_scope": self.country_scope,
            "is_mpa": self.is_mpa,
            "has_ipf_component": self.has_ipf_component,
            "preparation_regime": self.preparation_regime,
            "processing_model": self.processing_model,
            "es_regime": self.es_regime,
            "warning_codes": list(self.warning_codes),
            "evidence_notes": list(self.evidence_notes),
        }


def _primary_context_text(
    prepared: PreparedClimateSources,
) -> tuple[str, str]:
    primary_ids = {
        item.document_id
        for item in prepared.documents
        if item.relationship == "primary"
    }
    filenames = " ".join(
        item.filename
        for item in prepared.documents
        if item.document_id in primary_ids
    ).casefold()
    source_text = " ".join(
        item.text
        for item in prepared.blocks
        if item.document_id in primary_ids
    ).casefold()
    return filenames, source_text


def _context_matches(pattern: str, filenames: str, source_head: str) -> bool:
    return bool(re.search(pattern, filenames) or re.search(pattern, source_head))


def _extract_ois_creation_date(source_head: str):
    match = re.search(
        r"\bois\b.{0,80}?\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2})\b",
        source_head,
    )
    if not match:
        return None
    value = match.group(1).replace("/", "-")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def resolve_verified_operation_context(
    prepared: PreparedClimateSources,
    *,
    doc_type: str = "Unknown",
    instrument_type: str = "Unknown",
) -> VerifiedOperationContext:
    """Resolve conservative routing from explicit primary-document markers."""

    filenames, source_text = _primary_context_text(prepared)
    source_head = source_text[:8_000]
    warnings: list[str] = []
    notes: list[str] = []
    document = str(doc_type or "Unknown").strip() or "Unknown"
    instrument = str(instrument_type or "Unknown").strip() or "Unknown"

    document_markers = (
        (r"\bprogram document\b", "Program Document"),
        (r"\bprogram paper\b", "Program Paper"),
        (r"\bproject paper\b", "Project Paper"),
        (
            r"\bproject appraisal document\b|(?:^|[\W_])pad(?:[\W_]|$)",
            "PAD",
        ),
        (r"\bproject concept note\b|(?:^|[\W_])pcn(?:[\W_]|$)", "PCN"),
        (
            r"\bproject information document\b|(?:^|[\W_])pid(?:[\W_]|$)",
            "PID",
        ),
    )
    filename_document_matches = [
        value for pattern, value in document_markers
        if re.search(pattern, filenames)
    ]
    source_document_matches = [
        value for pattern, value in document_markers
        if re.search(pattern, source_head)
    ]
    detected_document = "Unknown"
    if len(dict.fromkeys(filename_document_matches)) == 1:
        detected_document = filename_document_matches[0]
    elif not filename_document_matches and len(
        dict.fromkeys(source_document_matches)
    ) == 1:
        detected_document = source_document_matches[0]
    elif filename_document_matches or source_document_matches:
        document = "Unknown"
        warnings.append("DOCUMENT_ROUTE_AMBIGUOUS")
    if detected_document != "Unknown":
        if (
            document.casefold() != "unknown"
            and document.casefold() != detected_document.casefold()
        ):
            warnings.append("DOCUMENT_HINT_OVERRIDDEN")
        document = detected_document
        notes.append(f"document_marker:{document}")

    pforr = _context_matches(
        r"\bprogram(?:-| )for(?:-| )results(?: financing)?\b|\bpforr\b|\bp4r\b",
        filenames,
        source_head,
    )
    dpf = _context_matches(
        r"\bdevelopment policy (?:financing|operation)\b|\bdpf\b|\bdpo\b",
        filenames,
        source_head,
    )
    ipf = _context_matches(
        r"\binvestment project financing\b|\bipf\b",
        filenames,
        source_head,
    )
    hybrid_ipf = bool(
        pforr
        and re.search(
            r"\b(?:includes?|with|hybrid)\b.{0,80}\bipf component\b|"
            r"\bipf component\b",
            source_head,
        )
    )
    detected_instrument = "Unknown"
    if pforr and not dpf and (not ipf or hybrid_ipf):
        detected_instrument = "PforR"
    elif dpf and not pforr and not ipf:
        detected_instrument = "DPF"
    elif ipf and not pforr and not dpf:
        detected_instrument = "IPF"
    if detected_instrument != "Unknown":
        if (
            instrument.casefold() != "unknown"
            and instrument.casefold() != detected_instrument.casefold()
        ):
            warnings.append("INSTRUMENT_HINT_OVERRIDDEN")
        instrument = detected_instrument
        notes.append(f"instrument_marker:{instrument}")
    elif sum((pforr, dpf, ipf)) > 1:
        instrument = "Unknown"
        warnings.append("INSTRUMENT_ROUTE_AMBIGUOUS")

    is_mpa = _context_matches(
        r"\bmultiphase programmatic approach\b|\bmpa\b",
        filenames,
        source_head,
    )
    country_scope = (
        "multi"
        if _context_matches(
            r"\bmulti(?:-| )country\b|\bregional (?:project|program|programme|operation)\b|"
            r"\bparticipating countries\b",
            filenames,
            source_head,
        )
        else "single"
    )
    if country_scope == "multi":
        warnings.append("MULTI_COUNTRY_BANK_WITHHELD")

    normalized_document = document.casefold()
    marker_preparation_regime = (
        "new_model"
        if normalized_document in {"project paper", "program paper", "program document"}
        else "legacy_transitional"
        if normalized_document in {"pcn", "pid", "pad"}
        else "unresolved_policy_source"
    )
    preparation_regime = marker_preparation_regime
    ois_creation_date = _extract_ois_creation_date(source_head)
    if ois_creation_date is not None:
        preparation_regime = regime_router.classify_preparation_regime(
            ois_creation_date,
            instrument,
        )
        notes.append(f"ois_creation_date:{ois_creation_date.isoformat()}")
        if (
            marker_preparation_regime != "unresolved_policy_source"
            and marker_preparation_regime != preparation_regime
        ):
            warnings.append("PREPARATION_MARKER_DATE_CONFLICT")
    processing_model = "unknown"
    if re.search(r"\btechnical design\b", source_head) and re.search(
        r"\bimplementation readiness\b", source_head
    ):
        processing_model = "two_step"
    elif re.search(r"\bone review\b", source_head):
        processing_model = "one_review"

    normalized_instrument = instrument.casefold()
    if normalized_instrument in {"pforr", "p4r", "dpf", "dpo"}:
        es_regime = "INSTRUMENT_SPECIFIC"
    elif normalized_instrument == "ipf":
        if re.search(
            r"\b(?:esf|esrs|escp|environmental and social framework)\b",
            source_head,
        ):
            es_regime = "ESF_ESS1_TO_ESS10"
        elif re.search(
            r"\b(?:safeguard policies|op 4\.01|bp 4\.01)\b",
            source_head,
        ):
            es_regime = "LEGACY_SAFEGUARDS"
        else:
            es_regime = "UNRESOLVED"
    else:
        es_regime = "UNRESOLVED"

    if normalized_document == "unknown":
        warnings.append("DOCUMENT_ROUTE_UNRESOLVED")
    if normalized_instrument == "unknown":
        warnings.append("INSTRUMENT_ROUTE_UNRESOLVED")
    if is_mpa and normalized_instrument == "unknown":
        warnings.append("MPA_BASE_INSTRUMENT_UNRESOLVED")

    return VerifiedOperationContext(
        document_type=document,
        instrument_type="DPF" if normalized_instrument == "dpo" else instrument,
        country_scope=country_scope,
        is_mpa=is_mpa,
        has_ipf_component=hybrid_ipf,
        preparation_regime=preparation_regime,
        processing_model=processing_model,
        es_regime=es_regime,
        warning_codes=tuple(dict.fromkeys(warnings)),
        evidence_notes=tuple(dict.fromkeys(notes)),
    )


def resolve_verified_document_context(
    prepared: PreparedClimateSources,
    *,
    doc_type: str,
    instrument_type: str,
) -> tuple[str, str]:
    """Resolve missing routing context from explicit primary-source markers."""

    context = resolve_verified_operation_context(
        prepared,
        doc_type=doc_type,
        instrument_type=instrument_type,
    )
    return context.document_type, context.instrument_type


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _chunks(text: str, size: int) -> list[str]:
    """Keep logical paragraphs intact while bounding over-large blocks."""

    result: list[str] = []
    paragraphs = re.split(r"\n\s*\n", text)
    for raw in paragraphs:
        value = normalize_block_text(raw)
        while value:
            if len(value) <= size:
                result.append(value)
                break
            window = value[: size + 1]
            sentence_cuts = [
                match.end()
                for match in re.finditer(r"[.!?](?=\s)", window)
            ]
            cut = sentence_cuts[-1] if sentence_cuts else 0
            if cut < max(80, size // 3):
                cut = value.rfind(" ", 0, size + 1)
            if cut < max(80, size // 3):
                cut = size
            result.append(value[:cut].strip())
            value = value[cut:].strip()
    return [item for item in result if item]


def _priority(block: SourceBlock) -> tuple[int, int]:
    lowered = block.text.casefold()
    score = sum(1 for term in _OPERATIONAL_TERMS if term in lowered)
    index = block.paragraph_index if block.paragraph_index is not None else 10**9
    return (-score, index)


def _bounded_blocks(
    blocks: list[SourceBlock],
    maximum_chars: int,
) -> tuple[tuple[SourceBlock, ...], bool]:
    if sum(len(item.text) for item in blocks) <= maximum_chars:
        return tuple(blocks), False

    selected: list[SourceBlock] = []
    remaining = maximum_chars
    for block in sorted(blocks, key=_priority):
        length = len(block.text)
        if length <= remaining:
            selected.append(block)
            remaining -= length
    selected_ids = {item.block_id for item in selected}
    ordered = tuple(item for item in blocks if item.block_id in selected_ids)
    return ordered, True


def prepare_verified_sources(
    doc_parts: object,
    *,
    maximum_chars: int = DEFAULT_MAXIMUM_SOURCE_CHARS,
) -> PreparedClimateSources:
    """Create stable, bounded project-fact sources from extracted uploads."""

    if maximum_chars < 1:
        raise ValueError("maximum_chars must be positive")
    documents: list[SourceDocument] = []
    blocks: list[SourceBlock] = []
    parts = doc_parts if isinstance(doc_parts, list) else []
    block_size = min(_BLOCK_CHARS, maximum_chars)
    primary_count = sum(
        1
        for item in parts
        if isinstance(item, dict)
        and str(item.get("label") or "").strip().upper() == "PROJECT DOCUMENT"
        and str(item.get("raw_text") or "").strip()
    )
    warnings: list[str] = []
    if primary_count > 1:
        warnings.append("PRIMARY_DOCUMENT_PRECEDENCE_UNRESOLVED")
    elif primary_count == 1:
        warnings.append("PRIMARY_APPLICABILITY_USER_DESIGNATED")

    for position, part in enumerate(parts):
        if not isinstance(part, dict):
            continue
        label = str(part.get("label") or "").strip().upper()
        if label not in _ALLOWED_LABELS:
            continue
        raw_text = str(part.get("raw_text") or "")
        if not raw_text.strip():
            continue
        filename = str(part.get("name") or f"upload-{position + 1}").strip()
        digest = _sha256(raw_text)
        identity = _sha256(f"{position}|{label}|{filename}|{digest}")[:16]
        document_id = f"DOC-{identity}"
        is_primary = label == "PROJECT DOCUMENT"
        controls_facts = is_primary and primary_count == 1
        document = SourceDocument(
            document_id=document_id,
            filename=filename,
            sha256=digest,
            applicability=(
                DocumentApplicability.PARTIAL
                if controls_facts
                else DocumentApplicability.UNRESOLVED
            ),
            relationship="primary" if is_primary else "package",
            version_status=(
                "user_designated" if controls_facts else "unresolved"
            ),
            operation_match=(
                "user_designated" if controls_facts else "unresolved"
            ),
            document_type=(
                "project_document_upload" if controls_facts else "unresolved"
            ),
        )
        documents.append(document)
        if not controls_facts:
            if not is_primary:
                warnings.append("PACKAGE_FACT_AUTHORITY_WITHHELD")
            continue
        for paragraph_index, text in enumerate(_chunks(raw_text, block_size)):
            normalized_hash = _sha256(
                f"{document_id}|p:{paragraph_index}|{text}"
            )
            blocks.append(SourceBlock(
                block_id=f"{document_id}-B-{normalized_hash[:12]}",
                document_id=document_id,
                text=text,
                normalized_hash=normalized_hash,
                heading_path=(),
                paragraph_index=paragraph_index,
            ))

    bounded, was_bounded = _bounded_blocks(blocks, maximum_chars)
    if was_bounded:
        warnings.append("SOURCE_BLOCKS_BOUNDED")
    return PreparedClimateSources(
        documents=tuple(documents),
        blocks=bounded,
        warning_codes=tuple(dict.fromkeys(warnings)),
    )


def _uploaded_context_evidence(
    doc_parts: object,
    *,
    maximum_chars: int = DEFAULT_MAXIMUM_CONTEXT_CHARS,
) -> tuple[ContextEvidenceRef, ...]:
    """Keep uploaded context useful without granting project-fact authority."""

    candidates: list[tuple[int, int, ContextEvidenceRef]] = []
    parts = doc_parts if isinstance(doc_parts, list) else []
    for position, part in enumerate(parts):
        if not isinstance(part, dict):
            continue
        if str(part.get("label") or "").strip().upper() != "CONTEXT DOCUMENT":
            continue
        raw_text = str(part.get("raw_text") or "")
        if not raw_text.strip():
            continue
        filename = str(part.get("name") or f"context-{position + 1}").strip()
        document_id = _sha256(f"{position}|{filename}|{_sha256(raw_text)}")[:16]
        for block_index, text in enumerate(_chunks(raw_text, _BLOCK_CHARS)):
            lowered = text.casefold()
            score = sum(1 for term in _OPERATIONAL_TERMS if term in lowered)
            block_id = _sha256(
                f"{document_id}|context:{block_index}|{text}"
            )[:16]
            candidates.append((
                -score,
                block_index,
                ContextEvidenceRef(
                    evidence_id=f"CE-UPLOAD-{block_id}",
                    evidence_class="country",
                    scope="unresolved",
                    statement=text,
                    source_ref=(
                        f"upload-context:{document_id}:{block_index}:{filename}"
                    ),
                    confidence="low",
                    source_kind="uploaded_context",
                    context_class="uploaded_context",
                ),
            ))

    selected: list[ContextEvidenceRef] = []
    remaining = maximum_chars
    for _, _, evidence in sorted(candidates, key=lambda item: (item[0], item[1])):
        if len(evidence.statement) <= remaining:
            selected.append(evidence)
            remaining -= len(evidence.statement)
    return tuple(selected)


def run_verified_from_doc_parts(
    *,
    doc_parts: object,
    climate_grounding: object,
    clients: PipelineClients,
    run_id: str,
    cancel_event: object | None = None,
    doc_type: str = "Unknown",
    instrument_type: str = "Unknown",
    operation_context: VerifiedOperationContext | None = None,
    wall_clock_seconds: int = 14 * 60,
) -> dict[str, object]:
    """Run verified-v2 from the final extraction and grounding contracts."""

    prepared = prepare_verified_sources(doc_parts)
    operation_context = operation_context or resolve_verified_operation_context(
        prepared,
        doc_type=doc_type,
        instrument_type=instrument_type,
    )
    doc_type = operation_context.document_type
    instrument_type = operation_context.instrument_type
    operation_record = operation_context.as_record()
    context = list(adapt_grounding_evidence(climate_grounding))
    context.extend(_uploaded_context_evidence(doc_parts))
    grounding = climate_grounding if isinstance(climate_grounding, dict) else {}
    assessment = run_verified_climate_pipeline(
        source_documents=list(prepared.documents),
        source_blocks=list(prepared.blocks),
        context_evidence=context,
        clients=clients,
        bank_release_id=str(grounding.get("content_version") or "") or None,
        run_id=run_id,
        cancel_event=cancel_event,
        wall_clock_seconds=wall_clock_seconds,
        doc_type=doc_type,
        instrument_type=instrument_type,
        operation_context=operation_record,
    )
    assessment.setdefault("operation_context", operation_record)
    normalized = normalize_climate_assessment(assessment)
    reader = build_reader_model(normalized)
    reader_issues = validate_reader_model(reader)
    # Project the evidence trail from the raw verified assessment (the pipeline's
    # canonical output with facts/analysis/diagnostics), not `normalized`, so the
    # trail never depends on the general normalizer's shape. Attached AFTER
    # validation so it can never affect the reader-integrity gate.
    attach_provenance(reader, assessment)
    if reader_issues:
        detail_suffix = ""
        if "EXECUTIVE_LENGTH_INVALID" in reader_issues:
            executive_words = len(
                str(reader.get("executive_readout") or "").split()
            )
            detail_suffix = f"; executive_words={executive_words}"
        raise ValueError(
            "READER_INTEGRITY: " + ", ".join(reader_issues) + detail_suffix
        )
    return {
        "assessment": normalized,
        "reader": reader,
        "source_warnings": list(dict.fromkeys(
            prepared.warning_codes + operation_context.warning_codes
        )),
    }
