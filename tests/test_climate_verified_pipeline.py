from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace

from sector_lenses.climate_analysis import ContextEvidenceRef
from sector_lenses.climate_source_blocks import (
    DocumentApplicability,
    SourceBlock,
    SourceDocument,
)
from sector_lenses.climate_verified_pipeline import (
    _candidate,
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


def _pass_review_client() -> FakeClient:
    return FakeClient(
        [{
            "verdict": "pass",
            "reason_codes": [],
            "object_ids": [],
        }],
        [],
    )


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
                "evidence_ids": ["PF-001"],
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
                    "current_document_drafting": {
                        "target_document": "PCN",
                        "target_section": "Project Description",
                        "drafting_status": "existing_commitment",
                        "text": ("Add bounded project design language here. " * 18).strip(),
                        "project_basis_ids": ["PF-001"],
                        "gap_basis_ids": ["RG-001"],
                        "guidance_ids": ["GUIDE-PCN-DESIGN"],
                    },
                    "operational_instrument_drafting": None,
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
        "doc_type": "PCN",
        "instrument_type": "IPF",
    }


def test_four_calls_run_when_semantic_review_is_not_required():
    assessment = FakeClient(_responses(), [])
    reviewer = FakeClient(
        [{
            "verdict": "pass",
            "reason_codes": [],
            "object_ids": [],
        }],
        [],
    )
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
        240,
        240,
    ]
    assert all(call["max_transient_retries"] == 1 for call in assessment.calls)
    assert [call["stage"] for call in reviewer.calls] == ["conditional_review"]
    assert result["schema_version"] == "climate-verified-v2.1"
    assert result["validation"]["status"] == "passed"
    assert len(result["priorities"]) == 1
    compiler_payload = assessment.calls[-1]["payload"]
    assert compiler_payload["guidance_registry_version"] == "climate-guidance-v1"
    assert "GUIDE-PCN-DESIGN" in {
        item["guidance_id"] for item in compiler_payload["operational_guidance"]
    }
    assert result["executive_readout"].startswith("Verified project facts")


def test_unresolved_routing_triggers_one_source_first_review():
    assessment = FakeClient(_responses(), [])
    reviewer = FakeClient(
        [
            {
                "verdict": "revise",
                "reason_codes": ["ROUTING_SCOPE_UNVERIFIED"],
                "object_ids": ["REC-001"],
            }
        ],
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
    assert result["recommendation_diagnostics"] == {
        "raw_candidate_count": 1,
        "parsed_candidate_count": 1,
        "valid_candidate_count": 1,
        "admitted_count": 1,
        "final_priority_count": 0,
        "reviewer_invoked": True,
        "reviewer_verdict": "revise",
        "reason_codes": ["ROUTING_SCOPE_UNVERIFIED"],
        "unsupported_numeric_tokens": [],
        "semantic_review_object_ids": ["REC-001"],
        "candidate_suppressions": [
            {
                "recommendation_id": "REC-001",
                "stage": "semantic_review",
                "reason_codes": ["ROUTING_SCOPE_UNVERIFIED"],
                "unsupported_numeric_fields": [],
            }
        ],
    }


def test_semantic_review_targets_only_affected_recommendations():
    responses = _responses()
    second = deepcopy(responses[3]["recommendation_candidates"][0])
    second["recommendation_id"] = "REC-002"
    second["title"] = "Confirm a second bounded site decision"
    responses[3]["recommendation_candidates"].append(second)
    reviewer = FakeClient(
        [
            {
                "verdict": "revise",
                "reason_codes": ["ROUTING_SCOPE_UNVERIFIED"],
                "object_ids": ["REC-001"],
            }
        ],
        [],
    )

    result = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(FakeClient(responses, []), reviewer),
    )

    assert [item["recommendation_id"] for item in result["priorities"]] == [
        "REC-002"
    ]
    diagnostics = result["recommendation_diagnostics"]
    assert diagnostics["semantic_review_object_ids"] == ["REC-001"]
    assert diagnostics["candidate_suppressions"] == [
        {
            "recommendation_id": "REC-001",
            "stage": "semantic_review",
            "reason_codes": ["ROUTING_SCOPE_UNVERIFIED"],
            "unsupported_numeric_fields": [],
        }
    ]


def test_semantic_review_reason_codes_are_bounded():
    reviewer = FakeClient(
        [
            {
                "verdict": "revise",
                "reason_codes": ["routing scope needs review"],
                "object_ids": ["REC-001"],
            }
        ],
        [],
    )
    result = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(
            FakeClient(_responses(), []),
            reviewer,
        ),
    )

    assert result["recommendation_diagnostics"]["reason_codes"] == [
        "SEMANTIC_REVIEW_REASON_INVALID"
    ]


def test_semantic_review_with_unresolved_targets_fails_safe():
    reviewer = FakeClient(
        [
            {
                "verdict": "revise",
                "reason_codes": ["ROUTING_SCOPE_UNVERIFIED"],
                "object_ids": ["RG-001"],
            }
        ],
        [],
    )

    result = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(
            FakeClient(_responses(), []),
            reviewer,
        ),
    )

    assert result["priorities"] == []
    diagnostics = result["recommendation_diagnostics"]
    assert diagnostics["semantic_review_object_ids"] == ["REC-001"]
    assert "SEMANTIC_REVIEW_TARGET_UNRESOLVED" in diagnostics["reason_codes"]


def test_admission_suppression_exposes_bounded_reason_codes():
    responses = _responses()
    recommendation = responses[3]["recommendation_candidates"][0]
    recommendation["score"]["materiality"] = 1
    recommendation["gate_results"]["timing"] = False

    result = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(FakeClient(responses, []), FakeClient([], [])),
    )

    assert result["priorities"] == []
    assert result["recommendation_diagnostics"] == {
        "raw_candidate_count": 1,
        "parsed_candidate_count": 1,
        "valid_candidate_count": 1,
        "admitted_count": 0,
        "final_priority_count": 0,
        "reviewer_invoked": False,
        "reviewer_verdict": "not_invoked",
        "reason_codes": [
            "ADMISSION_MATERIALITY_BELOW_MIN",
            "ADMISSION_GATE_FAILED_TIMING",
        ],
        "unsupported_numeric_tokens": [],
        "semantic_review_object_ids": [],
        "candidate_suppressions": [
            {
                "recommendation_id": "REC-001",
                "stage": "admission",
                "reason_codes": [
                    "ADMISSION_MATERIALITY_BELOW_MIN",
                    "ADMISSION_GATE_FAILED_TIMING",
                ],
                "unsupported_numeric_fields": [],
            }
        ],
    }


def test_source_linked_numeric_label_is_supported_without_model_echo():
    responses = _responses()
    fact = responses[0]["facts"][0]
    excerpt = (
        "The Project Operations Manual will define Component 1.4 site selection."
    )
    fact["object"] = "Component 1.4 site selection"
    fact["supporting_excerpt"] = excerpt
    recommendation = responses[3]["recommendation_candidates"][0]
    recommendation["decision"] = "Confirm the Component 1.4 site-selection method."

    arguments = _arguments()
    arguments["source_blocks"][0] = replace(
        arguments["source_blocks"][0],
        text=excerpt,
    )
    result = run_verified_climate_pipeline(
        **arguments,
        clients=PipelineClients(FakeClient(responses, []), _pass_review_client()),
    )

    assert len(result["priorities"]) == 1
    assert (
        result["recommendation_diagnostics"]["unsupported_numeric_tokens"] == []
    )


def test_model_cannot_self_attest_an_unsourced_numeric_token():
    responses = _responses()
    recommendation = responses[3]["recommendation_candidates"][0]
    recommendation["decision"] = "Complete the review in 2027."
    recommendation["supported_numeric_tokens"] = ["2027"]

    result = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(FakeClient(responses, []), _pass_review_client()),
    )

    assert result["priorities"][0]["decision"] == "Complete the review."
    diagnostics = result["recommendation_diagnostics"]
    assert diagnostics["unsupported_numeric_tokens"] == []
    assert "RECOMMENDATION_UNSUPPORTED_PRECISION_REMOVED" in (
        result["manifest"]["repair_actions"]
    )


def test_numeric_repair_removes_only_bounded_unsupported_tokens():
    responses = _responses()
    recommendation = responses[3]["recommendation_candidates"][0]
    recommendation["minimum_action"] = (
        "Update Components 1 and 2 before the 2027 review."
    )

    result = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(FakeClient(responses, []), _pass_review_client()),
    )

    assert result["priorities"][0]["minimum_action"] == (
        "Update Components before the review."
    )
    diagnostics = result["recommendation_diagnostics"]
    assert diagnostics["reason_codes"] == []
    assert diagnostics["unsupported_numeric_tokens"] == []
    assert diagnostics["candidate_suppressions"] == []


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


def test_precision_suppression_exposes_only_field_path_and_reason_code():
    responses = _responses()
    recommendation = responses[3]["recommendation_candidates"][0]
    recommendation["current_document_drafting"]["text"] = (
        "A hydrometeorological system will establish continuity alerts and "
        "procedures for access disruption. " * 8
    ).strip()

    result = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(
            FakeClient(responses, []),
            FakeClient([], []),
        ),
    )

    assert result["priorities"] == []
    diagnostics = result["recommendation_diagnostics"]
    assert diagnostics["reason_codes"] == ["DRAFTING_SYSTEM_UNVERIFIED"]
    assert diagnostics["candidate_suppressions"] == [
        {
            "recommendation_id": "REC-001",
            "stage": "validation",
            "reason_codes": ["DRAFTING_SYSTEM_UNVERIFIED"],
            "unsupported_numeric_fields": [],
            "unsupported_precision_fields": [
                {
                    "field": "current_document_drafting.text",
                    "reason_code": "DRAFTING_SYSTEM_UNVERIFIED",
                }
            ],
        }
    ]


def test_manifest_is_privacy_safe_and_scoped_to_the_run():
    first = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(FakeClient(_responses(), []), _pass_review_client()),
    )
    second_args = {**_arguments(), "run_id": "run-two"}
    second = run_verified_climate_pipeline(
        **second_args,
        clients=PipelineClients(FakeClient(_responses(), []), _pass_review_client()),
    )

    assert first["manifest"]["run_id"] == "run-test"
    assert second["manifest"]["run_id"] == "run-two"
    assert first["manifest"]["source_count"] == 1
    assert first["manifest"]["renderer_version"] == "climate-reader-v2.2"
    assert first["manifest"]["extraction_version"] == "source-blocks-v2.1"
    assert (
        first["manifest"]["prompt_versions"]["fact_extraction"]
        == "climate-facts-v2.2"
    )
    assert (
        first["manifest"]["prompt_versions"]["bounded_analysis"]
        == "climate-analysis-v2.2"
    )
    assert (
        first["manifest"]["prompt_versions"]["judgment_review"]
        == "climate-judgments-v2.3"
    )
    assert (
        first["manifest"]["prompt_versions"]["recommendation_compiler"]
        == "climate-recommendations-v2.4"
    )
    assert (
        first["manifest"]["prompt_versions"]["conditional_review"]
        == "climate-review-v2.5"
    )
    assert (
        first["manifest"]["prompt_versions"]["drafting_compiler"]
        == "climate-drafting-v1.0"
    )
    assert set(first["manifest"]["prompt_versions"]) == {
        "fact_extraction",
        "bounded_analysis",
        "judgment_review",
        "recommendation_compiler",
        "drafting_compiler",
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
        clients=PipelineClients(FakeClient(_responses(), []), _pass_review_client()),
    )

    assert result["evidence_status"] == "preview; not approved"


def test_candidate_maps_compact_drafting_blocks_to_domain_fields():
    record = deepcopy(_responses()[3]["recommendation_candidates"][0])
    current = record.pop("current_document_drafting")
    record.pop("operational_instrument_drafting")
    record["drafting_blocks"] = [
        {"drafting_role": "current_document", **current}
    ]

    candidate = _candidate(record)

    assert candidate.current_document_drafting is not None
    assert (
        candidate.current_document_drafting.target_section
        == "Project Description"
    )
    assert candidate.operational_instrument_drafting is None


def test_missing_transport_drafting_uses_bounded_drafting_compiler():
    responses = _responses()
    recommendation = responses[3]["recommendation_candidates"][0]
    current = recommendation.pop("current_document_drafting")
    recommendation.pop("operational_instrument_drafting")
    responses.append({
        "drafting_sets": [{
            "recommendation_id": "REC-001",
            "drafting_blocks": [{
                "drafting_role": "current_document",
                **current,
            }],
        }],
    })
    assessment = FakeClient(responses, [])

    result = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(assessment, _pass_review_client()),
    )

    assert [call["stage"] for call in assessment.calls] == [
        "fact_extraction",
        "bounded_analysis",
        "judgment_review",
        "recommendation_compiler",
        "drafting_compiler",
    ]
    assert result["priorities"][0]["current_document_drafting"]["text"] == (
        current["text"]
    )
    drafting_payload = assessment.calls[-1]["payload"]
    assert drafting_payload["recommendation_candidates"][0][
        "recommendation_id"
    ] == "REC-001"
