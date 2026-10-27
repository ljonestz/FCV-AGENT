"""Check or serve an isolated, explicitly UNAPPROVED country-bank app build.

Run from the repository root with ``python -m scripts.run_country_bank_test``.
Checking makes no provider calls. Serving binds only to loopback and preserves
the app's existing spend controls; it does not authorize a paid assessment.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from sector_lenses.climate_bank import (
    UNAPPROVED_TEST_ARTIFACT, load_climate_bank, materialize_bank_manifest,
)
from sector_lenses.climate_bank_selector import select_bank_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--serve', action='store_true')
    parser.add_argument('--port', type=int, default=5001)
    args = parser.parse_args(argv)
    try:
        raw = json.loads(args.bundle.read_text(encoding='utf-8'))
        if raw.get('artifact_kind') != UNAPPROVED_TEST_ARTIFACT:
            raise ValueError('not an unapproved test artifact')
    except (OSError, UnicodeError, ValueError, AttributeError) as exc:
        print(f'Test bank rejected: {exc}', file=sys.stderr)
        return 1
    settings = {
        'CLIMATE_COUNTRY_BANK_PATH': str(args.bundle.resolve()),
        'CLIMATE_COUNTRY_BANK_PREVIEW': 'unapproved-test',
        'FCV_APP_ENV': 'country-bank-test',
    }
    original = {k: os.environ.get(k) for k in settings}
    try:
        os.environ.update(settings)
        bank = load_climate_bank()
        if bank.status != 'ok' or not bank.draft_preview:
            print(f'Test bank rejected: {bank.warning_code}', file=sys.stderr)
            return 1
        failures = []
        for iso3 in sorted(bank.release['countries']):
            for sector, signals in (
                ('Agriculture', 'drought livelihoods displacement land tenure'),
                ('Water', 'flood water governance access'),
                ('Urban development', 'coastal heat informal settlements institutions'),
            ):
                manifest = select_bank_manifest(bank, country=iso3, country_scope='single',
                    resolved_country_count=1, sector=sector, project_signals=signals)
                packet = materialize_bank_manifest(bank, manifest)
                if packet.get('bank_status') != 'ok' or not packet.get('limitations'):
                    failures.append(f'{iso3}/{sector}: {packet.get("warning_code")}')
        if failures:
            print('\n'.join(failures), file=sys.stderr)
            return 1
        count = len(bank.release['countries'])
        print(f'UNAPPROVED: {count}/{count} countries select and materialize in three sectors. '
              f'Test artifact expires {bank.release["test_expires_on"]}. No provider calls made.')
        if not args.serve:
            return 0
        from app import app

        @app.after_request
        def test_build_notice(response):
            if response.mimetype == 'text/html':
                notice = (
                    '<div role="alert" style="padding:16px;background:#fff3cd;'
                    'color:#332600;border:3px solid #997400;font:16px sans-serif">'
                    '<strong>UNAPPROVED COUNTRY-BANK TEST BUILD.</strong> Draft evidence; '
                    'not for operational use. Production approvals are unchanged.</div>'
                )
                # The landing page uses send_file(), whose response is normally
                # passed through without buffering. This local-only banner edits
                # its body, so buffer it and discard stale file-cache validators.
                response.direct_passthrough = False
                body = response.get_data(as_text=True)
                if '<body' in body:
                    end = body.find('>', body.find('<body')) + 1
                    body = body[:end] + notice + body[end:]
                else:
                    body = notice + body
                response.set_data(body)
                response.headers.pop('ETag', None)
                response.headers.pop('Last-Modified', None)
                response.headers['Cache-Control'] = 'no-store'
            return response

        app.run(host='127.0.0.1', port=args.port, debug=False, use_reloader=False)
        return 0
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == '__main__':
    raise SystemExit(main())
