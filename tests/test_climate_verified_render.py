from __future__ import annotations

from io import BytesIO

from docx import Document

from climate_question_bank import CLIMATE_LITERATURE_REFERENCES
from sector_lenses.climate_verified_render import (
    HEADINGS,
    SENSITIVITY_RATING_QUESTION,
    attach_provenance,
    build_climate_guidance_items,
    build_reader_model,
    render_reader_html,
    validate_reader_model,
    write_reader_docx,
)


def test_build_climate_guidance_items_builds_a_matched_item():
    guidance = build_climate_guidance_items(
        [{"source": "Eligible", "summary": "Verified project finding."}],
        [{"title": "Eligible", "url": "https://www.worldbank.org/guide", "description": "Guidance."}],
    )
    assert guidance[0]["title"] == "Eligible"

def test_build_climate_guidance_items_uses_matched_south_sudan_findings_only():
    sources = [
        {"title": "FCV-Sensitive Climate Action Framework", "url": "https://www.worldbank.org/framework", "practical_value": "Stress-test climate action."},
        {"title": "Maximizing the Peace & Social Dividends of Climate Action", "url": "https://documents.worldbank.org/dividends", "practical_value": "Identify peace dividends."},
        {"title": "Defueling Conflict", "url": "https://www.worldbank.org/defueling", "practical_value": "Must not be padded."},
    ]
    core_questions = [
            {"question": "Question title must never appear.", "source": "fcv sensitive climate action framework", "summary": "Flooding around Pariang can interrupt BFMU access during the rainy season. Delivery partners should update flood access plans before deployment.\n\nA second paragraph is excluded.", "watch": "Track flood-season access constraints for BFMU teams."},
        {"question": "Another title that must never appear.", "source": "Maximizing the Peace and Social Dividends of Climate Action", "summary": "Shared water points for host and displaced households can reduce tensions in Pariang.", "watch": "Check whether benefit allocation remains inclusive after shocks."},
        {"source": "maximizing the peace and social dividends of climate action", "summary": "Flood response should keep displaced households connected to services.", "watch": "Check whether benefit allocation remains inclusive after shocks."},
    ]

    guidance = build_climate_guidance_items(core_questions, sources)

    assert [item["title"] for item in guidance] == ["Maximizing the Peace & Social Dividends of Climate Action", "FCV-Sensitive Climate Action Framework"]
    assert "Flood response should keep displaced households connected to services." in guidance[0]["project_use"]
    assert guidance[0]["project_use"].count("Check whether benefit allocation remains inclusive after shocks.") == 1
    assert "Flooding around Pariang can interrupt BFMU access during the rainy season." in guidance[1]["project_use"]
    assert "Delivery partners should update flood access plans before deployment." in guidance[1]["project_use"]
    assert "A second paragraph" not in guidance[1]["project_use"]
    assert "Question title must never appear" not in str(guidance)
    assert all(set(item) == {"title", "url", "practical_value", "project_use"} for item in guidance)


def test_build_climate_guidance_items_rejects_nonpublic_urls_and_does_not_pad():
    core_questions = [{"source": "Eligible", "summary": "Verified finding."}]
    bad_urls = ["http://www.worldbank.org/no", "https://example.org/no", "https://localhost/no", "https://127.0.0.1/no", "https://user:password@www.worldbank.org/no", "https://www.worldbank.org:443/no", "https://www.worldbank.org:8443/no", "https://www.worldbank.org:bad/no", "https:///missing-host"]

    for url in bad_urls:
        assert build_climate_guidance_items(core_questions, [{"title": "Eligible", "url": url}]) == []
    guidance = build_climate_guidance_items(
        [{"source": "Defueling Conflict", "summary": "Water governance can lower local tensions."}],
        [{"title": "Defueling Conflict", "url": "https://www.worldbank.org/defueling", "description": "Natural resource governance guidance."}, {"title": "CCDR guidance note", "url": "https://www.worldbank.org/ccdr", "description": "Unmatched."}],
    )
    assert [item["title"] for item in guidance] == ["Defueling Conflict"]
    assert guidance[0]["practical_value"] == "Natural resource governance guidance."


def test_build_climate_guidance_items_ranks_caps_and_preserves_catalog_order():
    sources = [{"title": title, "url": f"https://www.worldbank.org/{index}", "practical_value": f"Value {index}."} for index, title in enumerate(("One", "Two", "Three", "Four", "Five"), start=1)]
    core_questions = [
        {"question": "Internal question title", "source": "One", "summary": "One first."},
        {"source": "one", "summary": "One second."},
        {"source": "Two", "summary": "Two first."},
        {"source": "Three", "summary": "Three first."},
        {"source": "Four", "summary": "Four first."},
        {"source": "Five", "summary": "Five first."},
    ]

    guidance = build_climate_guidance_items(core_questions, sources)

    assert [item["title"] for item in guidance] == ["One", "Two", "Three", "Four"]
    assert guidance[0]["project_use"].startswith("For this project, One first. One second.")
    assert "Internal question title" not in str(guidance)
    assert all("match_count" not in item and "catalog_order" not in item for item in guidance)


def test_climate_literature_references_include_exact_practical_values():
    values = {entry["title"]: entry.get("practical_value") for entry in CLIMATE_LITERATURE_REFERENCES}

    assert values == {
        "Maximizing the Peace and Social Dividends of Climate Action": "Use this source to identify how climate action can strengthen peace and social outcomes, and where project design can maximize those dividends.",
        "FCV-Sensitive Climate Action Framework": "Use this source to stress-test whether climate action is conflict-sensitive, avoids harm and remains deliverable in fragile settings.",
        "Defueling Conflict": "Use this source to assess how environmental and natural-resource governance can reduce conflict risks and create incentives for cooperation.",
        "Conflict-Sensitive Climate Action Compendium": "Use this source for practical examples of adapting climate programming to conflict dynamics, exclusion risks and changing implementation conditions.",
        "CCDR guidance note": "Use this source to connect country-level climate and FCV diagnostics to operational priorities, sequencing and investment choices.",
    }


def test_attach_provenance_adds_guidance_items_after_reader_validation():
    assessment = _assessment()
    assessment["core_questions"] = [{"source": "Defueling Conflict", "summary": "Water governance can lower local tensions."}]
    reader = build_reader_model(assessment)
    assert validate_reader_model(reader) == ()

    attach_provenance(reader, assessment)

    assert [item["title"] for item in reader["guidance_items"]] == ["Defueling Conflict"]
def test_build_climate_guidance_items_rejects_malformed_authorities_fail_closed():
    core_questions = [{"source": "Eligible", "summary": "Verified finding."}]
    malformed_urls = [
        "https://.worldbank.org/path",
        "https://foo..worldbank.org/path",
        "https://-foo.worldbank.org/path",
        "https://foo-.worldbank.org/path",
        "https://foo_bar.worldbank.org/path",
        "https://" + ("a" * 64) + ".worldbank.org/path",
        "https://www.worldbank.org%2e/path",
        "https://worldbank.org:/path",
        "https://[::1]/path",
        "https://[::1/path",
        "https://user%3Apassword@www.worldbank.org/path",
        "https://www.w\u00f8rldbank.org/path",
        "https://www.worldbank.org./path",
    ]

    for url in malformed_urls:
        assert build_climate_guidance_items(
            core_questions, [{"title": "Eligible", "url": url}]
        ) == []
    allowed = build_climate_guidance_items(
        core_questions,
        [{"title": "Eligible", "url": "https://WWW.WORLDBANK.ORG/path"}],
    )
    assert [item["url"] for item in allowed] == ["https://WWW.WORLDBANK.ORG/path"]


def test_build_climate_guidance_items_skips_empty_findings_and_completes_sentences():
    source = {"title": "Eligible", "url": "https://www.worldbank.org/guide"}

    assert build_climate_guidance_items(
        [{"source": "Eligible", "summary": "", "watch": ""}], [source]
    ) == []
    guidance = build_climate_guidance_items([
        {"question": "Question title must never appear.", "source": "Eligible", "summary": "U.N. agencies coordinate flood access.", "watch": "Watch flood triggers"},
        {"source": "eligible", "summary": "e.g. community consultation should guide siting.", "watch": "watch flood triggers"},
    ], [source])

    assert guidance[0]["project_use"] == (
        "For this project, U.N. agencies coordinate flood access. "
        "e.g. community consultation should guide siting. Watch flood triggers. "
        "Use this guidance to refine project design and implementation choices."
    )
    assert "Question title must never appear" not in str(guidance)


def test_build_climate_guidance_items_deduplicates_questions_and_catalog_sources():
    sources = [
        {"title": "Defueling Conflict", "url": "https://www.worldbank.org/defueling"},
        {"title": "FCV-Sensitive Climate Action Framework", "url": "https://www.worldbank.org/framework"},
        {"title": "fcv sensitive climate action framework", "url": "https://www.worldbank.org/duplicate"},
    ]
    duplicated_question = {"source": "FCV-Sensitive Climate Action Framework", "summary": "Flood risk needs adaptive delivery.", "watch": "Monitor access."}
    core_questions = [
        duplicated_question,
        dict(duplicated_question),
        {"source": "Defueling Conflict", "summary": "Water governance can reduce tensions."},
    ]

    guidance = build_climate_guidance_items(core_questions, sources)

    assert [item["title"] for item in guidance] == [
        "Defueling Conflict", "FCV-Sensitive Climate Action Framework"
    ]
def test_build_climate_guidance_items_preserves_complete_first_paragraph_only():
    source = {"title": "Eligible", "url": "https://www.worldbank.org/guide"}
    summary = (
        "U.S. agencies coordinate flood access, etc. during the rainy season. "
        "Dr. Amina confirms the contingency.\n\n"
        "This subsequent paragraph must not appear."
    )

    guidance = build_climate_guidance_items(
        [{"source": "Eligible", "summary": summary}], [source]
    )

    assert guidance[0]["project_use"] == (
        "For this project, U.S. agencies coordinate flood access, etc. during the rainy season. "
        "Dr. Amina confirms the contingency. "
        "Use this guidance to refine project design and implementation choices."
    )


def test_build_climate_guidance_items_rejects_overlong_dns_authority():
    hostname = ".".join(["a" * 63] * 4 + ["worldbank", "org"])

    assert build_climate_guidance_items(
        [{"source": "Eligible", "summary": "Verified finding."}],
        [{"title": "Eligible", "url": f"https://{hostname}/guide"}],
    ) == []


def test_build_climate_guidance_items_deduplicates_by_question_id():
    sources = [
        {"title": "Defueling Conflict", "url": "https://www.worldbank.org/defueling"},
        {"title": "FCV-Sensitive Climate Action Framework", "url": "https://www.worldbank.org/framework"},
    ]
    core_questions = [
        {"question_id": "cq-1", "source": "FCV-Sensitive Climate Action Framework", "summary": "Flood risk needs adaptive delivery."},
        {"question_id": "cq-1", "source": "FCV-Sensitive Climate Action Framework", "summary": "Changed text must not increase the match count."},
        {"question_id": "cq-2", "source": "Defueling Conflict", "summary": "Water governance can reduce tensions."},
    ]

    guidance = build_climate_guidance_items(core_questions, sources)

    assert [item["title"] for item in guidance] == [
        "Defueling Conflict", "FCV-Sensitive Climate Action Framework"
    ]
def test_build_climate_guidance_items_preserves_exact_complete_first_paragraphs():
    source = {"title": "Eligible", "url": "https://www.worldbank.org/guide"}
    suffix = " Use this guidance to refine project design and implementation choices."
    cases = [
        "Coordination is led by the U.N.",
        "The note covers access, etc.",
        "Dr. Amina coordinates\nflood access planning.",
        "Flood access may fail... teams need contingencies.",
        "The project is \"high risk.\"",
        "The project is \u201chigh risk.\u201d",
        "The project is [high risk.]",
    ]

    for paragraph in cases:
        guidance = build_climate_guidance_items(
            [{"source": "Eligible", "summary": "\n\n" + paragraph + "\n\nSecond paragraph excluded."}],
            [source],
        )
        normalized = " ".join(paragraph.split())
        assert guidance[0]["project_use"] == (
            "For this project, " + normalized + suffix
        )
def test_build_reader_model_keeps_up_to_five_priorities():
    assessment = {
        "executive_readout": "One. Two. Three.",
        "judgments": {},
        "priorities": [
            {"rank": i, "title": f"Priority {i}", "recommendation_id": f"REC-00{i}"}
            for i in range(1, 7)  # six candidates
        ],
    }
    model = build_reader_model(assessment)
    # Cap is five, not three; a sixth is dropped.
    assert len(model["priorities"]) == 5
    assert [p["title"] for p in model["priorities"]] == [
        f"Priority {i}" for i in range(1, 6)
    ]


def test_rating_scale_renders_in_overview_before_core_questions():
    assessment = {
        "executive_readout": "Alpha sentence. " * 60,
        "judgments": {
            "sensitivity": {
                "value": "moderate", "rationale": "Because.", "evidence_ids": []
            }
        },
        "priorities": [],
    }
    html = render_reader_html(build_reader_model(assessment))
    rating_pos = html.find("climate-sens-rating")
    core_pos = html.find("Core climate-FCV questions")
    assert rating_pos != -1 and core_pos != -1
    # The rating sits in the overview, above the core-questions section.
    assert rating_pos < core_pos


def test_build_reader_model_carries_overview_summary_into_rating_block():
    assessment = {
        "executive_readout": "Alpha. Beta. Gamma.",
        "overview_summary": "OVERVIEW_MARKER first. Second overall sentence. Third.",
        "judgments": {
            "sensitivity": {"value": "strong", "rationale": "Because.", "evidence_ids": []}
        },
        "priorities": [],
    }
    model = build_reader_model(assessment)
    assert model["overview_summary"].startswith("OVERVIEW_MARKER")
    # The factored overview block (the rating unit) carries the summary too.
    assert model["climate_sensitivity_rating"]["overview_summary"].startswith(
        "OVERVIEW_MARKER"
    )


def test_overview_summary_renders_in_overview_box_at_the_very_top():
    assessment = {
        "executive_readout": "Alpha sentence. " * 60,
        "overview_summary": "OVERVIEW_MARKER first. Second overall sentence. Third one.",
        "judgments": {
            "sensitivity": {"value": "strong", "rationale": "Because.", "evidence_ids": []}
        },
        "priorities": [],
    }
    html = render_reader_html(build_reader_model(assessment))
    summary_pos = html.find("OVERVIEW_MARKER")
    rating_pos = html.find("climate-sens-rating")
    exec_heading_pos = html.find("Executive readout")
    assert summary_pos != -1 and rating_pos != -1 and exec_heading_pos != -1
    # The 3-4 sentence overall summary is embedded in the rating card, and the
    # whole overview block sits ABOVE the fuller Executive readout section.
    assert rating_pos < summary_pos
    assert summary_pos < exec_heading_pos


def test_rating_graphic_precedes_summary_text_within_the_box():
    assessment = {
        "executive_readout": "Alpha sentence. " * 60,
        "overview_summary": "OVERVIEW_MARKER first. Second overall sentence. Third one.",
        "judgments": {
            "sensitivity": {"value": "strong", "rationale": "Because.", "evidence_ids": []}
        },
        "priorities": [],
    }
    html = render_reader_html(build_reader_model(assessment))
    question_pos = html.find(SENSITIVITY_RATING_QUESTION)
    summary_pos = html.find("OVERVIEW_MARKER")
    assert question_pos != -1 and summary_pos != -1
    # The "How sensitive" graphic (question + label + scale) sits at the very top
    # of the card, above the overview summary text.
    assert question_pos < summary_pos


def test_overview_summary_renders_in_docx_before_executive_readout():
    assessment = {
        "executive_readout": "Alpha sentence one. Beta sentence two.",
        "overview_summary": "OVERVIEW_MARKER first. Second overall sentence. Third one.",
        "judgments": {
            "sensitivity": {"value": "strong", "rationale": "Because.", "evidence_ids": []}
        },
        "priorities": [],
    }
    stream = BytesIO()
    write_reader_docx(build_reader_model(assessment), stream)
    stream.seek(0)
    texts = [p.text for p in Document(stream).paragraphs]
    question_idx = next(
        i for i, t in enumerate(texts) if t.startswith(SENSITIVITY_RATING_QUESTION)
    )
    summary_idx = next(i for i, t in enumerate(texts) if "OVERVIEW_MARKER" in t)
    exec_idx = next(i for i, t in enumerate(texts) if t == HEADINGS[0])
    # Graphic (rating question line) first, then the summary text, then the
    # fuller Executive readout heading below.
    assert question_idx < summary_idx < exec_idx


def test_overview_box_renders_without_summary_when_absent():
    assessment = {
        "executive_readout": "Alpha. Beta. Gamma.",
        "judgments": {
            "sensitivity": {"value": "strong", "rationale": "Because.", "evidence_ids": []}
        },
        "priorities": [],
    }
    model = build_reader_model(assessment)
    assert model["overview_summary"] == ""
    html = render_reader_html(model)
    # Graceful degradation: the rating card still renders (with its level gloss),
    # just with no embedded overall summary.
    assert "climate-sens-rating" in html
    assert "strongly designed to recognise" in html


def test_visible_tiers_hide_routing_metadata_and_evidence_codes():
    assessment = {
        "executive_readout": "Alpha sentence. " * 60,
        "judgments": {
            "sensitivity": {
                "value": "moderate", "rationale": "Because.", "evidence_ids": ["PF-001"]
            }
        },
        "priorities": [{
            "rank": 1, "title": "Do the thing", "recommendation_id": "REC-001",
            "decision": "Do it.", "minimum_action": "Add a clause.", "confidence": "high",
            "routing_status": "standard_document_advisory", "authority_basis": "none_verified",
            "recommendation_basis": "project_evidence", "pathway_ids": ["PW-001"],
            "project_anchor_ids": ["PF-001"],
            "current_document_drafting": {
                "target_document": "PCN", "target_section": "X",
                "drafting_status": "advisory_proposal", "text": "Add text.",
                "project_basis_ids": [], "gap_basis_ids": [], "guidance_ids": [],
            },
        }],
    }
    model = build_reader_model(assessment)
    html = render_reader_html(model)
    # Priority card must not show the internal routing metadata rows.
    assert "Routing status" not in html
    assert "Authority basis" not in html
    assert "Recommendation basis" not in html
    assert "Pathway references" not in html
    # The priority body must not leak raw evidence codes.
    priorities_section = html.split("Ranked operational priorities", 1)[1].split(
        "Points to check", 1
    )[0]
    assert "PW-001" not in priorities_section
    assert "PF-001" not in priorities_section
    # Provenance remains attached internally but raw codes stay out of the reader.
    model = attach_provenance(model, assessment)
    html2 = render_reader_html(model)
    assert "Evidence key" not in html2
    assert "PF-001" not in html2


def test_quick_fixes_are_visible_not_collapsed():
    assessment = {
        "executive_readout": "Alpha sentence. " * 60,
        "judgments": {
            "sensitivity": {
                "value": "moderate", "rationale": "Because.", "evidence_ids": []
            }
        },
        "priorities": [],
        "minor_climate_points": [
            {"point": "Reconcile the figure", "why": "Two values differ.",
             "how_to_check": "Confirm the cost across cover and tables.",
             "residual_gap_ids": []}
        ],
        "review_readiness_flags": [
            {"flag": "Empty screening field", "why_it_matters": "Template field blank.",
             "document_basis_ids": [], "suggested_verification": "Confirm before the meeting."}
        ],
    }
    html = render_reader_html(build_reader_model(assessment))
    quick = html.split("Ranked operational priorities", 1)[1]
    assert "Reconcile the figure" in quick
    assert "Empty screening field" in quick
    assert "How to address" in quick
    assert "Technical annex" not in quick
    # The quick-fix block is a visible section, not a collapsed <details>.
    assert "<summary>Points to check" not in quick


def test_watch_lines_render_in_standalone_section_not_inline():
    assessment = {
        "executive_readout": "Alpha sentence. " * 60,
        "judgments": {
            "sensitivity": {
                "value": "moderate", "rationale": "Because.", "evidence_ids": []
            }
        },
        "priorities": [],
        "core_questions": [
            {"question_id": "cq1", "theme": "cq1_interaction", "question": "Does X hold?",
             "source": "Guidance", "summary": "A finding.", "evidence_ids": [],
             "watch": "Keep an eye on the flood season."}
        ],
    }
    html = render_reader_html(build_reader_model(assessment))
    # Watch content appears in the standalone section, not inline in the card.
    assert "What to keep an eye on" in html
    assert "Keep an eye on the flood season." in html
    core_block = html.split("Core climate-FCV questions", 1)[1].split(
        "Ranked operational priorities", 1
    )[0]
    assert "What to watch" not in core_block


def _assessment() -> dict[str, object]:
    sentence = (
        "The project evidence supports a material Climate-FCV pathway, while "
        "the documented response remains at an early operational stage. "
    )
    return {
        "schema_version": "climate-verified-v2.1",
        "run_id": "run-1",
        "bank_release_id": "ssd-2026.08",
        "evidence_status": "preview; not approved",
        "executive_readout": sentence * 25,
        "judgments": {
            "relevance": {"value": "high", "rationale": "Material pathway."},
            "sensitivity": {
                "value": "moderate",
                "rationale": "Some relevant risks are recognized.",
            },
            "responsiveness": {
                "value": "emerging",
                "rationale": "Potential benefits are developing.",
            },
            "operationalization": {
                "value": "partial",
                "rationale": "Delivery arrangements remain incomplete.",
            },
        },
        "priorities": [
            {
                "recommendation_id": f"REC-00{index}",
                "rank": index,
                "title": f"Priority {index}",
                "decision": "Make a documented design decision.",
                "minimum_action": "Complete the proportionate minimum action.",
                "enhanced_action": None,
                "enhanced_activation": None,
                "responsible_function": "Task team",
                "routing_status": "standard_document_advisory",
                "authority_basis": "none_verified",
                "recommendation_basis": "project_evidence",
                "project_anchor_ids": ["PF-001"],
                "pathway_ids": ["PW-001"],
                "existing_response_ids": ["ER-001"],
                "residual_gap_ids": ["RG-001"],
                "instrument_claim_ids": [],
                "completion_evidence": "Updated project section",
                "completion_evidence_status": "updated_section",
                "confidence": "medium",
                "limitation": "Detailed parameters remain to be confirmed.",
                "caution": "Avoid unintended exclusion.",
                "current_document_drafting": {
                    "target_document": "PCN",
                    "target_section": "Project Description",
                    "drafting_status": "advisory_proposal",
                    "text": (
                        "Suggested targeted text for the current project document. "
                        * 12
                    ).strip(),
                    "project_basis_ids": ["PF-001"],
                    "gap_basis_ids": ["RG-001"],
                    "guidance_ids": ["GUIDE-PCN-DESIGN"],
                },
                "operational_instrument_drafting": ({
                    "target_document": "Security Risk Management Plan",
                    "target_section": "Continuity arrangements",
                    "drafting_status": "existing_commitment",
                    "text": (
                        "Distinct operational instrument text for continuity. " * 12
                    ).strip(),
                    "project_basis_ids": ["PF-001"],
                    "gap_basis_ids": ["RG-001"],
                    "guidance_ids": ["GUIDE-FCV-CONTINUITY"],
                } if index == 1 else None),
            }
            for index in range(1, 5)
        ],
        "review_readiness_flags": [
            {
                "flag_id": "RF-001",
                "category": "document_inconsistency",
                "flag": "Two sections state different financing totals.",
                "why_it_matters": "The controlling scope cannot be verified.",
                "suggested_verification": "Confirm the controlling total.",
            }
        ],
        "validation": {"status": "passed"},
        "recommendation_diagnostics": {
            "raw_candidate_count": 3,
            "parsed_candidate_count": 3,
            "valid_candidate_count": 3,
            "admitted_count": 3,
            "final_priority_count": 3,
            "reviewer_invoked": False,
            "reviewer_verdict": "not_invoked",
            "reason_codes": [],
            "unsupported_numeric_tokens": [],
            "semantic_review_object_ids": [],
            "candidate_suppressions": [],
        },
    }


def test_reader_has_four_dimensions_priority_cap_and_safe_annex():
    model = build_reader_model(_assessment())

    assert len(model["judgments"]) == 4
    # Fixture supplies four priorities; the cap is now five, so all four survive.
    assert len(model["priorities"]) == 4
    assert model["priority_summary"] == {
        "count": 4,
        "titles": ["Priority 1", "Priority 2", "Priority 3", "Priority 4"],
        "statement": (
            "Drawing on the overview and core climate-FCV questions, the analysis "
            "identifies 4 main operational priorities for strengthening climate "
            "resilience, conflict sensitivity and implementation readiness in this "
            "project. These are followed by secondary points to check before the "
            "decision meeting and issues to keep under review as preparation advances."
        ),
    }
    assert "overall_rating" not in model
    assert model["evidence_status"] == "preview; not approved"
    assert model["technical_annex"] == {
        "run_id": "run-1",
        "schema_version": "climate-verified-v2.1",
        "bank_release_id": "ssd-2026.08",
        "validation_status": "passed",
        "recommendation_candidate_count": 3,
        "recommendation_admitted_count": 3,
        "recommendation_final_count": 3,
        "semantic_reviewer_invoked": False,
        "semantic_reviewer_verdict": "not_invoked",
        "recommendation_reason_codes": [],
        "unsupported_numeric_tokens": [],
        "semantic_review_object_ids": [],
        "candidate_suppressions": [],
        "live_research_count": 0,
    }


def test_judgment_evidence_ids_render_from_tuple_and_list():
    # The pipeline stores judgments via dataclasses.asdict(), which preserves
    # Judgment.evidence_ids as a tuple. The reader must surface those IDs, not
    # drop them because they are a tuple rather than a list.
    assessment = _assessment()
    assessment["judgments"]["relevance"]["evidence_ids"] = ("PF-001", "CE-001")
    assessment["judgments"]["sensitivity"]["evidence_ids"] = ["PF-002"]

    model = build_reader_model(assessment)
    by_dimension = {item["dimension"]: item for item in model["judgments"]}

    assert by_dimension["relevance"]["evidence_ids"] == ["PF-001", "CE-001"]
    assert by_dimension["sensitivity"]["evidence_ids"] == ["PF-002"]


def test_priority_narrative_renders_in_reader_html_and_docx():
    assessment = _assessment()
    assessment["priorities"][0]["narrative"] = (
        "First paragraph tells the story of the gap and what to do.\n\n"
        "Second paragraph covers who leads it and what done looks like."
    )
    model = build_reader_model(assessment)
    assert model["priorities"][0]["narrative"].startswith("First paragraph")

    html = render_reader_html(model)
    assert "First paragraph tells the story of the gap" in html
    assert "Second paragraph covers who leads it" in html

    buffer = BytesIO()
    write_reader_docx(model, buffer)
    buffer.seek(0)
    text = "\n".join(p.text for p in Document(buffer).paragraphs)
    assert "First paragraph tells the story of the gap" in text
    assert "Second paragraph covers who leads it" in text


def test_priority_summary_count_must_match_final_priorities():
    model = build_reader_model(_assessment())
    model["priority_summary"]["count"] = 2

    assert "PRIORITY_SUMMARY_MISMATCH" in validate_reader_model(model)


def test_reader_annex_preserves_bounded_candidate_suppression_path():
    assessment = _assessment()
    detail = {
        "recommendation_id": "REC-001",
        "stage": "validation",
        "reason_codes": ["RECOMMENDATION_NUMBER_UNSUPPORTED"],
        "unsupported_numeric_fields": [
            {"field": "minimum_action", "tokens": ["30"]}
        ],
    }
    assessment["recommendation_diagnostics"]["candidate_suppressions"] = [
        detail
    ]
    assessment["recommendation_diagnostics"]["semantic_review_object_ids"] = [
        "REC-001"
    ]

    model = build_reader_model(assessment)

    assert model["technical_annex"]["candidate_suppressions"] == [detail]
    assert model["technical_annex"]["semantic_review_object_ids"] == [
        "REC-001"
    ]


def test_reader_validation_rejects_placeholder_and_duplicate_titles():
    model = build_reader_model(_assessment())
    model["priorities"][1]["title"] = model["priorities"][0]["title"]
    model["priorities"][0]["minimum_action"] = "[TBD]"

    issues = validate_reader_model(model)

    assert "DUPLICATE_PRIORITY_TITLE" in issues
    assert "UNRESOLVED_PLACEHOLDER" in issues


def test_reader_allows_readiness_flag_to_describe_project_placeholder():
    model = build_reader_model(_assessment())
    flag = model["review_readiness_flags"][0]
    flag["category"] = "material_placeholder"
    flag["flag"] = "The climate screening field remains a placeholder."

    assert validate_reader_model(model) == ()


def test_reader_uses_tolerant_integrity_bounds_for_executive_length():
    model = build_reader_model(_assessment())
    model["executive_readout"] = ("word " * 699) + "word."

    assert "EXECUTIVE_LENGTH_INVALID" not in validate_reader_model(model)

    model["executive_readout"] = ("word " * 249) + "word."
    assert "EXECUTIVE_LENGTH_INVALID" in validate_reader_model(model)

    model["executive_readout"] = ("word " * 949) + "word."
    assert "EXECUTIVE_LENGTH_INVALID" in validate_reader_model(model)


def test_html_and_docx_share_headings_and_priority_order():
    model = build_reader_model(_assessment())
    assert validate_reader_model(model) == ()

    html = render_reader_html(model)
    output = BytesIO()
    write_reader_docx(model, output)
    output.seek(0)
    document = Document(output)
    document_text = "\n".join(
        paragraph.text for paragraph in document.paragraphs
    )

    # HTML and DOCX render the same present headings in the same visual order
    # (robust to conditionally-rendered sections such as the Watch section).
    by_html = sorted((h for h in HEADINGS if h in html), key=html.index)
    by_docx = sorted(
        (h for h in HEADINGS if h in document_text), key=document_text.index
    )
    assert by_html == by_docx
    for index in range(1, 5):
        identifier = f"REC-00{index}"
        assert identifier in html
        assert identifier in document_text
        assert f"Priority {index}" in html
        assert f"Priority {index}" in document_text
    # Drafting blocks stay; model-internal routing metadata and raw evidence
    # codes are no longer rendered in the visible priority card.
    for expected in (
        "Current document drafting",
        "Operational instrument drafting",
        "Suggested targeted text for the current project document.",
        "Distinct operational instrument text for continuity.",
        "GUIDE-PCN-DESIGN",
        "GUIDE-FCV-CONTINUITY",
    ):
        assert expected in html
        assert expected in document_text
    for removed in ("standard_document_advisory", "none_verified", "project_evidence"):
        assert removed not in html
        assert removed not in document_text
    assert not any(
        paragraph.text.rstrip().endswith(("[", "{", "..."))
        for paragraph in document.paragraphs
    )
    assert html.count("Operational instrument drafting") == 1
    assert document_text.count("Operational instrument drafting") == 1
    assert html.index("Current document drafting") < html.index(
        "Operational instrument drafting"
    )


def _reader_with_balanced_hierarchy_content() -> dict[str, object]:
    assessment = _assessment()
    assessment["minor_climate_points"] = [{
        "point": "Confirm heat safeguards for field teams.",
        "why": "Hotter working conditions may affect delivery.",
        "how_to_check": "Check the ESMP and contractor procedures.",
        "residual_gap_ids": ["RG-002"],
    }]
    assessment["core_questions"] = [
        {
            "question_id": "cq1",
            "theme": "cq1_interaction",
            "question": "Can shared institutions reduce resource tensions?",
            "source": "Maximizing the Peace and Social Dividends of Climate Action",
            "summary": "BFMUs bring competing resource users into shared governance.",
            "evidence_ids": [],
            "watch": "Track whether benefit-sharing remains inclusive.",
        },
        {
            "question_id": "cq2",
            "theme": "cq2_conflict_sensitivity",
            "question": "Will delivery remain workable during floods?",
            "source": "FCV-Sensitive Climate Action Framework",
            "summary": "Flood access arrangements need to cover remote sites.",
            "evidence_ids": [],
            "watch": "Review combined flood-conflict contingencies.",
        },
    ]
    assessment["priorities"][3]["narrative"] = (
        "Complete drafting paragraph for priority four."
    )
    model = build_reader_model(assessment)
    model["guidance_items"] = [{
        "title": "Maximizing the Peace and Social Dividends of Climate Action",
        "url": "https://www.worldbank.org/peace-dividends",
        "practical_value": "Use this source to identify positive peace outcomes.",
        "project_use": "For this project, BFMUs can strengthen shared governance.",
    }]
    model["sources"] = [{
        "title": "Maximizing the Peace and Social Dividends of Climate Action",
        "url": "https://www.worldbank.org/peace-dividends",
        "description": "Guidance on peace and social dividends.",
    }]
    model["evidence_trail"] = {
        "methodology_note": "The analysis used verified project evidence.",
        "pathways": [{
            "direction_label": "Climate -> FCV",
            "chain_prose": "Flood disruption can increase resource tensions.",
        }],
        "limitations": "The analysis depends on the uploaded document's detail.",
        "evidence_key": [{"id": "PF-001", "type_label": "Project fact", "text": "Hidden."}],
        "diagnostics": {"candidate_count": 4, "final_count": 4},
    }
    return model


def test_html_uses_balanced_hierarchy_without_reader_clutter():
    model = _reader_with_balanced_hierarchy_content()
    html = render_reader_html(model)

    assert '<section class="climate-overview-panel climate-sens-rating"' in html
    assert html.count("climate-overview-panel") == 1
    assert '<section class="climate-overview-panel"><div' not in html
    assert html.index("climate-overview-panel") < html.index("Executive readout")
    assert html.count('<details class="climate-priority-disclosure" open>') == 1
    assert html.count('<details class="climate-priority-disclosure">') == 3
    assert '<summary><h3 class="climate-priority-title">1. Priority 1' in html
    assert "Suggested targeted text for the current project document." in html
    assert "Distinct operational instrument text for continuity." in html
    assert "Complete drafting paragraph for priority four." in html
    assert html.index("Smaller climate &amp; fragility points") < html.index(
        "Document points to confirm"
    )
    assert "<h3>Smaller climate &amp; fragility points to consider</h3>" in html
    assert "<h4>Confirm heat safeguards for field teams.</h4>" in html
    assert "<h3>Document points to confirm</h3>" in html
    assert "<h4>Two sections state different financing totals.</h4>" in html
    assert html.count('class="climate-item-number"') == 4
    assert html.count('<span class="climate-item-number">01</span>') == 3
    assert '<span class="climate-item-number">02</span>' in html
    assert html.index("Relevant WBG guidance for this project") < html.index(
        "Method, limitations, and sources"
    )
    assert "Use this source to identify positive peace outcomes." in html
    assert "For this project, BFMUs can strengthen shared governance." in html
    assert "The analysis depends on the uploaded document&#x27;s detail." in html
    assert "Sources &amp; further reading" in html
    for removed in (
        "Evidence status", "preview; not approved", "Technical annex",
        "Evidence key", "Run diagnostics",
    ):
        assert removed not in html


def test_html_heading_structure_is_ordered_and_priorities_navigable():
    html = render_reader_html(_reader_with_balanced_hierarchy_content())

    assert html.count('<summary><h3 class="climate-priority-title">') == 4
    assert '<summary><h3 class="climate-priority-title">1. Priority 1' in html
    assert "<h2>Points to check before the decision meeting</h2>" in html
    assert "<h3>Smaller climate &amp; fragility points to consider</h3>" in html
    assert "<h4>Confirm heat safeguards for field teams.</h4>" in html
    assert "<h3>Document points to confirm</h3>" in html
    assert "<h4>Two sections state different financing totals.</h4>" in html


def test_docx_matches_balanced_reader_content_and_keeps_all_priorities():
    model = _reader_with_balanced_hierarchy_content()
    stream = BytesIO()
    write_reader_docx(model, stream)
    stream.seek(0)
    text = "\n".join(paragraph.text for paragraph in Document(stream).paragraphs)

    for index in range(1, 5):
        assert f"Priority {index}" in text
    assert "Suggested targeted text for the current project document." in text
    assert "Distinct operational instrument text for continuity." in text
    assert "Complete drafting paragraph for priority four." in text
    assert text.index("Smaller climate & fragility points") < text.index(
        "Document points to confirm"
    )
    assert "01 Confirm heat safeguards for field teams." in text
    assert "01 Two sections state different financing totals." in text
    assert "01 Can shared institutions reduce resource tensions?" in text
    assert "02 Will delivery remain workable during floods?" in text
    assert text.index("Relevant WBG guidance for this project") < text.index(
        "Method, limitations, and sources"
    )
    assert "Use this source to identify positive peace outcomes." in text
    assert "For this project, BFMUs can strengthen shared governance." in text
    assert "https://www.worldbank.org/peace-dividends" in text
    assert "The analysis depends on the uploaded document's detail." in text
    assert "Sources & further reading" in text
    for removed in (
        "Evidence status", "preview; not approved", "Technical annex",
        "Evidence key", "Run diagnostics",
    ):
        assert removed not in text


def test_zero_priority_message_is_shared_by_html_and_docx():
    assessment = _assessment()
    assessment["priorities"] = []
    model = build_reader_model(assessment)

    rendered = render_reader_html(model)
    stream = BytesIO()
    write_reader_docx(model, stream)
    stream.seek(0)
    document_text = "\n".join(
        paragraph.text for paragraph in Document(stream).paragraphs
    )

    message = "No recommendation passed the admission threshold for this run."
    assert rendered.count(message) == 1
    assert document_text.count(message) == 1
    assert "No final operational priority was admitted" not in rendered
    assert "No final operational priority was admitted" not in document_text


def test_semantic_review_suppression_is_explained_in_html_and_docx():
    assessment = _assessment()
    assessment["priorities"] = []
    assessment["recommendation_diagnostics"] = {
        "raw_candidate_count": 3,
        "admitted_count": 3,
        "final_priority_count": 0,
        "reviewer_invoked": True,
        "reviewer_verdict": "revise",
        "reason_codes": ["PROJECT_FACT_PROVENANCE_UNSUPPORTED"],
    }
    model = build_reader_model(assessment)

    rendered = render_reader_html(model)
    stream = BytesIO()
    write_reader_docx(model, stream)
    stream.seek(0)
    document_text = "\n".join(
        paragraph.text for paragraph in Document(stream).paragraphs
    )

    message = (
        "3 recommendation candidates passed deterministic admission but were "
        "withheld after semantic review. Review outcome: revise."
    )
    assert message in rendered
    assert message in document_text
    assert "No recommendation passed the admission threshold" not in rendered
    assert "No recommendation passed the admission threshold" not in document_text


def test_html_escapes_model_authored_content():
    assessment = _assessment()
    assessment["priorities"][0]["title"] = "<script>alert('x')</script>"
    model = build_reader_model(assessment)

    rendered = render_reader_html(model)

    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered


def test_docx_writer_accepts_an_in_memory_stream():
    model = build_reader_model(_assessment())
    stream = BytesIO()

    returned = write_reader_docx(model, stream)

    assert returned is stream
    stream.seek(0)
    texts = [p.text for p in Document(stream).paragraphs]
    # The overview block now leads; the Executive readout heading follows below it.
    assert texts[0].startswith(SENSITIVITY_RATING_QUESTION)
    assert HEADINGS[0] in texts


def test_smoke_runtime_is_watermarked_in_html_and_docx():
    model = build_reader_model(_assessment())
    model["runtime_mode"] = "smoke"
    model["technical_annex"]["runtime_mode"] = "smoke"

    rendered = render_reader_html(model)
    stream = BytesIO()
    write_reader_docx(model, stream)
    stream.seek(0)
    document_text = "\n".join(
        paragraph.text for paragraph in Document(stream).paragraphs
    )

    warning = (
        "Smoke test: validates workflow completion only; "
        "not a quality benchmark."
    )
    assert warning in rendered
    assert warning in document_text


def test_quality_runtime_does_not_show_smoke_watermark():
    model = build_reader_model(_assessment())
    model["runtime_mode"] = "quality"

    assert "Smoke test:" not in render_reader_html(model)
