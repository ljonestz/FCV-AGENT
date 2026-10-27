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
from sector_lenses.climate_bank_selector import (
    CLIMATE_BANK_MAX_CHARS, select_bank_manifest,
)
from sector_lenses.climate_grounding import merge_climate_grounding


def _final_prompt_failure(packet: dict) -> str | None:
    """Check the final model-facing projection, not only its source packet."""

    merged = merge_climate_grounding(packet, {})
    prompt = merged.get("prompt_context", "")
    if not prompt or len(prompt) > 12_000:
        return "missing or over combined prompt budget"
    try:
        payload = json.loads(prompt)
    except (TypeError, json.JSONDecodeError):
        return "is not valid prompt JSON"
    bank = payload.get("bank")
    if not isinstance(bank, dict):
        return "has no bank object"
    serialized_bank = json.dumps(
        bank,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    if (
        len(serialized_bank) > CLIMATE_BANK_MAX_CHARS
        or merged.get("bank_character_count", CLIMATE_BANK_MAX_CHARS + 1)
        > CLIMATE_BANK_MAX_CHARS
        or merged.get("combined_character_count", 12_001) > 12_000
    ):
        return "exceeds bank or combined prompt budget"
    if bank.get("coverage_metadata_available") is not True:
        return "dropped coverage metadata"
    profile = bank.get("country_profile")
    if (
        not isinstance(profile, dict)
        or not isinstance(profile.get("coverage"), list)
        or not isinstance(profile.get("known_gaps"), list)
        or not profile["coverage"]
        or not profile["known_gaps"]
    ):
        return "dropped profile coverage or known gaps"
    if "complete national or population coverage" not in bank.get(
        "coverage_note", ""
    ):
        return "omitted the coverage limitation"

    source_index = {
        item.get("source_id"): item
        for item in bank.get("sources", [])
        if isinstance(item, dict) and isinstance(item.get("source_id"), str)
    }
    original_sources = {
        item.get("source_id"): item
        for item in packet.get("sources", [])
        if isinstance(item, dict) and isinstance(item.get("source_id"), str)
    }
    original_evidence = {
        item.get("evidence_id"): item
        for item in packet.get("evidence_records", [])
        if isinstance(item, dict) and isinstance(item.get("evidence_id"), str)
    }
    retained_ids: set[str] = set()
    qualifier_fields = (
        "compact_statement", "evidence_status", "evidence_class",
        "analytical_role", "scenario", "time_horizons", "confidence",
        "uncertainty", "interaction_direction", "geographies",
        "affected_groups", "administrative_level", "ecological_level",
        "source_refs",
    )
    for item in bank.get("evidence_records", []):
        evidence_id = item.get("evidence_id")
        original = original_evidence.get(evidence_id)
        if not isinstance(original, dict):
            return "contains evidence without a canonical source record"
        retained_ids.add(evidence_id)
        if any(
            field not in item or item[field] != original.get(field)
            for field in qualifier_fields
            if field in original
        ):
            return f"lost a qualifier on {evidence_id}"
        for ref in item.get("source_refs", []):
            source_id = ref.get("source_id") if isinstance(ref, dict) else None
            source = source_index.get(source_id)
            original_source = original_sources.get(source_id)
            if not source or not original_source or not ref.get("locator"):
                return f"lost source support for {evidence_id}"
            if any(
                source.get(field) != original_source.get(field)
                for field in (
                    "title", "organization", "publication_date",
                    "publication_date_basis", "url",
                )
                if field in original_source
            ):
                return f"lost source metadata for {evidence_id}"
    original_pathways = {
        item.get("pathway_id"): item
        for item in packet.get("pathways", [])
        if isinstance(item, dict) and isinstance(item.get("pathway_id"), str)
    }
    pathway_fields = (
        "compact_statement", "evidence_strength", "supporting_evidence_ids",
        "interaction_direction", "geographies", "affected_groups",
        "alternative_explanations", "uncertainty",
    )
    for pathway in bank.get("pathways", []):
        pathway_id = pathway.get("pathway_id")
        original = original_pathways.get(pathway_id)
        supporting = pathway.get("supporting_evidence_ids")
        if not isinstance(original, dict) or any(
            field not in pathway or pathway[field] != original.get(field)
            for field in pathway_fields
            if field in original
        ):
            return f"lost a qualifier on {pathway_id}"
        if not isinstance(supporting, list) or not set(supporting).issubset(
            retained_ids
        ):
            return "contains a pathway without all supporting evidence"
    if not bank.get("pathways") and "does not establish" not in bank.get(
        "pathway_coverage_note", ""
    ):
        return "omitted the empty-pathway limitation"
    return None


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
        resolution_checks = 0
        resolved_aliases = set()
        for country in bank.release['countries'].values():
            expected_iso3 = country.get('iso3')
            identifiers = [
                expected_iso3,
                country.get('name'),
                *(
                    country.get('aliases', [])
                    if isinstance(country.get('aliases', []), list)
                    else []
                ),
            ]
            for identifier in identifiers:
                if not isinstance(identifier, str) or not identifier.strip():
                    continue
                key = (expected_iso3, identifier.strip().casefold())
                if key in resolved_aliases:
                    continue
                resolved_aliases.add(key)
                resolved = bank.resolve_country(identifier)
                if not resolved or resolved.get('iso3') != expected_iso3:
                    failures.append(
                        f'{expected_iso3}/{identifier}: country resolution mismatch'
                    )
                else:
                    resolution_checks += 1
        prompt_checks = 0
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
                    continue
                prompt_failure = _final_prompt_failure(packet)
                if prompt_failure:
                    failures.append(f'{iso3}/{sector}: final prompt {prompt_failure}')
                else:
                    prompt_checks += 1
        if failures:
            print('\n'.join(failures), file=sys.stderr)
            return 1
        count = len(bank.release['countries'])
        print(f'UNAPPROVED: {count}/{count} countries select and materialize in three sectors. '
              f'Test artifact expires {bank.release["test_expires_on"]}. No provider calls made.')
        print(f'Country/name/alias resolutions: {resolution_checks} unique identifiers checked.')
        print(f'Final prompt checks: {count} country x 3 sectors ({prompt_checks} prompts); '
              f'qualifiers, source locators, and coverage verified.')
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
