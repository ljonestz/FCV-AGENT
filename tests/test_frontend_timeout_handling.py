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
