"""The test launcher checks real selection without importing the paid app runtime."""

import json
from pathlib import Path

import pytest

from scripts.run_country_bank_test import main


FIXTURE = Path(__file__).parent / 'fixtures/climate_bank/runtime_v1_1_candidate.json'


def draft_bundle(tmp_path):
    from datetime import date, timedelta

    release = json.loads(FIXTURE.read_text(encoding='utf-8'))
    release.update(artifact_kind='unapproved-country-bank-test',
                   generated_at=date.today().isoformat() + 'T00:00:00Z',
                   test_expires_on=(date.today() + timedelta(days=1)).isoformat())
    for c in release['countries'].values():
        c.update(status='draft', reviewer=None, reviewed_on=None, review_due=None)
    for r in release['evidence_records'] + release['pathways']:
        r.update(review_status='draft', review_date=None)
    release['country_profiles'] = {
        'SSD': {
            'coverage': [{'dimension': 'geographic', 'covered': ['Jonglei']}],
            'known_gaps': ['No county population denominator.'],
        }
    }
    path = tmp_path / 'test.json'
    path.write_text(json.dumps(release), encoding='utf-8')
    return path


def test_launcher_check_does_not_import_app_or_call_provider(tmp_path, monkeypatch, capsys):
    import sys

    path = draft_bundle(tmp_path)
    # Importing Flask's app would start application setup; checking needs none of it.
    monkeypatch.setitem(sys.modules, 'app', None)
    for key in ('CLIMATE_COUNTRY_BANK_PATH', 'CLIMATE_COUNTRY_BANK_PREVIEW', 'FCV_APP_ENV'):
        monkeypatch.delenv(key, raising=False)
    assert main(['--bundle', str(path), '--check']) == 0
    output = capsys.readouterr().out
    assert 'UNAPPROVED' in output and '1/1' in output


def test_launcher_rejects_reviewed_release(tmp_path, capsys):
    assert main(['--bundle', str(FIXTURE), '--check']) == 1
    assert 'not an unapproved test artifact' in capsys.readouterr().err


def test_served_build_is_loopback_only_and_visibly_unapproved(tmp_path, monkeypatch):
    import sys
    from types import SimpleNamespace
    from flask import Flask, Response, send_file

    app = Flask('isolated-bank-test')
    landing = tmp_path / 'landing.html'
    landing.write_text('<html><body>Static landing page</body></html>', encoding='utf-8')

    @app.get('/')
    def home():
        return '<html><body>Original app page</body></html>'

    @app.get('/binary')
    def binary():
        return Response(b'unchanged-export', mimetype='application/octet-stream')

    @app.get('/static-page')
    def static_page():
        return send_file(landing)

    def run(**kwargs):
        assert kwargs == dict(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
        client = app.test_client()
        text = client.get('/').get_data(as_text=True)
        assert '<body><div role="alert"' in text
        assert 'UNAPPROVED COUNTRY-BANK TEST BUILD' in text
        assert 'Original app page' in text
        assert client.get('/binary').data == b'unchanged-export'
        response = client.get('/static-page')
        assert response.status_code == 200
        assert 'UNAPPROVED COUNTRY-BANK TEST BUILD' in response.get_data(as_text=True)
        assert 'Static landing page' in response.get_data(as_text=True)
        assert response.headers['Cache-Control'] == 'no-store'
        assert 'ETag' not in response.headers
        assert 'Last-Modified' not in response.headers

    monkeypatch.setattr(app, 'run', run)
    monkeypatch.setitem(sys.modules, 'app', SimpleNamespace(app=app))
    assert main(['--bundle', str(draft_bundle(tmp_path)), '--serve']) == 0


def test_launcher_checks_final_merged_prompt_qualifiers_and_coverage(
    tmp_path, monkeypatch, capsys
):
    path = draft_bundle(tmp_path)
    for key in ('CLIMATE_COUNTRY_BANK_PATH', 'CLIMATE_COUNTRY_BANK_PREVIEW', 'FCV_APP_ENV'):
        monkeypatch.delenv(key, raising=False)

    assert main(['--bundle', str(path), '--check']) == 0
    output = capsys.readouterr().out
    assert 'Final prompt checks: 1 country x 3 sectors' in output
    assert 'qualifiers, source locators, and coverage verified' in output
    assert 'Country/name/alias resolutions: 3 unique identifiers checked' in output


@pytest.mark.parametrize('field', ['coverage', 'known_gaps'])
def test_launcher_rejects_empty_final_profile_sections(
    tmp_path, monkeypatch, capsys, field
):
    import scripts.run_country_bank_test as launcher

    original_merge = launcher.merge_climate_grounding

    def drop_profile_section(packet, external):
        merged = original_merge(packet, external)
        payload = json.loads(merged['prompt_context'])
        payload['bank']['country_profile'][field] = []
        merged['prompt_context'] = json.dumps(payload, separators=(',', ':'))
        return merged

    monkeypatch.setattr(launcher, 'merge_climate_grounding', drop_profile_section)
    assert main(['--bundle', str(draft_bundle(tmp_path)), '--check']) == 1
    assert 'profile coverage or known gaps' in capsys.readouterr().err
