"""Regression tests for frontend request-timeout messaging."""

import re
import subprocess
from pathlib import Path


def _extract_js_function(source: str, name: str) -> str:
    match = re.search(rf"function\s+{name}\s*\(", source)
    assert match, f"Missing JS helper {name}()"
    start = match.start()
    brace = source.find("{", match.end())
    assert brace != -1, f"Missing body for {name}()"
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise AssertionError(f"Unterminated body for {name}()")


def test_custom_abort_error_message_is_treated_as_timeout():
    index_html = Path(__file__).resolve().parents[1] / "index.html"
    helper = _extract_js_function(
        index_html.read_text(encoding="utf-8"), "requestErrorMessage"
    )
    script = f"""
{helper}
const timeoutError = new Error('Stage 1 timed out after 9 minutes.');
const abortError = new DOMException('Request timed out', 'AbortError');
const networkError = new TypeError('Failed to fetch');

const timeoutMessage = requestErrorMessage(timeoutError, 'Could not reach the server.');
const abortMessage = requestErrorMessage(abortError, 'Could not reach the server.');
const networkMessage = requestErrorMessage(networkError, 'Could not reach the server.');

if (timeoutMessage !== 'Stage 1 timed out after 9 minutes.') {{
  throw new Error('custom timeout reason was not preserved: ' + timeoutMessage);
}}
if (abortMessage !== 'Request timed out') {{
  throw new Error('AbortError message was not preserved: ' + abortMessage);
}}
if (networkMessage !== 'Could not reach the server.') {{
  throw new Error('network fallback was not used: ' + networkMessage);
}}
"""
    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_payload_limit_message_tracks_published_backend_cap():
    index_html = Path(__file__).resolve().parents[1] / "index.html"
    helper = _extract_js_function(
        index_html.read_text(encoding="utf-8"), "uploadPayloadLimitMessage"
    )
    # A ~100 MiB upload (~133 MB base64) is blocked under the 50 MB fallback cap
    # but allowed once the backend publishes a 200 MB cap — proving the pre-submit
    # warning follows uploadLimitMb rather than a hard-coded threshold.
    script = f"""
let uploadLimitMb = 50;
{helper}
const oneMiB = 1024 * 1024;
const blockedAtDefault = uploadPayloadLimitMessage([{{ size: 100 * oneMiB }}], [], []);
if (!blockedAtDefault.includes('too large')) {{
  throw new Error('100 MiB should be blocked under the 50 MB fallback cap');
}}
uploadLimitMb = 200;
const allowedAtRaisedCap = uploadPayloadLimitMessage([{{ size: 100 * oneMiB }}], [], []);
if (allowedAtRaisedCap !== '') {{
  throw new Error('100 MiB should be allowed under a 200 MB cap: ' + allowedAtRaisedCap);
}}
"""
    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_payload_limit_message_blocks_large_base64_upload():
    index_html = Path(__file__).resolve().parents[1] / "index.html"
    helper = _extract_js_function(
        index_html.read_text(encoding="utf-8"), "uploadPayloadLimitMessage"
    )
    script = f"""
{helper}
const oneMiB = 1024 * 1024;
const small = uploadPayloadLimitMessage([{{ size: oneMiB }}], [], []);
const large = uploadPayloadLimitMessage([{{ size: 36 * oneMiB }}], [], []);

if (small !== '') {{
  throw new Error('small upload was blocked: ' + small);
}}
if (!large.includes('too large')) {{
  throw new Error('large upload was not blocked clearly: ' + large);
}}
if (!large.includes('base64')) {{
  throw new Error('large upload message should explain browser encoding: ' + large);
}}
"""
    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_md_groups_blank_line_separated_bullets_and_strips_stray_tokens():
    index_html = Path(__file__).resolve().parents[1] / "index.html"
    helper = _extract_js_function(index_html.read_text(encoding="utf-8"), "md")
    script = f"""
{helper}
const NL = String.fromCharCode(10);
const loose = md(["- **A:** foo", "- **B:** bar", "- **C:** baz"].join(NL + NL));
const ulCount = (loose.match(/<ul>/g) || []).length;
const liCount = (loose.match(/<li>/g) || []).length;
if (ulCount !== 1) {{ throw new Error("expected 1 <ul>, got " + ulCount); }}
if (liCount !== 3) {{ throw new Error("expected 3 <li>, got " + liCount); }}
const tok = md("para " + "%%%" + "RISK_NARRATIVE_START" + "%%%" + " tail");
if (tok.indexOf("%" + "%%") !== -1) {{ throw new Error("stray token not stripped: " + tok); }}
"""
    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
