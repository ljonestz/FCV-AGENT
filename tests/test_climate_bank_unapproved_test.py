"""Draft content is usable only in an explicitly isolated local test build."""

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from sector_lenses.climate_bank import load_climate_bank, materialize_bank_manifest
from sector_lenses.climate_bank_selector import select_bank_manifest, compact_bank_packet
from sector_lenses.climate_grounding import merge_climate_grounding
from sector_lenses.climate_context_adapter import adapt_grounding_evidence


FIXTURE = Path(__file__).parent / 'fixtures/climate_bank/runtime_v1_1_candidate.json'


@pytest.fixture
def draft(tmp_path, monkeypatch):
    release = json.loads(FIXTURE.read_text(encoding='utf-8'))
    release.update(artifact_kind='unapproved-country-bank-test',
                   generated_at=date.today().isoformat() + 'T00:00:00Z',
                   test_expires_on=(date.today() + timedelta(days=1)).isoformat())
    for country in release['countries'].values():
        country.update(status='draft', reviewer=None, reviewed_on=None, review_due=None)
    for record in release['evidence_records'] + release['pathways']:
        record.update(review_status='draft', review_date=None)
    path = tmp_path / 'draft.json'
    path.write_text(json.dumps(release), encoding='utf-8')
    monkeypatch.setenv('CLIMATE_COUNTRY_BANK_PATH', str(path))
    monkeypatch.delenv('CLIMATE_COUNTRY_BANK_PREVIEW', raising=False)
    monkeypatch.delenv('FCV_APP_ENV', raising=False)
    return path, release


@pytest.mark.parametrize('token,environment', [
    ('', ''), ('reviewed-candidate', ''), ('reviewed-candidate', 'country-bank-test'),
    ('unapproved-test', ''), ('unapproved-test', 'production'),
])
def test_draft_denied_outside_isolated_test(draft, monkeypatch, token, environment):
    monkeypatch.setenv('CLIMATE_COUNTRY_BANK_PREVIEW', token)
    monkeypatch.setenv('FCV_APP_ENV', environment)
    assert load_climate_bank().warning_code == 'bank_incompatible'


def opt_in(monkeypatch):
    monkeypatch.setenv('CLIMATE_COUNTRY_BANK_PREVIEW', 'unapproved-test')
    monkeypatch.setenv('FCV_APP_ENV', 'country-bank-test')


def select(bank):
    return select_bank_manifest(bank, country='SSD', country_scope='single',
                                resolved_country_count=1, sector='Fisheries',
                                project_signals='Jonglei flooding livelihoods')


def test_draft_preserves_real_status_and_warning_through_grounding(draft, monkeypatch):
    opt_in(monkeypatch)
    bank = load_climate_bank()
    assert bank.status == 'ok'
    assert bank.draft_preview and bank.candidate_preview
    assert bank.release['countries']['SSD']['reviewed_on'] is None
    selected = select(bank)
    assert selected['candidate_preview'] is True
    packet = materialize_bank_manifest(bank, selected)
    assert packet['bank_status'] == 'ok'
    assert packet['reviewed_on'] is None
    assert all(r['review_status'] == 'draft' and r['review_date'] is None
               for r in packet['evidence_records'] + packet['pathways'])
    assert 'UNAPPROVED' in packet['limitations'][0]
    assert compact_bank_packet(packet)['limitations'] == packet['limitations']
    grounding = merge_climate_grounding(packet, {})
    context = adapt_grounding_evidence(grounding)
    assert context and all(c.preview_status == 'preview; not approved' for c in context)
    assert all('UNAPPROVED' in c.evidence_gap for c in context)
    assert grounding['bank_character_count'] <= 6000


def test_explicit_path_cannot_authorize_drafts(draft, monkeypatch):
    opt_in(monkeypatch)
    assert load_climate_bank(draft[0]).warning_code == 'bank_incompatible'


@pytest.mark.parametrize('changes', [
    {'candidate': False}, {'schema_version': '1.0.0'},
    {'test_expires_on': '2000-01-01'}, {'test_expires_on': None},
    {'test_expires_on': '2099-01-01'}, {'generated_at': 'invalid'},
])
def test_test_bundle_cannot_masquerade_as_production(draft, monkeypatch, changes):
    opt_in(monkeypatch)
    path, release = draft
    release.update(changes)
    path.write_text(json.dumps(release), encoding='utf-8')
    assert load_climate_bank().warning_code == 'bank_incompatible'


def test_draft_cannot_claim_a_review_date(draft, monkeypatch):
    opt_in(monkeypatch)
    path, release = draft
    for record in release['evidence_records'] + release['pathways']:
        record['review_date'] = date.today().isoformat()
    path.write_text(json.dumps(release), encoding='utf-8')
    assert select(load_climate_bank())['bank_status'] == 'unavailable'


def test_draft_current_record_freshness_still_enforced(draft, monkeypatch):
    opt_in(monkeypatch)
    path, release = draft
    release['evidence_records'][0].update(refresh_tier='current', review_due='2000-01-01')
    path.write_text(json.dumps(release), encoding='utf-8')
    selected = select(load_climate_bank())
    assert selected['evidence_ids'] == ['SSD-E-002']
    assert selected['pathway_ids'] == []
