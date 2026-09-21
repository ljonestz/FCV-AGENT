# Bounded Climate Evidence Handoff Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent completed Climate-FCV searches from failing when the structuring model receives or emits an oversized response.

**Architecture:** Add a pure adapter that converts Anthropic search-response blocks into a small trusted evidence packet. Use that packet in a fresh one-turn Haiku structuring request, preserving the existing Climate bundle schema and evidence gate while reporting truncation accurately.

**Tech Stack:** Python 3, Flask, Anthropic Messages API, pytest.

---

### Task 1: Define the bounded evidence-packet contract

**Files:**
- Modify: `tests/test_climate_research.py`
- Modify: `sector_lenses/research.py`
- Modify: `sector_lenses/__init__.py`

- [ ] **Step 1: Write the failing evidence-packet tests**

Add tests that build SDK-like text, citation, and tool-result objects containing
duplicate trusted URLs, an untrusted URL, encrypted content, and oversized note
text. Assert that `build_climate_evidence_packet(content, project_profile)`:

```python
packet = build_climate_evidence_packet(content, project_profile)
assert len(json.dumps(packet)) <= CLIMATE_EVIDENCE_PACKET_MAX_CHARS
assert packet["notes"]
assert [source["url"] for source in packet["sources"]] == [
    "https://www.worldbank.org/example-ccdr",
    "https://www.un.org/example-climate",
]
assert "encrypted-secret" not in json.dumps(packet)
assert packet["project_profile"]["document_excerpt"]
```

Also test dictionary-shaped blocks and missing metadata so the helper does not
depend on Anthropic SDK classes.

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
python -m pytest tests/test_climate_research.py -k "evidence_packet" -q
```

Expected: collection/import failure because
`build_climate_evidence_packet` and its bound do not exist.

- [ ] **Step 3: Implement the minimal pure helper**

In `sector_lenses/research.py`, add bounded constants and small access helpers,
then implement:

```python
def build_climate_evidence_packet(
    content: Any,
    project_profile: dict[str, Any],
) -> dict[str, Any]:
    """Convert search response blocks into bounded, trusted evidence."""
```

The implementation must:

- collect bounded text notes;
- inspect text citations and nested `web_search_tool_result` content;
- retain only `_trusted_https()` URLs;
- deduplicate by lowercase URL without a trailing slash;
- cap source count, title/date/excerpt lengths, note length, and serialized
  project-profile fields;
- omit encrypted content and unknown fields.

Export the helper and packet-size constant from `sector_lenses/__init__.py`.

- [ ] **Step 4: Run the tests and verify GREEN**

Run:

```powershell
python -m pytest tests/test_climate_research.py -k "evidence_packet" -q
```

Expected: all evidence-packet tests pass.

- [ ] **Step 5: Commit**

```powershell
git add -- sector_lenses/research.py sector_lenses/__init__.py tests/test_climate_research.py
git commit -m "feat: bound climate search evidence handoff"
```

### Task 2: Replace full-conversation replay

**Files:**
- Modify: `tests/test_climate_research.py`
- Modify: `app.py`

- [ ] **Step 1: Rewrite the structuring-call regression test**

Update `test_climate_research_structures_search_notes_without_researching` so
the simulated response includes very large tool-result/encrypted fields and two
trusted citations. Assert:

```python
recovery = client.calls[1]
assert [message["role"] for message in recovery["messages"]] == ["user"]
request_text = recovery["messages"][0]["content"]
assert "EVIDENCE PACKET" in request_text
assert "original-search-secret" not in request_text
assert "encrypted-secret" not in request_text
assert CLIMATE_RESEARCH_START in request_text
assert "four to six" in request_text.lower()
assert len(request_text) < 20_000
```

- [ ] **Step 2: Run the regression and verify RED**

Run:

```powershell
python -m pytest tests/test_climate_research.py::test_climate_research_structures_search_notes_without_researching -q
```

Expected: failure because the current request still has three conversation
messages and replays `response.content`.

- [ ] **Step 3: Implement the fresh structuring request**

Import `build_climate_evidence_packet` in `app.py`. In
`run_climate_web_research()`, build the packet after two completed search
results and call Haiku with:

```python
messages=[{
    "role": "user",
    "content": (
        "Do not search. Structure only the bounded evidence packet below.\n\n"
        "EVIDENCE PACKET:\n"
        + json.dumps(packet, ensure_ascii=False, separators=(",", ":"))
        + "\n\n"
        + build_climate_research_prompt(
            country, sector, packet["project_profile"], narrow=True
        )
    ),
}]
```

Do not pass the original search prompt, assistant tool blocks, or the complete
project profile into this call.

- [ ] **Step 4: Add content-free packet telemetry**

Extend the existing `structuring_search_results` log with packet characters,
source count, and a yes/no notes flag. Do not log packet content.

- [ ] **Step 5: Run the focused tests and verify GREEN**

Run:

```powershell
python -m pytest tests/test_climate_research.py -q
```

Expected: all Climate research tests pass.

- [ ] **Step 6: Commit**

```powershell
git add -- app.py tests/test_climate_research.py
git commit -m "fix: structure bounded climate evidence"
```

### Task 3: Report structuring truncation accurately

**Files:**
- Modify: `tests/test_climate_research.py`
- Modify: `sector_lenses/research.py`
- Modify: `app.py`

- [ ] **Step 1: Write failing truncation-message tests**

Add a test where the structuring response has `stop_reason="max_tokens"`, an
opening delimiter, and no closing delimiter. Assert that the returned failed
bundle contains:

```python
assert result["failure_reason"] == (
    "Climate evidence structuring was truncated before valid JSON completed."
)
decision = climate_research_evidence_gate(result)
assert "structured" in decision["message"].lower()
assert "two relevant sources" not in decision["message"].lower()
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
python -m pytest tests/test_climate_research.py -k "truncat and message" -q
```

Expected: failure because the current failed bundle has no
structuring-specific reason and uses the generic evidence-gate message.

- [ ] **Step 3: Implement the minimal error classification**

When the structuring response stops at `max_tokens` or has exactly one
delimiter, set the normalized bundle's failure reason to the string asserted
above. Update `climate_research_evidence_gate()` to return:

```python
"Climate-FCV web evidence was found but could not be structured into a "
"validated research bundle. Retry the climate assessment."
```

when that bounded failure reason is present.

- [ ] **Step 4: Run the tests and verify GREEN**

Run:

```powershell
python -m pytest tests/test_climate_research.py -q
```

Expected: all Climate research tests pass.

- [ ] **Step 5: Commit**

```powershell
git add -- app.py sector_lenses/research.py tests/test_climate_research.py
git commit -m "fix: distinguish climate structuring truncation"
```

### Task 4: Document and verify the change

**Files:**
- Modify: `CLAUDE.md`
- Modify: `docs/reference/reference_sector_lenses.md`

- [ ] **Step 1: Update architecture documentation**

Document that Sonnet search results cross into Haiku through the bounded
evidence-packet adapter, that raw tool blocks are not replayed, and that the
Climate bundle schema/evidence gate remain unchanged. This is Render-specific
provider plumbing and does not add an ITS parity-contract surface.

- [ ] **Step 2: Run focused and route-level verification**

Run:

```powershell
python -m pytest tests/test_climate_research.py tests/test_sector_lens_app_contract.py tests/test_climate_workflow_contract.py -q
python -m py_compile app.py sector_lenses/research.py
git diff --check
```

Expected: all tests pass, compilation succeeds, and the diff check is clean.

- [ ] **Step 3: Commit and push**

```powershell
git add -- CLAUDE.md docs/reference/reference_sector_lenses.md
git commit -m "docs: explain bounded climate evidence handoff"
git push origin HEAD:refs/heads/feat/climate-readout-redesign
```

- [ ] **Step 4: Verify on Render**

Wait for the new commit to become live. Upload
`Project Concept Note (PCN)_Draft_15_June 2026.docx`, select Climate-FCV and
Express mode, and verify:

- Stage 1 passes the mandatory Climate research gate;
- Render logs show a bounded packet and a complete structuring response;
- Stage 2 starts without `sector-lens Stage 2 prompt exceeded its token ceiling`;
- native Climate Stage 2 and Stage 3 complete, or any new failure is captured
  with its assessment ID and exact server diagnostic before further changes.
