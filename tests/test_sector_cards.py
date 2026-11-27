"""Tests for the mechanism-card package: schema, datasheet parser and eligibility router (design v3)."""
from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from sector_cards import (
    CardError,
    FeatureEvidence,
    ProjectFacts,
    load_cards,
    parse_cards,
    parse_practice_areas,
    resolve_sectors,
    route,
)
from sector_cards.models import CARDS_PATH

CARDS = load_cards()


# --- schema -----------------------------------------------------------------------------------------------

def test_card_file_loads_and_is_within_budget():
    assert len(CARDS.cards) == 20
    assert all(c.est_tokens <= 260 for c in CARDS.cards)
    assert all(c.user_citations for c in CARDS.cards)


def test_mc24_is_reachable_only_through_the_dpf_route():
    mc24 = CARDS.by_id()["mc-24"]
    assert mc24.routes == ("dpf_prior_action",)
    assert all(f.startswith("pa_") for f in mc24.features)


def _raw():
    return yaml.safe_load(CARDS_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("mutate, message", [
    (lambda c: c.update(prompt_text="The project must define local hiring."), "advisory wording"),
    (lambda c: c.update(core_mappings=["ost:13"]), "unknown values"),
    (lambda c: c.update(features=["not_a_feature"]), "unknown values"),
    (lambda c: c.update(sources=[{"citation": "x", "kind": "internal", "cite_to_user": True}]), "internal sources"),
    (lambda c: c.update(sources=[{"citation": "x", "kind": "internal", "cite_to_user": False}]), "citable to users"),
    (lambda c: c.update(look_for="x " * 2000), "exceeds"),
])
def test_schema_rejects_bad_cards(mutate, message):
    doc = _raw()
    mutate(doc["cards"][0])
    with pytest.raises(CardError, match=message):
        parse_cards(doc)


def test_schema_rejects_duplicate_ids():
    doc = _raw()
    doc["cards"].append(copy.deepcopy(doc["cards"][0]))
    with pytest.raises(CardError, match="duplicate"):
        parse_cards(doc)


# --- datasheet parser (synthetic layouts seen in the probe) -------------------------------------------------

@pytest.mark.parametrize("text, lead, contributing", [
    (("INSTITUTIONAL DATA Practice Area (Lead) Contributing Practice Areas Water Environment, Natural Resources & "
     "the Blue Economy Climate Change and Disaster Screening Yes"), "Water",
     ("Environment, Natural Resources & the Blue Economy",)),
    (("Practice Area (Lead) Contributing Practice Areas Agriculture and Food Environment, Natural Resources & the "
     "Blue Economy, Urban, Resilience and Land, Water Climate Change and Disaster Screening"), "Agriculture and Food",
     ("Environment, Natural Resources & the Blue Economy", "Urban, Resilience and Land", "Water")),
    (("Practice Area (Lead) Environment, Natural Resources & the Blue Economy Contributing Practice Areas Finance, "
     "Competitiveness and Innovation OVERALL RISK RATING"), "Environment, Natural Resources & the Blue Economy",
     ("Finance, Competitiveness and Innovation",)),
    # Older PID table: the value follows several labels.
    (("Region Estimated Board Date Practice Area (Lead) Financing Instrument Eastern and Southern Africa 15-Jun-2022 "
     "Macroeconomics, Trade and Investment Development Policy Financing"), "Macroeconomics, Trade and Investment", ()),
    # Retired name and an alias for agriculture.
    (("Practice Area (Lead) Contributing Practice Areas Social, Urban, Rural and Resilience Global Practice Climate "
     "Change and Disaster Screening"), "Social, Urban, Rural and Resilience", ()),
    (("Practice Area (Lead) Contributing Practice Areas Water Agriculture, Fragile, Conflict & Violence Climate "
     "Change and Disaster Screening"), "Water", ("Agriculture and Food", "Fragile, Conflict & Violence")),
])
def test_parse_practice_areas_layouts(text, lead, contributing):
    pa = parse_practice_areas(text)
    assert pa.lead == lead
    assert pa.contributing == contributing


def test_parser_ignores_gef_focal_area_and_reads_cover():
    text = ("Water Global Practice\nWestern and Central Africa Region\n" + "x " * 50 +
            "Practice Area (Lead) Contributing Practice Areas Water GEF Focal Area: Climate Change Climate Change and "
            "Disaster Screening")
    pa = parse_practice_areas(text)
    assert pa.lead == "Water" and pa.contributing == ()
    assert pa.cover_gps == ("Water",)


def test_parser_without_label():
    pa = parse_practice_areas("Project Concept Note\nTransport\nsome text")
    assert pa.lead is None and not pa.found_label
    assert pa.cover_gps == ("Transport",)


# --- decision table ---------------------------------------------------------------------------------------

def test_step1_lead_fires_and_step2_non_pilot_does_not():
    assert resolve_sectors(ProjectFacts(instrument="IPF", pa_lead_parsed="Transport"))[0] == ["transport"]
    assert resolve_sectors(ProjectFacts(instrument="IPF", pa_lead_parsed="Social Sustainability and Inclusion",
                                        stage1_sector="water", stage1_confidence="high", pdo_names_sector=True,
                                        sector_financing_share={"water": 0.9}))[0] == []
    assert resolve_sectors(ProjectFacts(instrument="IPF", pa_lead_parsed="Other"))[0] == []


def test_ews_leads_need_the_ews_check_and_take_precedence_over_enrm():
    surr = "Social, Urban, Rural and Resilience"
    assert resolve_sectors(ProjectFacts(pa_lead_parsed=surr))[0] == []
    assert resolve_sectors(ProjectFacts(pa_lead_parsed=surr, ews_is_primary=True))[0] == ["ews_hydromet"]
    assert resolve_sectors(ProjectFacts(pa_lead_parsed="Climate Change", ews_is_primary=True))[0] == ["ews_hydromet"]
    assert resolve_sectors(ProjectFacts(pa_lead_parsed="Climate Change"))[0] == ["enrm"]


def test_second_sector_needs_contributing_pa_share_and_confidence():
    base = {"instrument": "IPF", "pa_lead_parsed": "Water", "pa_contributing": ("Agriculture and Food",)}
    assert resolve_sectors(ProjectFacts(**base, sector_financing_share={"agriculture": 0.4},
                                        stage1_confidence="high"))[0] == ["water", "agriculture"]
    assert resolve_sectors(ProjectFacts(**base, sector_financing_share={"agriculture": 0.2},
                                        stage1_confidence="high"))[0] == ["water"]
    assert resolve_sectors(ProjectFacts(**base, sector_financing_share={"agriculture": 0.4},
                                        stage1_confidence="medium"))[0] == ["water"]
    # Unattributed multi-purpose component: no share given, no second sector.
    assert resolve_sectors(ProjectFacts(**base, stage1_confidence="high"))[0] == ["water"]


def test_step3_cover_and_stage1_route():
    assert resolve_sectors(ProjectFacts(cover_gps=("Water",)))[0] == ["water"]
    assert resolve_sectors(ProjectFacts(cover_gps=("Water", "Transport")))[0] == []
    ok = {"stage1_sector": "transport", "stage1_confidence": "high", "pdo_names_sector": True}
    assert resolve_sectors(ProjectFacts(**ok, sector_financing_share={"transport": 0.9}))[0] == ["transport"]
    assert resolve_sectors(ProjectFacts(**ok))[0] == []  # financing shares missing: nothing fires
    assert resolve_sectors(ProjectFacts(**ok, sector_financing_share={"transport": 0.4}))[0] == []


def test_instrument_rules_and_disagreement():
    assert resolve_sectors(ProjectFacts(instrument="DPF", pa_lead_parsed="Water"))[0] == []
    assert resolve_sectors(ProjectFacts(cerc_only=True, pa_lead_parsed="Water"))[0] == []
    assert resolve_sectors(ProjectFacts(pa_lead_parsed="Water", pa_lead_model="Transport"))[0] == []


# --- feature layer and card eligibility -------------------------------------------------------------------

def test_immaterial_feature_never_routes_a_card():
    facts = ProjectFacts(instrument="IPF", pa_lead_parsed="Health, Nutrition & Population", fcv_setting="active_conflict",
                         features=(FeatureEvidence("water_points_wash", financing_share=0.02, mechanism_evidence=True),))
    assert route(facts, CARDS).eligible == []


def test_material_feature_routes_cards_without_a_sector():
    facts = ProjectFacts(instrument="IPF", pa_lead_parsed="Health, Nutrition & Population", fcv_setting="displacement_hosting",
                         features=(FeatureEvidence("water_points_wash", financing_share=0.14, mechanism_evidence=True,
                                                   page="22"),))
    res = route(facts, CARDS)
    assert res.sectors == []
    assert res.eligible and all(e["route"] == "feature" for e in res.eligible)
    assert {"mc-03", "mc-05"} <= set(res.eligible_ids)


def test_feature_route_needs_fragile_setting_and_mechanism_evidence():
    fe = FeatureEvidence("local_funds_cdd", named=True, mechanism_evidence=True)
    assert route(ProjectFacts(fcv_setting="any", features=(fe,)), CARDS).eligible == []
    weak = FeatureEvidence("local_funds_cdd", named=True, mechanism_evidence=False)
    assert route(ProjectFacts(fcv_setting="active_conflict", features=(weak,)), CARDS).eligible == []


def test_fired_sector_still_needs_a_relevant_feature():
    res = route(ProjectFacts(instrument="IPF", pa_lead_parsed="Transport", fcv_setting="any"), CARDS)
    assert res.sectors == ["transport"] and res.eligible == []
    fe = FeatureEvidence("rural_feeder_roads", financing_share=0.9)
    res = route(ProjectFacts(instrument="IPF", pa_lead_parsed="Transport", fcv_setting="any", features=(fe,)), CARDS)
    assert res.eligible and all(e["route"] == "sector" for e in res.eligible)


def test_multi_country_features_must_be_country_scoped():
    fe = FeatureEvidence("agri_inputs_pastoral", financing_share=0.3, mechanism_evidence=True)
    base = {"instrument": "IPF", "pa_lead_parsed": "Agriculture and Food", "fcv_setting": "active_conflict", "multi_country": True}
    assert route(ProjectFacts(**base, features=(fe,)), CARDS).eligible == []
    scoped = FeatureEvidence("agri_inputs_pastoral", financing_share=0.3, mechanism_evidence=True, country="Chad")
    assert route(ProjectFacts(**base, features=(scoped,)), CARDS).eligible


def test_eligible_set_is_capped_and_overflow_is_traced():
    feats = tuple(FeatureEvidence(f, financing_share=0.2, named=True, mechanism_evidence=True) for f in
                  ("rural_feeder_roads", "water_points_wash", "nrm_landscape_forest", "agri_inputs_pastoral",
                   "ews_hydromet", "local_funds_cdd", "land_acquisition_tenure"))
    res = route(ProjectFacts(instrument="IPF", fcv_setting="active_conflict", features=feats), CARDS)
    assert len(res.eligible) == 6
    assert any("budget" in r["reason"] for r in res.rejected)


def test_dpf_prior_action_route():
    pas = ("Cabinet approved a new water tariff schedule with cost-recovery targets",
           "Parliament adopted the revised Land Code")
    res = route(ProjectFacts(instrument="DPF", fcv_setting="post_conflict", prior_actions=pas), CARDS)
    assert res.sectors == []
    assert set(res.eligible_ids) == {"mc-13", "mc-02"}
    assert all(e["route"] == "dpf_prior_action" for e in res.eligible)
    assert route(ProjectFacts(instrument="DPF", fcv_setting="any", prior_actions=pas), CARDS).eligible == []
    res = route(ProjectFacts(instrument="DPF", fcv_setting="active_conflict",
                             prior_actions=("Government adopted a decree phasing out fuel subsidies",)), CARDS)
    assert "mc-24" in res.eligible_ids


def test_cerc_only_routes_nothing():
    fe = FeatureEvidence("ews_hydromet", financing_share=1.0, named=True, mechanism_evidence=True)
    assert route(ProjectFacts(cerc_only=True, fcv_setting="active_conflict", features=(fe,)), CARDS).eligible == []


# --- parser on real test documents (skipped where the OneDrive folders are absent) --------------------------

_ONEDRIVE = Path("C:/Users/wb559324/OneDrive - WBG")
_ST = _ONEDRIVE / "fcv-project-screener/FCV_Screener_test_cases"
_AT = _ONEDRIVE / "Documents/Cowork/Tasks/wbg-project-documents-access-through-2026-06-22/output/WBG_Appraisal_TestCases"
REAL_DOCS = [
    (_ST / "Honduras/Project Appraisal Document (PAD) clean.pdf", "Transport"),
    (_ST / "Guinea - Water/BOSIB-2e1acf99-ec4d-4ffc-b49b-0c9ec31f74c2.pdf", "Water"),
    (_ST / "Guinea - Gov/BOSIB-dbb6f3f7-06bb-4d73-a6df-8c71eb7f7711.pdf", "Social Sustainability and Inclusion"),
    (_AT / "MPA/P178132_FSRP_Phase2/MPA_Regional_WCA_FSRP_Phase2_P178132_PAD.pdf", "Agriculture and Food"),
    (_AT / "PforR/P170419_Morocco_GreenGeneration/PforR_Morocco_GreenGeneration_P170419_PAD.pdf", "Agriculture and Food"),
    (_AT / "Multi-country MPA/MPA_Regional_ESA_ASCENT_P180547_PAD.pdf", "Energy & Extractives"),
    (_AT / "MPA/P173789_COVID19_SPRP/MPA_Global_COVID19_SPRP_P173789_PAD.pdf", "Other"),
    (_AT / "IPF/P179698_BREHS/IPF_Kenya_BREHS_P179698_PAD.pdf", "Health, Nutrition & Population"),
    (_AT / "PforR/P166868_India_STARS/PforR_India_STARS_P166868_PAD.pdf", "Education"),
    (_ST / "Sector_ENRM_EWS_2026-11/ENRM_Nigeria_ACReSAL_P175237_PAD_2021.pdf", "Environment, Natural Resources & the Blue Economy"),
    (_ST / "Sector_ENRM_EWS_2026-11/ENRM_Uganda_ProtectedAreas_P174337_ProjectPaper_2021.pdf", "Environment, Natural Resources & the Blue Economy"),
    (_ST / "Sector_ENRM_EWS_2026-11/ENRM_Yemen_RedSeaFisheries_P178143_PAD_2022.pdf", "Environment, Natural Resources & the Blue Economy"),
    (_ST / "Sector_ENRM_EWS_2026-11/EWS_Mali_ClimateResilience-Hydromet_P161406_PAD_2019.pdf", "Social, Urban, Rural and Resilience"),
    (_ST / "Sector_ENRM_EWS_2026-11/WAT-AGR_Somalia_WaterAgroPastoral_P167826_PAD_2019.pdf", "Water"),
]


@pytest.mark.parametrize("path, lead", REAL_DOCS, ids=[p.name[:40] for p, _ in REAL_DOCS])
def test_parser_on_real_documents(path, lead):
    if not path.exists():
        pytest.skip("test document not available on this machine")
    fitz = pytest.importorskip("fitz")
    doc = fitz.open(path)
    text = "\n".join(doc[i].get_text() for i in range(min(15, doc.page_count)))
    assert parse_practice_areas(text).lead == lead
