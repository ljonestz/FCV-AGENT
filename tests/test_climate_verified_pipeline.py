from __future__ import annotations

from dataclasses import dataclass

from sector_lenses.climate_analysis import ContextEvidenceRef
from sector_lenses.climate_source_blocks import (
    DocumentApplicability,
    SourceBlock,
    SourceDocument,
)
from sector_lenses.climate_verified_pipeline import (
    PipelineClients,
    run_verified_climate_pipeline,
)


@dataclass
class FakeClient:
    responses: list[dict[str, object]]
    calls: list[dict[str, object]]

    def complete_json(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


def _source() -> tuple[list[SourceDocument], list[SourceBlock]]:
    document = SourceDocument(
        document_id="DOC-1",
        filename="pcn.docx",
        sha256="abc123",
        applicability=DocumentApplicability.VERIFIED,
        relationship="primary",
        version_status="latest",
        operation_match="verified",
    )
    block = SourceBlock(
        block_id="DOC-1-B-1",
        document_id="DOC-1",
        text="The Project Operations Manual will define site selection.",
        normalized_hash="block123",
        heading_path=("Components",),
        paragraph_index=1,
    )
    return [document], [block]


def _responses(*, unresolved_routing: bool = False):
    routing = "team_to_confirm" if unresolved_routing else "verified_existing"
    instrument_ids = [] if unresolved_routing else ["PF-001"]
    return [
        {
            "facts": [
                {
                    "claim_id": "PF-001",
                    "claim_type": "named_instrument",
                    "subject": "Project Operations Manual",
                    "predicate": "will define",
                    "object": "site selection",
                    "epistemic_status": "explicit",
                    "source_block_ids": ["DOC-1-B-1"],
                    "supporting_excerpt": (
                        "The Project Operations Manual will define site selection."
                    ),
                    "confidence": "high",
                }
            ],
            "derived_assertions": [],
        },
        {
            "existing_responses": [],
            "pathways": [
                {
                    "pathway_id": "PW-001",
                    "direction": "climate_to_fcv",
                    "chain": ["flood", "access disruption", "exclusion"],
                    "project_anchor_ids": ["PF-001"],
                    "evidence_ids": ["CE-001"],
                    "confidence": "medium",
                }
            ],
            "residual_gaps": [
                {
                    "gap_id": "RG-001",
                    "gap_type": "not_yet_specified",
                    "statement": "Site criteria are not yet specified.",
                    "pathway_ids": ["PW-001"],
                    "project_anchor_ids": ["PF-001"],
                    "existing_response_ids": [],
                    "evidence_ids": ["CE-001"],
                    "confidence": "medium",
                }
            ],
        },
        {
            "executive_readout": (
                "Verified project facts support a bounded Climate-FCV readout. " * 45
            ).strip(),
            "relevance": {
                "value": "high",
                "evidence_ids": ["PW-001"],
                "rationale": "A material pathway is connected to project design.",
            },
            "sensitivity": {
                "value": "limited",
                "evidence_ids": ["RG-001"],
                "rationale": "The residual gap remains material.",
            },
            "responsiveness": {
                "value": "not_expected",
                "evidence_ids": [],
                "rationale": "Responsiveness is not required for this design choice.",
            },
            "operationalization": {
                "value": "early",
                "evidence_ids": ["PF-001"],
                "rationale": "An instrument is named but its requirements are open.",
            },
        },
        {
            "recommendation_candidates": [
                {
                    "recommendation_id": "REC-001",
                    "title": "Define climate-FCV site-selection criteria",
                    "pathway_ids": ["PW-001"],
                    "existing_response_ids": [],
                    "residual_gap_ids": ["RG-001"],
                    "project_anchor_ids": ["PF-001"],
                    "decision": "Decide how site selection will address the pathway.",
                    "minimum_action": "Document exposure and access considerations.",
                    "enhanced_action": None,
                    "enhanced_activation": None,
                    "routing_status": routing,
                    "instrument_claim_ids": instrument_ids,
                    "responsible_function": "Task team",
                    "authority_basis": "project_commitment",
                    "recommendation_basis": "project_evidence",
                    "completion_evidence": "Updated site-selection method",
                    "completion_evidence_status": "updated_section",
                    "confidence": "medium",
                    "limitation": "Site-level conditions remain to be verified.",
                    "caution": "Avoid restricting necessary seasonal mobility.",
                    "drafting_language": None,
                    "score": {
                        "materiality": 3,
                        "gap_strength": 2,
                        "leverage_urgency": 2,
                        "evidence": 2,
                        "feasibility": 1,
                    },
                    "gate_results": {
                        "connection": True,
                        "residuality": True,
                        "materiality": True,
                        "actionability": True,
                        "timing": True,
                        "distinctiveness": True,
                    },
                }
            ],
            "readiness_flags": [],
        },
    ]


def _arguments():
    documents, blocks = _source()
    context = [
        ContextEvidenceRef(
            evidence_id="CE-001",
            evidence_class="country",
            scope="national",
            statement="Flooding can disrupt access.",
            source_ref="bank:ssd-2026.08:E-001",
            confidence="medium",
        )
    ]
    return {
        "source_documents": documents,
        "source_blocks": blocks,
        "context_evidence": context,
        "bank_release_id": "2026.08",
        "run_id": "run-test",
    }


def test_four_calls_run_when_semantic_review_is_not_required():
    assessment = FakeClient(_responses(), [])
    reviewer = FakeClient([], [])
    result = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(assessment, reviewer),
    )

    assert [call["stage"] for call in assessment.calls] == [
        "fact_extraction",
        "bounded_analysis",
        "judgment_review",
        "recommendation_compiler",
    ]
    assert [call["timeout_seconds"] for call in assessment.calls] == [
        300,
        180,
        60,
        240,
    ]
    assert all(call["max_transient_retries"] == 1 for call in assessment.calls)
    assert reviewer.calls == []
    assert result["schema_version"] == "climate-verified-v2"
    assert result["validation"]["status"] == "passed"
    assert len(result["priorities"]) == 1
    assert result["executive_readout"].startswith("Verified project facts")


def test_unresolved_routing_triggers_one_source_first_review():
    assessment = FakeClient(_responses(unresolved_routing=True), [])
    reviewer = FakeClient(
        [{"verdict": "revise", "reason_codes": ["ROUTING_SCOPE_UNVERIFIED"]}],
        [],
    )
    result = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(assessment, reviewer),
    )

    assert len(reviewer.calls) == 1
    assert reviewer.calls[0]["stage"] == "conditional_review"
    assert reviewer.calls[0]["timeout_seconds"] == 120
    assert "source_blocks" in reviewer.calls[0]["payload"]
    assert result["validation"]["status"] == "attention"
    assert result["priorities"] == []
    assert result["manifest"]["suppressed_counts"]["recommendations"] == 1


def test_bad_fact_suppresses_dependent_analysis_and_recommendation():
    responses = _responses()
    responses[0]["facts"][0]["supporting_excerpt"] = "Invented excerpt"
    result = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(FakeClient(responses, []), FakeClient([], [])),
    )

    assert result["facts"] == []
    assert result["analysis"]["pathways"] == []
    assert result["priorities"] == []
    assert "FACT_SOURCE_UNRESOLVED" in result["validation"]["reason_codes"]


def test_manifest_is_privacy_safe_and_scoped_to_the_run():
    first = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(FakeClient(_responses(), []), FakeClient([], [])),
    )
    second_args = {**_arguments(), "run_id": "run-two"}
    second = run_verified_climate_pipeline(
        **second_args,
        clients=PipelineClients(FakeClient(_responses(), []), FakeClient([], [])),
    )

    assert first["manifest"]["run_id"] == "run-test"
    assert second["manifest"]["run_id"] == "run-two"
    assert first["manifest"]["source_count"] == 1
    assert set(first["manifest"]["prompt_versions"]) == {
        "fact_extraction",
        "bounded_analysis",
        "judgment_review",
        "recommendation_compiler",
        "conditional_review",
    }
    manifest_text = str(first["manifest"])
    assert "Project Operations Manual will define" not in manifest_text
    assert "prompt_text" not in manifest_text


def test_preview_label_survives_into_reader_payload():
    args = _arguments()
    args["context_evidence"] = [
        ContextEvidenceRef(
            evidence_id="CE-001",
            evidence_class="country",
            scope="national",
            statement="Flooding can disrupt access.",
            source_ref="bank-preview:2026.08:E-001",
            confidence="medium",
            preview_status="preview; not approved",
        )
    ]
    result = run_verified_climate_pipeline(
        **args,
        clients=PipelineClients(FakeClient(_responses(), []), FakeClient([], [])),
    )

    assert result["evidence_status"] == "preview; not approved"
