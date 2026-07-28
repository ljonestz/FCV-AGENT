"""Tests for the WBG-source climate-FCV core-question bank and trigger selector."""

import climate_question_bank as bank


VALID_THEMES = {
    "cq1_interaction", "cq2_maladaptation", "cq3_dividends",
    "cq4_inclusion", "cq5_institutions", "cq6_adaptive",
}


def test_bank_entries_have_required_shape():
    assert bank.CLIMATE_QUESTION_BANK, "bank must not be empty"
    for q in bank.CLIMATE_QUESTION_BANK:
        assert q["theme"] in VALID_THEMES, q
        assert q["id"] and isinstance(q["id"], str)
        assert q["question"].strip()
        assert q["source"].strip()
        assert isinstance(q["triggers"], list) and q["triggers"], q
        # triggers are lowercase keyword tokens matched against project signals
        assert all(isinstance(t, str) and t == t.lower() for t in q["triggers"])


def test_bank_ids_are_unique():
    ids = [q["id"] for q in bank.CLIMATE_QUESTION_BANK]
    assert len(ids) == len(set(ids))


def test_every_theme_has_at_least_one_bank_question():
    covered = {q["theme"] for q in bank.CLIMATE_QUESTION_BANK}
    assert VALID_THEMES <= covered


def test_selector_fires_relevant_questions_by_signal():
    # A fisheries/flood/refugee project fires interaction, inclusion, HDP, infra.
    signals = ["IPF fisheries", "Sudd flooding and displacement",
               "refugee and host communities", "cold storage infrastructure",
               "community co-management"]
    fired = bank.select_triggered_questions(signals)
    assert "cq1_interaction" in fired
    assert any(q["id"] == "cq2-infra-horizon" for q in fired.get("cq2_maladaptation", []))
    assert any(q["id"] == "cq5-hdp-nexus" for q in fired.get("cq5_institutions", []))


def test_selector_omits_unfired_themes_but_always_keeps_cq1():
    fired = bank.select_triggered_questions("a project with no matching keywords zzz")
    assert "cq1_interaction" in fired  # always guaranteed
    # A theme with no trigger match is omitted entirely (curation, not padding).
    assert "cq2_maladaptation" not in fired


def test_selector_accepts_plain_string():
    fired = bank.select_triggered_questions("drought and grazing and conservancy governance")
    assert "cq1_interaction" in fired
    assert "cq3_dividends" in fired  # 'governance' fires cq3-peace-dividend


def test_question_plan_preserves_anchors_and_surfaces_material_candidate():
    plan = bank.build_question_plan(
        "flood displacement humanitarian coordination cold storage"
    )

    assert "cq1_interaction" in plan["anchors"]
    assert any(
        item["id"] == "cq5-hdp-nexus"
        for item in plan["supplementary_candidates"]
    )
    assert all(
        set(item) == {"id", "theme", "question", "source"}
        for item in plan["supplementary_candidates"]
    )


def test_question_plan_candidates_are_deterministic_and_deduplicated():
    signals = [
        "humanitarian displacement humanitarian",
        "displacement and refugee coordination",
        "humanitarian displacement",
    ]

    first = bank.build_question_plan(signals)
    second = bank.build_question_plan(signals)
    candidate_ids = [
        item["id"] for item in first["supplementary_candidates"]
    ]

    assert first == second
    assert candidate_ids.count("cq5-hdp-nexus") == 1
    assert len(candidate_ids) == len(set(candidate_ids))


def test_question_plan_does_not_treat_guaranteed_anchor_as_candidate():
    plan = bank.build_question_plan("a project with no matching keywords zzz")

    assert "cq1_interaction" in plan["anchors"]
    assert plan["supplementary_candidates"] == []


def test_question_plan_trigger_matching_respects_word_boundaries():
    plan = bank.build_question_plan(
        "a broad stakeholder assessment on an island"
    )
    candidate_ids = {
        item["id"] for item in plan["supplementary_candidates"]
    }

    assert "cq2-infra-horizon" not in candidate_ids
    assert "cq2-access-path-dependence" not in candidate_ids


def test_trigger_matching_preserves_multiword_and_hyphenated_phrases():
    plan = bank.build_question_plan(
        "long-term climate projection and results framework"
    )
    candidate_ids = {
        item["id"] for item in plan["supplementary_candidates"]
    }

    assert "cq6-time-horizons" in candidate_ids
    assert "cq6-adaptive-triggers" in candidate_ids
    assert "cq6_adaptive" in plan["anchors"]


def test_trigger_matching_supports_controlled_inflections():
    plan = bank.build_question_plan(
        "flooding livelihoods institutions markets benefits resources"
    )
    candidate_ids = {
        item["id"] for item in plan["supplementary_candidates"]
    }

    assert {
        "cq1-hazard-delivery",
        "cq1-access-security",
        "cq2-access-path-dependence",
        "cq3-peace-dividend",
        "cq3-shared-benefit",
        "cq5-delivery-institutions",
    } <= candidate_ids


def test_trigger_matching_treats_spaces_and_hyphens_as_separators():
    for signals in ("results-framework", "early-warning"):
        plan = bank.build_question_plan(signals)
        candidate_ids = {
            item["id"] for item in plan["supplementary_candidates"]
        }

        assert "cq6-adaptive-triggers" in candidate_ids
