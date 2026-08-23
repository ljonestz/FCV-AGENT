# Climate and FCV Summary and Extraction Production Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Climate Summary a standalone synthesis, align safe follow-up content across Climate and main FCV, and reliably extract labelled metadata from modern DOCX templates without false instrument classifications.

**Architecture:** Add one shared OOXML traversal module and route both existing DOCX consumers through it. Extend the existing verified Climate judgment payload with a structured Summary paragraph bundle, normalize it into the canonical reader, and render follow-up information from that reader in both concise and detailed views. Preserve the existing main-FCV concise narrative and add only a conditional disclosure sourced from its normalized watch collections.

**Tech Stack:** Python 3.13, Flask, python-docx/lxml OOXML, pytest, vanilla JavaScript/CSS, Node-based frontend contract tests, Playwright/browser smoke checks.

---

## File map

- Create `docx_structure.py`: shared ordered OOXML traversal, visible-text filtering, table field/value pairing, and checkbox-state filtering.
- Modify `app.py`: replace its private top-level-only DOCX loop with the shared extractor while retaining the public `(text, part_count)` return contract.
- Modify `sector_lenses/climate_source_blocks.py`: build stable evidence blocks from the same ordered units and expose paired structured metadata as one block.
- Modify `sector_lenses/climate_verified_runtime.py`: prioritize explicit labelled financing metadata and avoid treating unselected options as instrument or MPA evidence.
- Modify `sector_lenses/climate_verified_prompts.py`, `sector_lenses/climate_verified_schemas.py`, and `sector_lenses/climate_verified_pipeline.py`: generate and admit the Climate `summary_overview.paragraphs` bundle in the existing judgment call.
- Modify `sector_lenses/climate_verified_render.py`: normalize Summary paragraphs, deterministic legacy fallback, source-supported guidance wording, and reader/export parity.
- Modify `index.html`: render the Climate synthesis, follow-up disclosures, purpose-led Detailed bands, accessible routing language, and the normal-FCV watch disclosure.
- Modify focused tests under `tests/`: prove each behavior red then green before moving to the next task.
- Modify `CLAUDE.md`, relevant `docs/reference/` files, and the private parity log: record only the final shared contracts.

### Task 1: Shared content-control and nested-table DOCX extraction

**Files:**
- Create: `docx_structure.py`
- Modify: `app.py:7207-7245`
- Modify: `sector_lenses/climate_source_blocks.py:50-145`
- Modify: `sector_lenses/climate_verified_runtime.py:100-270`
- Create: `tests/test_docx_structure.py`
- Modify: `tests/test_climate_source_blocks.py`
- Modify: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write failing realistic OOXML tests**

Create a small DOCX in memory with `w:sdt/w:sdtContent`, an outer table, a nested Basic Information table, and rows for Operation ID, Financing Instrument, and Environmental and Social Risk Classification. Include `[ ] Multiphase Programmatic Approach (MPA)` elsewhere. Assertions must require:

```python
assert "P511185" in extracted
assert "Financing Instrument: Investment Project Financing (IPF)" in extracted
assert "Environmental and Social Risk Classification: Substantial" in extracted
assert "Multiphase Programmatic Approach" not in extracted
assert context.instrument_type == "IPF"
assert context.is_mpa is False
assert context.es_regime == "UNRESOLVED"
```

Also assert stable source-block IDs, document order, no nested-table duplication, hidden/instruction/deleted text exclusion, checked `[x]` retention, and safe conflict behavior for two incompatible labelled financing values.

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```powershell
python -m pytest tests/test_docx_structure.py tests/test_climate_source_blocks.py tests/test_sector_lens_app_contract.py -q
```

Expected: the new SDT/nested-table assertions fail because current traversal sees only direct body paragraphs and tables; the unchecked MPA case either leaks or the structured financing row is absent.

- [ ] **Step 3: Implement the minimal shared traversal**

Use a focused result type rather than returning raw XML:

```python
@dataclass(frozen=True)
class DocxUnit:
    text: str
    kind: str
    paragraph_index: int | None = None
    table_coordinates: tuple[int, ...] | None = None
    heading_level: int | None = None
    field_name: str = ""
    field_value: str = ""


def extract_docx_units(document: Document) -> list[DocxUnit]:
    """Return visible reader content once, in document order."""
```

The recursive walker must descend through `w:sdtContent`, `w:tbl`, `w:tr`, and `w:tc` while emitting leaf paragraphs and paired table rows once. Normalize Word checkbox states and bracket forms before classification. Do not emit the label of an unchecked option as positive reader text. When a row has recognizable labels and a following value row, emit canonical pairs such as `Financing Instrument: Investment Project Financing (IPF)`.

Adapt `extract_docx_text()` to join the unit texts and keep its two-value return API. Adapt `build_docx_blocks()` to use unit location metadata when creating hashes and coordinates. In `resolve_verified_operation_context()`, first inspect explicit `Financing Instrument:` records; accept one unambiguous normalized value, fail closed on conflicting labelled values, and use existing narrative heuristics only when structured metadata is absent.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run the command from Step 2. Expected: all selected tests pass, including the unchanged simple paragraph/table and hidden-run tests.

- [ ] **Step 5: Commit the extraction checkpoint**

```powershell
git add -- docx_structure.py app.py sector_lenses/climate_source_blocks.py sector_lenses/climate_verified_runtime.py tests/test_docx_structure.py tests/test_climate_source_blocks.py tests/test_sector_lens_app_contract.py
git commit -m "fix: extract structured metadata from modern docx templates"
```

### Task 2: Dedicated verified Climate Summary synthesis

**Files:**
- Modify: `sector_lenses/climate_verified_prompts.py:139-205`
- Modify: `sector_lenses/climate_verified_schemas.py:350-375`
- Modify: `sector_lenses/climate_verified_pipeline.py:950-1390`
- Modify: `sector_lenses/climate_verified_render.py:500-650`
- Modify: `tests/test_climate_verified_client.py`
- Modify: `tests/test_climate_verified_pipeline.py`
- Modify: `tests/test_climate_verified_render.py`

- [ ] **Step 1: Write failing schema, pipeline, and reader tests**

Require the existing judgment call to return:

```python
"summary_overview": {
    "paragraphs": [
        "Verdict and foundation.",
        "Four-dimensional assessment.",
        "Practical implication and bridge."
    ]
}
```

Tests must prove two or three strings are admitted, blank/one/four-paragraph bundles fail validation, all four dimensions are mentioned across the bundle, the reader carries the normalized array, and the legacy fallback derives only from `overview_summary` plus validated rating rationales. Add a regression asserting no fallback paragraph is a prefix or slice of `executive_readout`.

- [ ] **Step 2: Run tests and verify RED**

```powershell
python -m pytest tests/test_climate_verified_client.py tests/test_climate_verified_pipeline.py tests/test_climate_verified_render.py -q
```

Expected: failures show `summary_overview` is absent from the schema/prompt/pipeline/reader.

- [ ] **Step 3: Extend the existing one-call contract and reader normalization**

Add the object to the judgment schema and prompt. The prompt requires 160–230 words, two or three paragraphs, the three approved narrative jobs, and explicit relevance/sensitivity/responsiveness/operationalization coverage. It must forbid copying the executive opening and forbid new facts or actions.

Normalize with a small helper:

```python
def _summary_overview_paragraphs(value: object) -> list[str]:
    mapping = _mapping(value)
    paragraphs = [_text(item) for item in mapping.get("paragraphs", [])]
    paragraphs = [item for item in paragraphs if item]
    return paragraphs if len(paragraphs) in {2, 3} else []
```

When new content fails, construct a bounded two-paragraph reader fallback by splitting `overview_summary` and the verified four rating rationales at sentence boundaries. Never read from `executive_readout` in that fallback. Store only escaped plain strings; emphasis belongs to the frontend.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run Step 2 again. Expected: all selected tests pass with no repair or second model call.

- [ ] **Step 5: Commit the synthesis checkpoint**

```powershell
git add -- sector_lenses/climate_verified_prompts.py sector_lenses/climate_verified_schemas.py sector_lenses/climate_verified_pipeline.py sector_lenses/climate_verified_render.py tests/test_climate_verified_client.py tests/test_climate_verified_pipeline.py tests/test_climate_verified_render.py
git commit -m "feat: add standalone climate summary synthesis"
```

### Task 3: Climate follow-up hierarchy, safe guidance, and concise rendering

**Files:**
- Modify: `sector_lenses/climate_verified_render.py:300-370, 840-1180`
- Modify: `index.html:463-525, 4760-5050, 6400-6500`
- Modify: `tests/test_climate_verified_render.py`
- Modify: `tests/test_climate_lens_frontend.py`
- Modify: `tests/test_concise_stage3_contract.py`
- Modify: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write failing backend and frontend contract tests**

Require guidance items to retain only a curated purpose sentence:

```python
assert item["project_use"] == (
    "Use this source to assess how environmental and natural-resource "
    "governance can reduce conflict risk."
)
assert "For this project" not in item["project_use"]
```

Require the Climate Summary to use `summary_overview.paragraphs`, render every first sentence in `<strong>`, escape markup, and contain two initially closed native disclosures named “What to keep an eye on” and “Relevant WBG guidance for this project.” Require the Detailed output to use distinct `climate-decision-preparation` and `climate-further-guidance` purpose classes and retain equivalent static/export content. Add a route-warning assertion for accessible wording rather than “legacy transitional” or “UNRESOLVED.”

- [ ] **Step 2: Run tests and verify RED**

```powershell
python -m pytest tests/test_climate_verified_render.py tests/test_climate_lens_frontend.py tests/test_concise_stage3_contract.py tests/test_sector_lens_app_contract.py -q
```

Expected: current Summary still slices `executive_readout`, guidance still appends generated project-specific text, and the purpose-led sections/disclosures do not exist.

- [ ] **Step 3: Implement the minimal canonical rendering changes**

Replace the executive slicing block in `renderClimateVerifiedSummary()` with paragraph rendering from `r.summary_overview.paragraphs`. Use a shared escaped first-sentence helper:

```javascript
function boldEscapedFirstSentence(value){
  const text=String(value||'').trim();
  const match=text.match(/^(.+?[.!?](?:["')\]]+)?)(\s+)([\s\S]*)$/);
  return match?`<strong>${esc(match[1])}</strong>${esc(match[2]+match[3])}`:`<strong>${esc(text)}</strong>`;
}
```

Build Summary watch items from canonical `core_questions[].watch`, preserving order and removing normalized duplicates. Reuse the canonical `guidance_items`; do not reconstruct more-specific wording in JavaScript. Add closed `<details>` elements with semantic summaries and visible focus states.

Wrap Detailed points-to-check content in the amber decision-preparation class and guidance in the teal further-guidance class. Color is supplementary to headings and explanatory text. Translate internal route values into plain labels and show a plain withholding explanation only when needed.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run Step 2 again. Expected: all selected tests pass, Summary contains no executive slice, and both reader surfaces use the canonical guidance collection.

- [ ] **Step 5: Commit the Climate reader checkpoint**

```powershell
git add -- sector_lenses/climate_verified_render.py index.html tests/test_climate_verified_render.py tests/test_climate_lens_frontend.py tests/test_concise_stage3_contract.py tests/test_sector_lens_app_contract.py
git commit -m "feat: align climate summary and follow-up sections"
```

### Task 4: Conditional main-FCV watch disclosure

**Files:**
- Modify: `index.html:3270-3350, 3930-4300, 6170-6350`
- Modify: `tests/test_concise_stage3_contract.py`

- [ ] **Step 1: Write failing normal-FCV disclosure tests**

Extract the planned helper with the existing Node harness and assert:

```javascript
const groups=normalFcvWatchGroups();
if(groups.length!==2)throw new Error('missing applicable groups');
if(!html.includes('What to keep an eye on'))throw new Error('missing disclosure');
if(html.includes('Relevant WBG guidance'))throw new Error('invented global guidance');
```

Cover empty omission, AF-only mid-cycle visibility, DPF/PforR/regional labels, stable deduplication, HTML escaping, closed initial state, and persistence/restoration of the watch arrays needed by Summary. Assert the pre-existing headline, overview, strengths, transitions, priorities, and closing remain byte-for-byte in their established order.

- [ ] **Step 2: Run tests and verify RED**

```powershell
python -m pytest tests/test_concise_stage3_contract.py -q
```

Expected: the conditional disclosure/helper is absent.

- [ ] **Step 3: Add the minimal disclosure without changing narrative generation**

Implement normalized stable deduplication across `midCycleWatch`, `dpfWatch`, `p4rWatch`, `regionalWatch`, and `horizonConsiderations`. Return labelled groups only for non-empty arrays applicable to the current result. Render one closed native `<details class="normal-fcv-watch-disclosure">` between the priority accordion and closing. Do not aggregate “Go Deeper” references or add another guidance control.

Ensure session and Express persistence retain these watch arrays wherever Stage 3 state is retained, and reset clears them. Do not change `concise_readout` schema or prompt wording.

- [ ] **Step 4: Run tests and verify GREEN**

Run Step 2 again. Expected: all concise contract tests pass, including the unchanged narrative-order assertions.

- [ ] **Step 5: Commit the normal-FCV checkpoint**

```powershell
git add -- index.html tests/test_concise_stage3_contract.py
git commit -m "feat: add contextual watch items to fcv summary"
```

### Task 5: Documentation, parity record, and production acceptance

**Files:**
- Modify: `CLAUDE.md`
- Modify: relevant files under `docs/reference/`
- Modify outside git: `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`
- Create outside git: dated browser screenshots and standalone HTML in the existing visualization session directory

- [ ] **Step 1: Update maintained architecture documentation**

Record the shared DOCX walker, structured financing precedence, Climate `summary_overview` field, Summary disclosures, and unchanged normal-FCV narrative contract. Update the private parity log with only the shared contract surfaces; do not copy private parity content into tracked files.

- [ ] **Step 2: Run focused regression groups**

```powershell
python -m pytest tests/test_docx_structure.py tests/test_climate_source_blocks.py tests/test_climate_verified_runtime.py tests/test_climate_verified_pipeline.py tests/test_climate_verified_render.py tests/test_climate_lens_frontend.py tests/test_concise_stage3_contract.py tests/test_sector_lens_app_contract.py -q
```

Expected: zero failures.

- [ ] **Step 3: Run the full suite**

```powershell
python -m pytest -q
```

Expected: zero failures. Do not reuse an earlier run as completion evidence.

- [ ] **Step 4: Run fresh South Sudan PCN Climate and normal-FCV smoke checks**

Use the test PCN at `.superpowers/brainstorm/Southsudan/Project Concept Note (PCN)_Draft_15_June 2026.docx`. Assert the extracted context displays Operation ID P511185, IPF, and Substantial; MPA is not selected; Climate suggested drafting appears in Summary and Detailed; both modules complete without parse or route errors.

- [ ] **Step 5: Perform browser and export QA**

At phone, laptop, and wide desktop sizes, inspect Climate Summary, Climate Detailed, and normal FCV Summary. Capture full-browser Climate Summary screenshots for the initial closed state and for each opened disclosure. Download a dated standalone shareable HTML, open it offline, and verify disclosures, links, content order, and print expansion. Render and inspect DOCX if its output changed.

- [ ] **Step 6: Final review, commit, push, deploy, and deployed smoke**

Inspect `git diff`, run a final spec-compliance review followed by code-quality review, commit documentation, and push `codex/climate-summary-quality-fixes`. Deploy the approved preview targets, verify they identify the intended commit, and repeat the PCN smoke against the deployed build before reporting production readiness.
