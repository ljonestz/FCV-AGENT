"""Approved-release and freshness contracts; all content is synthetic."""

import json
from datetime import date
from pathlib import Path

import pytest

from sector_lenses.climate_bank import load_climate_bank, materialize_bank_manifest
from sector_lenses.climate_bank_selector import select_bank_manifest, compact_bank_packet
from sector_lenses.climate_grounding import merge_climate_grounding
from sector_lenses.climate_context_adapter import adapt_grounding_evidence


FIXTURE = Path(__file__).parent / 'fixtures/climate_bank/runtime_v1_1_candidate.json'


def approved_release():
    release = json.loads(FIXTURE.read_text(encoding='utf-8'))
    release['candidate'] = False
    release['countries']['SSD']['status'] = 'approved'
    for record in release['evidence_records'] + release['pathways']:
        record['review_status'] = 'approved'
    return release


def load(tmp_path, release):
    path = tmp_path / 'runtime.json'
    path.write_text(json.dumps(release), encoding='utf-8')
    return load_climate_bank(path)


def manifest(**changes):
    return {
        'country_iso3': 'SSD', 'content_version': 'test-1-preview',
        'evidence_ids': ['SSD-E-001'], 'pathway_ids': ['SSD-P-001'],
        **changes,
    }


def select(bank):
    return select_bank_manifest(
        bank, country='South Sudan', country_scope='single',
        resolved_country_count=1, sector='Fisheries',
        project_signals='Jonglei fisheries seasonal flooding',
    )


def test_approved_v11_materializes_without_preview(tmp_path, monkeypatch):
    monkeypatch.delenv('CLIMATE_COUNTRY_BANK_PREVIEW', raising=False)
    bank = load(tmp_path, approved_release())
    assert bank.status == 'ok'
    assert bank.candidate_preview is False
    packet = materialize_bank_manifest(bank, manifest())
    assert packet['bank_status'] == 'ok'
    assert packet['evidence_records'][0]['evidence_class'] == 'climate-pressure'
    assert 'candidate_preview' not in packet


@pytest.mark.parametrize('field', ['evidence_class', 'review_due', 'refresh_tier'])
def test_approved_v11_still_requires_v11_fields(tmp_path, field):
    release = approved_release()
    del release['evidence_records'][0][field]
    packet = materialize_bank_manifest(load(tmp_path, release), manifest())
    assert packet['warning_code'] == 'bank_manifest_invalid'


@pytest.mark.parametrize('kind', ['country', 'evidence', 'pathway'])
def test_reviewed_content_never_enters_approved_packet(tmp_path, kind, monkeypatch):
    release = approved_release()
    if kind == 'country':
        release['countries']['SSD']['status'] = 'reviewed'
    else:
        release['evidence_records' if kind == 'evidence' else 'pathways'][0]['review_status'] = 'reviewed'
    monkeypatch.setenv('CLIMATE_COUNTRY_BANK_PREVIEW', 'reviewed-candidate')
    packet = materialize_bank_manifest(load(tmp_path, release), manifest())
    assert packet['warning_code'] == (
        'bank_country_unapproved' if kind == 'country' else 'bank_manifest_invalid'
    )
    assert set(packet) == {'bank_status', 'warning_code'}


@pytest.mark.parametrize('flag', [True, None, 'false', 0])
def test_v11_requires_explicit_false_candidate_in_production(tmp_path, flag):
    release = approved_release()
    release['candidate'] = flag
    assert load(tmp_path, release).warning_code == 'bank_incompatible'


def test_v10_cannot_bypass_preview_policy_with_candidate_flag(tmp_path):
    release = json.loads(FIXTURE.with_name('runtime_v1.json').read_text(encoding='utf-8'))
    release['candidate'] = True
    assert load(tmp_path, release).warning_code == 'bank_incompatible'


@pytest.mark.parametrize('pathways_only', [False, True])
def test_expired_current_record_rejected_including_indirect_support(tmp_path, pathways_only):
    release = approved_release()
    release['evidence_records'][0].update(refresh_tier='current', review_due='2020-01-01')
    packet = materialize_bank_manifest(
        load(tmp_path, release), manifest(evidence_ids=[] if pathways_only else ['SSD-E-001']),
    )
    assert packet == {'bank_status': 'unavailable', 'warning_code': 'bank_content_expired'}


def test_expiry_on_today_is_still_valid(tmp_path):
    release = approved_release()
    release['evidence_records'][0].update(refresh_tier='current', review_due=date.today().isoformat())
    assert materialize_bank_manifest(load(tmp_path, release), manifest())['bank_status'] == 'ok'


def test_selection_preserves_structural_fallback_and_discloses_omission(tmp_path):
    release = approved_release()
    release['evidence_records'][0].update(refresh_tier='current', review_due='2020-01-01')
    bank = load(tmp_path, release)
    selected = select(bank)
    assert selected['bank_status'] == 'ok'
    assert selected['evidence_ids'] == ['SSD-E-002']
    assert selected['pathway_ids'] == []
    packet = materialize_bank_manifest(bank, selected)
    assert packet['limitations']
    assert compact_bank_packet(packet)['limitations'] == packet['limitations']
    grounding = merge_climate_grounding(packet, {})
    assert grounding['state'] == 'bank-only'
    assert json.loads(grounding['prompt_context'])['bank']['limitations'] == packet['limitations']
    assert grounding['bank_character_count'] <= 6000
    context = adapt_grounding_evidence(grounding)
    assert context
    assert all(item.evidence_gap == packet['limitations'][0] for item in context)


def test_all_current_content_expired_returns_expiry_reason(tmp_path):
    release = approved_release()
    for record in release['evidence_records']:
        record.update(refresh_tier='current', review_due='2020-01-01')
    bank = load(tmp_path, release)
    selected = select(bank)
    assert selected == {'bank_status': 'unavailable', 'warning_code': 'bank_content_expired'}
    assert materialize_bank_manifest(bank, selected) == selected


def test_current_expiry_is_also_enforced_in_preview(tmp_path, monkeypatch):
    release = json.loads(FIXTURE.read_text(encoding='utf-8'))
    release['evidence_records'][0].update(refresh_tier='current', review_due='2020-01-01')
    path = tmp_path / 'preview.json'
    path.write_text(json.dumps(release), encoding='utf-8')
    monkeypatch.setenv('CLIMATE_COUNTRY_BANK_PATH', str(path))
    monkeypatch.setenv('CLIMATE_COUNTRY_BANK_PREVIEW', 'reviewed-candidate')
    bank = load_climate_bank()
    selected = select(bank)
    assert selected['candidate_preview'] is True
    assert selected['evidence_ids'] == ['SSD-E-002']
    assert selected['pathway_ids'] == []
