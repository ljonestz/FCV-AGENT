# Climate-FCV Evidence Bank Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the public `climate-fcv-country-bank` companion repository and publish a human-reviewed South Sudan runtime release grounded in traceable qualitative Climate-FCV evidence.

**Architecture:** The companion repository keeps source metadata, atomic evidence, mediated pathways, review decisions, and a long-form country dossier separate from the compact runtime release. Codex may extract and summarize candidate records, but deterministic validators, source locators, and a human approval gate control what enters `releases/current/runtime.json`.

**Tech Stack:** Python 3.13, JSON, JSON Schema Draft 2020-12, `jsonschema`, pytest, Markdown, Git, GitHub CLI.

**Design:** `FCV-AGENT/docs/superpowers/specs/2026-07-30-climate-fcv-evidence-bank-design.md`

**Repository:** `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\climate-fcv-country-bank`

---

## File Map

- `README.md`: purpose, evidence method, review workflow, release use, and copyright boundary.
- `.gitignore`: Python, credentials, downloaded source documents, and generated caches.
- `pyproject.toml`: Python metadata and pytest configuration.
- `requirements-dev.txt`: pinned validation and test dependencies.
- `schemas/source.schema.json`: source provenance and analytical-role contract.
- `schemas/evidence.schema.json`: atomic claim and locator contract.
- `schemas/pathway.schema.json`: mediated Climate-FCV pathway contract.
- `schemas/review.schema.json`: country review and approval contract.
- `schemas/runtime-release.schema.json`: deployable release contract.
- `climate_bank/validation.py`: schema, cross-reference, locator, and review validation.
- `climate_bank/release.py`: deterministic approved-only runtime release builder.
- `climate_bank/dossier.py`: deterministic Markdown dossier assembler.
- `scripts/validate_bank.py`: repository validation CLI.
- `scripts/build_release.py`: runtime release CLI.
- `scripts/build_dossier.py`: dossier-generation CLI.
- `countries/SSD/sources.json`: South Sudan source registry.
- `countries/SSD/evidence.json`: reviewed atomic evidence.
- `countries/SSD/pathways.json`: reviewed mediated pathways.
- `countries/SSD/review.json`: country-level review decision.
- `countries/SSD/dossier.md`: 8-12-page-equivalent human review artifact.
- `releases/current/runtime.json`: compact approved runtime release.
- `tests/`: schema, validation, release, dossier, and South Sudan acceptance tests.

## Fixed Pilot Parameters

- Country: South Sudan (`SSD`) only.
- Runtime item target: 8; hard maximum: 12 across evidence and pathway items.
- Physical-baseline maximum: 2 selected items when Role A or Role B evidence is available.
- Evidence statuses: `observed`, `projected`, `inferred`.
- Analytical roles: `direct-climate-fcv`, `vulnerability-capacity`, `physical-baseline`.
- Pathway strengths: `direct`, `triangulated`, `analytical-inference`.
- Review statuses: `draft`, `reviewed`, `approved`, `stale`, `rejected`.
- Source files remain link-only unless redistribution rights are explicit.
- No open-content licence is added during the pilot; source copyright remains with publishers and the repository contains derived summaries and metadata.

### Task 1: Create and publish the public repository scaffold

**Files:**
- Create: repository root files listed under File Map
- Test: `tests/test_repository_contract.py`

- [ ] **Step 1: Create the repository and feature branch**

Run from `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub`:

```powershell
New-Item -ItemType Directory -Path 'climate-fcv-country-bank'
Set-Location 'climate-fcv-country-bank'
git init -b main
```

Expected: an empty repository on `main` for the scaffold-only initial commit.

- [ ] **Step 2: Write the failing repository-contract test**

```python
# tests/test_repository_contract.py
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_repository_paths_exist() -> None:
    required = (
        "README.md",
        "schemas/source.schema.json",
        "schemas/evidence.schema.json",
        "schemas/pathway.schema.json",
        "schemas/review.schema.json",
        "schemas/runtime-release.schema.json",
        "climate_bank/validation.py",
        "climate_bank/release.py",
        "climate_bank/dossier.py",
    )
    assert all((ROOT / path).exists() for path in required)


def test_raw_source_documents_are_not_tracked() -> None:
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "source_documents/" in ignore
    assert ".env" in ignore
    assert "*credentials*" in ignore
```

- [ ] **Step 3: Run the test to verify it fails**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_repository_contract.py -q -p no:cacheprovider
```

Expected: FAIL because the required scaffold does not exist.

- [ ] **Step 4: Add the minimal scaffold**

Create `.gitignore` with:

```gitignore
.env
*.key
*credentials*
__pycache__/
*.pyc
.venv/
.pytest_cache/
source_documents/
*.tmp
*.log
.DS_Store
Thumbs.db
desktop.ini
```

Create `requirements-dev.txt` with:

```text
jsonschema>=4.23,<5
pytest>=8,<9
```

Create `pyproject.toml` with:

```toml
[project]
name = "climate-fcv-country-bank"
version = "0.1.0"
requires-python = ">=3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Create the package and schema directories named in the File Map. `README.md` must state that the bank is analytical, is not an official WBG classification or policy source, stores no restricted OPCS material, and does not redistribute source PDFs without permission.

- [ ] **Step 5: Run the test to verify it passes**

Run the Task 1 pytest command.

Expected: `2 passed`.

- [ ] **Step 6: Commit and create the public GitHub repository**

```powershell
git add .gitignore README.md pyproject.toml requirements-dev.txt schemas climate_bank scripts tests
git commit -m "chore: scaffold climate fcv country bank"
gh repo create ljonestz/climate-fcv-country-bank --public --source . --remote origin --push
git checkout -b feat/south-sudan-pilot
git push -u origin feat/south-sudan-pilot
```

Expected: the scaffold is published on `main`, and subsequent bank work starts
on the pushed `feat/south-sudan-pilot` branch.

### Task 2: Define schemas and deterministic validation

**Files:**
- Create: `schemas/source.schema.json`
- Create: `schemas/evidence.schema.json`
- Create: `schemas/pathway.schema.json`
- Create: `schemas/review.schema.json`
- Create: `schemas/runtime-release.schema.json`
- Create: `climate_bank/validation.py`
- Create: `scripts/validate_bank.py`
- Test: `tests/test_validation.py`
- Test fixture: `tests/fixtures/valid_country/`

- [ ] **Step 1: Write failing validator tests**

```python
# tests/test_validation.py
import json
from pathlib import Path

from climate_bank.validation import validate_country_directory


FIXTURE = Path(__file__).parent / "fixtures" / "valid_country"


def _copy_fixture(target: Path) -> None:
    for item in FIXTURE.iterdir():
        (target / item.name).write_bytes(item.read_bytes())


def test_valid_country_fixture_has_no_errors() -> None:
    assert validate_country_directory(FIXTURE) == []


def test_general_knowledge_is_rejected(tmp_path: Path) -> None:
    _copy_fixture(tmp_path)
    evidence = json.loads((tmp_path / "evidence.json").read_text(encoding="utf-8"))
    evidence[0]["source_refs"][0]["source_id"] = "general-knowledge"
    (tmp_path / "evidence.json").write_text(json.dumps(evidence), encoding="utf-8")
    assert any("general-knowledge" in error
               for error in validate_country_directory(tmp_path))


def test_missing_locator_is_rejected(tmp_path: Path) -> None:
    _copy_fixture(tmp_path)
    evidence = json.loads((tmp_path / "evidence.json").read_text(encoding="utf-8"))
    evidence[0]["source_refs"][0]["locator"] = ""
    (tmp_path / "evidence.json").write_text(json.dumps(evidence), encoding="utf-8")
    assert any("locator" in error
               for error in validate_country_directory(tmp_path))


def test_pathway_cross_references_are_checked(tmp_path: Path) -> None:
    _copy_fixture(tmp_path)
    pathways = json.loads((tmp_path / "pathways.json").read_text(encoding="utf-8"))
    pathways[0]["supporting_evidence_ids"] = ["SSD-E-999"]
    (tmp_path / "pathways.json").write_text(json.dumps(pathways), encoding="utf-8")
    assert any("SSD-E-999" in error
               for error in validate_country_directory(tmp_path))
```

- [ ] **Step 2: Run the tests to verify they fail**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_validation.py -v -p no:cacheprovider
```

Expected: FAIL with `ModuleNotFoundError` or missing validator functions.

- [ ] **Step 3: Implement the schema contracts**

Use JSON Schema Draft 2020-12. Require these fields and set `additionalProperties` to `false`:

```text
Source: source_id, title, organization, publication_date, url,
repository_file, source_type, analytical_roles[], country_codes[],
geographic_coverage[], temporal_coverage, accessed_on, methodology,
limitations, license_status, checksum

Evidence: evidence_id, iso3, statement, compact_statement, evidence_status,
analytical_role, hazard_tags[], impact_tags[], geographies[], affected_groups[],
sectors[], systems_assets_resources[], institutions[], mediator_tags[],
interaction_direction, time_horizons[], scenario,
source_refs[{source_id, locator}], confidence, uncertainty,
review_status, review_date

Pathway: pathway_id, iso3, climate_pressure, documented_impact, fcv_mediator,
possible_consequence, geographies[], affected_groups[], sectors[],
systems_assets_resources[], institutions[], supporting_evidence_ids[],
link_evidence{pressure[], impact[], mediator[], consequence[]},
evidence_strength, alternative_explanations[], uncertainty,
resilience_factors[], compact_statement, review_status, review_date

Review: iso3, country_name, country_aliases[], status, reviewer, reviewed_on,
review_due, dossier_path, evidence_ids[], pathway_ids[], decision_notes
```

Reject the literal source ID `general-knowledge`. Require HTTPS URLs, non-empty locators, stable IDs matching `SSD-SRC-001`, `SSD-E-001`, and `SSD-P-001` patterns, and enum values from Fixed Pilot Parameters.

- [ ] **Step 4: Implement cross-reference validation**

```python
# climate_bank/validation.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "schemas"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_errors(value: Any, schema_name: str, label: str) -> list[str]:
    schema = _read_json(SCHEMA_ROOT / schema_name)
    validator = Draft202012Validator(schema)
    return [
        f"{label}: {'/'.join(str(part) for part in error.path)}: {error.message}"
        for error in sorted(validator.iter_errors(value), key=str)
    ]


def validate_country_directory(country_dir: Path) -> list[str]:
    sources = _read_json(country_dir / "sources.json")
    evidence = _read_json(country_dir / "evidence.json")
    pathways = _read_json(country_dir / "pathways.json")
    review = _read_json(country_dir / "review.json")
    errors = []
    for value, schema_name, label in (
        (sources, "source.schema.json", "sources"),
        (evidence, "evidence.schema.json", "evidence"),
        (pathways, "pathway.schema.json", "pathways"),
        (review, "review.schema.json", "review"),
    ):
        errors.extend(_schema_errors(value, schema_name, label))
    source_ids = {item["source_id"] for item in sources if isinstance(item, dict)}
    evidence_ids = {item["evidence_id"] for item in evidence if isinstance(item, dict)}
    if "general-knowledge" in source_ids:
        errors.append("sources: general-knowledge is not an admissible source")
    for item in evidence:
        for ref in item.get("source_refs", []):
            if ref.get("source_id") not in source_ids:
                errors.append(f"{item.get('evidence_id')}: unknown source {ref.get('source_id')}")
            if not str(ref.get("locator", "")).strip():
                errors.append(f"{item.get('evidence_id')}: locator is required")
    for pathway in pathways:
        for evidence_id in pathway.get("supporting_evidence_ids", []):
            if evidence_id not in evidence_ids:
                errors.append(f"{pathway.get('pathway_id')}: unknown evidence {evidence_id}")
    if set(review.get("evidence_ids", [])) != evidence_ids:
        errors.append("review: evidence_ids must exactly match the ledger")
    pathway_ids = {item["pathway_id"] for item in pathways if isinstance(item, dict)}
    if set(review.get("pathway_ids", [])) != pathway_ids:
        errors.append("review: pathway_ids must exactly match the pathway ledger")
    return sorted(set(errors))
```

The fixtures must contain two sources, two evidence records, one pathway, and one `draft` review record with valid cross-references.

- [ ] **Step 5: Implement the validation CLI**

```python
# scripts/validate_bank.py
from pathlib import Path

from climate_bank.validation import validate_country_directory


def main() -> int:
    root = Path(__file__).resolve().parents[1] / "countries"
    errors = []
    for country_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        errors.extend(validate_country_directory(country_dir))
    if errors:
        print("\n".join(errors))
        return 1
    print("Climate-FCV country bank validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 6: Run tests and commit**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_validation.py -q -p no:cacheprovider
C:/WBG/Python313/python.exe -m scripts.validate_bank
git add schemas climate_bank scripts tests
git commit -m "feat: define evidence bank schemas and validation"
```

Expected: all validator tests pass and the CLI exits 0.

### Task 3: Build approved-only releases and dossiers

**Files:**
- Create: `climate_bank/release.py`
- Create: `climate_bank/dossier.py`
- Create: `scripts/build_release.py`
- Create: `scripts/build_dossier.py`
- Test: `tests/test_release.py`
- Test: `tests/test_dossier.py`

- [ ] **Step 1: Write failing release tests**

```python
# tests/test_release.py
import json
from pathlib import Path

from climate_bank.release import build_release


FIXTURE = Path(__file__).parent / "fixtures" / "valid_country"


def test_draft_country_is_excluded() -> None:
    release = build_release([FIXTURE], generated_at="2026-07-30T00:00:00Z")
    assert release["countries"] == {}
    assert release["evidence_records"] == []
    assert release["pathways"] == []


def test_approved_country_is_deterministic(tmp_path: Path) -> None:
    for item in FIXTURE.iterdir():
        (tmp_path / item.name).write_bytes(item.read_bytes())
    review = json.loads((tmp_path / "review.json").read_text(encoding="utf-8"))
    review["status"] = "approved"
    (tmp_path / "review.json").write_text(json.dumps(review), encoding="utf-8")
    first = build_release([tmp_path], generated_at="2026-07-30T00:00:00Z")
    second = build_release([tmp_path], generated_at="2026-07-30T00:00:00Z")
    assert first == second
    assert first["countries"]["SSD"]["review_status"] == "approved"
    assert first["source_manifest_checksum"]
```

- [ ] **Step 2: Write failing dossier tests**

```python
# tests/test_dossier.py
from pathlib import Path

from climate_bank.dossier import build_dossier


FIXTURE = Path(__file__).parent / "fixtures" / "valid_country"


def test_dossier_is_built_only_from_ledger_content() -> None:
    dossier = build_dossier(FIXTURE)
    assert "# South Sudan Climate-FCV Evidence Dossier" in dossier
    assert "SSD-E-001" in dossier
    assert "SSD-P-001" in dossier
    assert "general knowledge" not in dossier.casefold()
```

- [ ] **Step 3: Run tests to verify they fail**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_release.py tests/test_dossier.py -v -p no:cacheprovider
```

Expected: FAIL because the builders do not exist.

- [ ] **Step 4: Implement deterministic builders**

Implement the release builder as a deterministic projection of approved ledger
content, including a final validation against `runtime-release.schema.json`:

```python
# climate_bank/release.py
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from climate_bank.validation import (
    validate_country_directory,
    validate_runtime_release,
)


SCHEMA_VERSION = "1.0.0"
CONTENT_VERSION = "2026.07.south-sudan-pilot"


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def build_release(
    country_dirs: Iterable[Path], *, generated_at: str
) -> dict[str, Any]:
    countries: dict[str, Any] = {}
    sources_by_id: dict[str, Any] = {}
    evidence_records: list[dict[str, Any]] = []
    pathways: list[dict[str, Any]] = []
    today = date.fromisoformat(generated_at[:10])
    for country_dir in sorted(Path(path) for path in country_dirs):
        errors = validate_country_directory(country_dir)
        if errors:
            raise ValueError("; ".join(errors))
        review = _read(country_dir / "review.json")
        if review["status"] != "approved":
            continue
        if date.fromisoformat(review["review_due"]) < today:
            raise ValueError(f"{review['iso3']}: approved review is expired")
        country_sources = _read(country_dir / "sources.json")
        country_evidence = [
            item for item in _read(country_dir / "evidence.json")
            if item["review_status"] == "approved"
        ]
        country_pathways = [
            item for item in _read(country_dir / "pathways.json")
            if item["review_status"] == "approved"
        ]
        selected_source_ids = {
            ref["source_id"] for item in country_evidence
            for ref in item["source_refs"]
        }
        for source in country_sources:
            if source["source_id"] in selected_source_ids:
                sources_by_id[source["source_id"]] = source
        evidence_records.extend(country_evidence)
        pathways.extend(country_pathways)
        countries[review["iso3"]] = {
            "iso3": review["iso3"],
            "name": review["country_name"],
            "aliases": sorted(review["country_aliases"]),
            "review_status": "approved",
            "reviewed_on": review["reviewed_on"],
            "review_due": review["review_due"],
            "evidence_ids": sorted(item["evidence_id"] for item in country_evidence),
            "pathway_ids": sorted(item["pathway_id"] for item in country_pathways),
        }
    sources = sorted(sources_by_id.values(), key=lambda item: item["source_id"])
    release = {
        "schema_version": SCHEMA_VERSION,
        "content_version": CONTENT_VERSION,
        "generated_at": generated_at,
        "countries": dict(sorted(countries.items())),
        "sources": sources,
        "evidence_records": sorted(
            evidence_records, key=lambda item: item["evidence_id"]
        ),
        "pathways": sorted(pathways, key=lambda item: item["pathway_id"]),
        "source_manifest_checksum": hashlib.sha256(_canonical(sources)).hexdigest(),
    }
    runtime_errors = validate_runtime_release(release)
    if runtime_errors:
        raise ValueError("; ".join(runtime_errors))
    return release
```

`validate_runtime_release()` uses `_schema_errors()` with
`runtime-release.schema.json`. Implement the dossier as a traceable view over
the same stored records:

```python
# climate_bank/dossier.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _evidence_paragraph(item: dict[str, Any]) -> str:
    return f"{item['statement']} [{item['evidence_id']}]"


def _pathway_paragraph(item: dict[str, Any]) -> str:
    alternatives = "; ".join(item["alternative_explanations"])
    resilience = "; ".join(item["resilience_factors"])
    return (
        f"{item['climate_pressure']} is linked to {item['documented_impact']}. "
        f"Through {item['fcv_mediator']}, a possible consequence is "
        f"{item['possible_consequence']}. Evidence strength: "
        f"{item['evidence_strength']}. Alternative explanations: "
        f"{alternatives}. Resilience factors: {resilience}. Uncertainty: "
        f"{item['uncertainty']} [{item['pathway_id']}; supporting evidence: "
        f"{', '.join(item['supporting_evidence_ids'])}]"
    )


def _section(
    title: str,
    records: list[dict[str, Any]],
    include: Callable[[dict[str, Any]], bool],
) -> list[str]:
    return [f"## {title}", *(
        _evidence_paragraph(item) for item in records if include(item)
    )]


def build_dossier(country_dir: Path) -> str:
    sources = _read(country_dir / "sources.json")
    evidence = _read(country_dir / "evidence.json")
    pathways = _read(country_dir / "pathways.json")
    review = _read(country_dir / "review.json")
    lines = [
        f"# {review['country_name']} Climate-FCV Evidence Dossier",
        "## Scope, sources, and limitations",
        *(
            f"{item['organization']}: {item['title']}. Method: "
            f"{item['methodology']} Limitation: {item['limitations']} "
            f"[{item['source_id']}]"
            for item in sources
        ),
        *_section(
            "Climate baseline", evidence,
            lambda item: item["analytical_role"] == "physical-baseline",
        ),
        *_section(
            "Vulnerability and capacity", evidence,
            lambda item: item["analytical_role"] == "vulnerability-capacity",
        ),
        *_section(
            "Institutions, services, sectors, and livelihoods", evidence,
            lambda item: bool(item["institutions"] or item["sectors"]),
        ),
        "## Mediated Climate-FCV pathways",
        *(_pathway_paragraph(item) for item in pathways),
        "## Reverse pathways",
        *(
            _pathway_paragraph(item) for item in pathways
            if item.get("interaction_direction") == "fcv-to-climate"
        ),
        "## Resilience factors",
        *(
            f"{'; '.join(item['resilience_factors'])} [{item['pathway_id']}]"
            for item in pathways if item["resilience_factors"]
        ),
        "## Uncertainties",
        *(
            f"{item['uncertainty']} [{item['pathway_id']}]"
            for item in pathways
        ),
        "## Project-screening implications",
        *(_evidence_paragraph(item) for item in evidence),
        "## Evidence table",
        *(f"- {item['evidence_id']}: {item['compact_statement']}" for item in evidence),
        "## Bibliography",
        *(f"- {item['source_id']}: {item['title']} - {item['url']}" for item in sources),
    ]
    return "\n\n".join(lines).strip() + "\n"
```

The South Sudan acceptance band is 3,200-4,800 words; the small fixture is
exempt. The builder never invents bridging prose: all analytical paragraphs are
stored evidence or pathway content carrying their canonical IDs.

- [ ] **Step 5: Run tests and commit**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_release.py tests/test_dossier.py -q -p no:cacheprovider
git add climate_bank scripts tests
git commit -m "feat: build reviewed dossiers and runtime releases"
```

Expected: all release and dossier tests pass.

### Task 4: Register the South Sudan pilot literature

**Files:**
- Create: `countries/SSD/sources.json`
- Create: `countries/SSD/evidence.json`
- Create: `countries/SSD/pathways.json`
- Create: `countries/SSD/review.json`
- Test: `tests/test_south_sudan_sources.py`

- [ ] **Step 1: Write the failing source-coverage test**

```python
# tests/test_south_sudan_sources.py
import json
from pathlib import Path


COUNTRY = Path(__file__).resolve().parents[1] / "countries" / "SSD"


def test_south_sudan_source_mix_covers_all_analytical_roles() -> None:
    sources = json.loads((COUNTRY / "sources.json").read_text(encoding="utf-8"))
    roles = {role for source in sources for role in source["analytical_roles"]}
    assert roles == {
        "direct-climate-fcv", "vulnerability-capacity", "physical-baseline"
    }
    assert len(sources) >= 10


def test_qualitative_sources_outnumber_physical_sources() -> None:
    sources = json.loads((COUNTRY / "sources.json").read_text(encoding="utf-8"))
    physical = sum("physical-baseline" in item["analytical_roles"]
                   for item in sources)
    qualitative = sum(bool(
        {"direct-climate-fcv", "vulnerability-capacity"}
        & set(item["analytical_roles"])
    ) for item in sources)
    assert qualitative >= physical * 3
```

- [ ] **Step 2: Run the test to verify it fails**

Expected: FAIL because `countries/SSD/sources.json` does not exist.

- [ ] **Step 3: Add the initial source registry**

Register these link-only sources with access date `2026-07-30`, explicit methodology and limitation notes, and the listed analytical roles:

| ID | Source | Roles |
|---|---|---|
| `SSD-SRC-001` | SIPRI, *Climate, Peace and Security Fact Sheet: South Sudan* (2025), `https://www.sipri.org/publications/2025/partner-publications/climate-peace-and-security-fact-sheet-south-sudan-2025` | direct-climate-fcv |
| `SSD-SRC-002` | UN Climate Security Mechanism, *Climate Security Risks in South Sudan: An Information Brief* (2025), `https://www.un.org/climatesecuritymechanism/en/media/338` | direct-climate-fcv; vulnerability-capacity |
| `SSD-SRC-003` | UN Climate Security Mechanism, *Joining Forces for a Conflict-Sensitive Flood Response in South Sudan* (2025), `https://www.un.org/climatesecuritymechanism/en/news/joining-forces-conflict-sensitive-flood-response-south-sudan` | direct-climate-fcv; vulnerability-capacity |
| `SSD-SRC-004` | World Bank, *South Sudan Country Climate and Development Report* (2026), `https://documents.worldbank.org/en/publication/documents-reports/documentdetail/099013026015514714` | vulnerability-capacity; physical-baseline |
| `SSD-SRC-005` | Government of South Sudan/UNDP, *First National Adaptation Plan* (2021), `https://www.undp.org/south-sudan/publications/first-national-adaptation-plan-climate-change-republic-south-sudan` | vulnerability-capacity |
| `SSD-SRC-006` | Government of South Sudan/UNFCCC, *Second NDC* (2021), `https://unfccc.int/documents/497930` | vulnerability-capacity |
| `SSD-SRC-007` | IOM DTM, *South Sudan Flood Damage and Needs Assessment Study* (2021), `https://dtm.iom.int/reports/south-sudan-flood-damage-and-needs-assessment-study-2021` | vulnerability-capacity |
| `SSD-SRC-008` | UN South Sudan, *Common Country Analysis* (2022), `https://southsudan.un.org/en/187947-south-sudan-un-common-country-analysis-cca` | direct-climate-fcv; vulnerability-capacity |
| `SSD-SRC-009` | INFORM, *South Sudan Country Risk Profile* (2021), `https://drmkc.jrc.ec.europa.eu/Inform-Index/Portals/0/InfoRM/CountryProfiles/SSD.pdf` | vulnerability-capacity |
| `SSD-SRC-010` | UNFPA/UN South Sudan, climate, gender inequality, and violence study summary (2025), `https://southsudan.un.org/en/293784-climate-change-deepens-gender-inequality-and-violence-south-sudan-unfpa-study-highlights` | direct-climate-fcv; vulnerability-capacity |
| `SSD-SRC-011` | IOM DTM, *Event Tracking Report 73: Flood Displacements* (2024), `https://dtm.iom.int/reports/south-sudan-event-tracking-report-73-flood-displacements-1-31-december-2024` | vulnerability-capacity |
| `SSD-SRC-012` | World Bank Climate Change Knowledge Portal, South Sudan resources, `https://climateknowledgeportal.worldbank.org/country/south-sudan/resources` | physical-baseline |

Initialize evidence and pathway ledgers as empty arrays and create a `draft` review record with empty ID lists.

- [ ] **Step 4: Run validation and commit**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_south_sudan_sources.py -q -p no:cacheprovider
C:/WBG/Python313/python.exe -m scripts.validate_bank
git add countries/SSD tests/test_south_sudan_sources.py
git commit -m "data: register South Sudan climate fcv sources"
```

Expected: the source tests pass and repository validation exits 0.

### Task 5: Extract South Sudan evidence and mediated pathways

**Files:**
- Modify: `countries/SSD/evidence.json`
- Modify: `countries/SSD/pathways.json`
- Modify: `countries/SSD/review.json`
- Create: `countries/SSD/dossier.md`
- Test: `tests/test_south_sudan_content.py`

- [ ] **Step 1: Write the failing content acceptance test**

```python
# tests/test_south_sudan_content.py
import json
from pathlib import Path


COUNTRY = Path(__file__).resolve().parents[1] / "countries" / "SSD"


def _read(name: str):
    return json.loads((COUNTRY / name).read_text(encoding="utf-8"))


def test_south_sudan_has_balanced_reviewable_content() -> None:
    evidence = _read("evidence.json")
    pathways = _read("pathways.json")
    roles = [item["analytical_role"] for item in evidence]
    assert 16 <= len(evidence) <= 24
    assert 5 <= len(pathways) <= 8
    assert roles.count("physical-baseline") <= 4
    assert roles.count("direct-climate-fcv") >= 6
    assert roles.count("vulnerability-capacity") >= 6


def test_pathways_expose_causal_uncertainty() -> None:
    for pathway in _read("pathways.json"):
        assert pathway["alternative_explanations"]
        assert pathway["uncertainty"]
        assert pathway["evidence_strength"] in {
            "direct", "triangulated", "analytical-inference"
        }
        assert all(pathway["link_evidence"].values())


def test_dossier_is_long_form_and_traceable() -> None:
    dossier = (COUNTRY / "dossier.md").read_text(encoding="utf-8")
    assert 3200 <= len(dossier.split()) <= 4800
    assert "SSD-E-" in dossier
    assert "SSD-P-" in dossier
```

- [ ] **Step 2: Run the test to verify it fails**

Expected: FAIL because the ledgers are empty and no dossier exists.

- [ ] **Step 3: Extract candidate atomic evidence**

Read every registered source. Paraphrase rather than copy extended text; attach a page, paragraph, table, section, or named webpage-heading locator; tag geography, groups, sectors, systems, institutions, mediators, time horizon, confidence, and uncertainty; classify analytical role separately from source quality; distinguish observed, projected, and inferred evidence; reject model general knowledge; and use IDs `SSD-E-001` upward.

The 16-24 records must cover flooding and drought only to the depth required to support displacement and secondary displacement; pastoral mobility and customary agreements; food and livelihood insecurity; access to services and humanitarian delivery; differentiated gender impacts; governance and coping capacity; conflict constraints on adaptation; and community or institutional resilience.

- [ ] **Step 4: Build mediated pathways**

Create 5-8 pathways covering both directions. Each states pressure, documented impact, mediator, possible consequence, alternative explanations, resilience factors, uncertainty, and evidence support for every link. At least two are `direct`, at least two `triangulated`, and no more than two `analytical-inference`. Never state that climate change causes conflict.

- [ ] **Step 5: Generate the dossier and mark the package reviewed**

```powershell
C:/WBG/Python313/python.exe -m scripts.build_dossier --country SSD
```

Set candidate records and pathways to `reviewed`, set the country review to `reviewed`, populate exact IDs, and record `Codex-assisted draft for Lindsey review` as reviewer.

- [ ] **Step 6: Run validation and content tests**

```powershell
C:/WBG/Python313/python.exe -m scripts.validate_bank
C:/WBG/Python313/python.exe -m pytest tests/test_south_sudan_content.py -q -p no:cacheprovider
```

Expected: validation and content tests pass.

- [ ] **Step 7: Commit the review candidate**

```powershell
git add countries/SSD tests/test_south_sudan_content.py
git commit -m "data: draft South Sudan climate fcv evidence package"
git push -u origin feat/south-sudan-pilot
```

Expected: the candidate is available on GitHub but not in a runtime release.

### Task 6: Human review, release promotion, and pull request

**Files:**
- Modify: `countries/SSD/evidence.json`
- Modify: `countries/SSD/pathways.json`
- Modify: `countries/SSD/review.json`
- Modify: `countries/SSD/dossier.md`
- Create: `releases/current/runtime.json`
- Test: `tests/test_south_sudan_release.py`

- [ ] **Step 1: Pause for country-level human review**

Present the dossier and linked evidence/pathway tables to Lindsey. Approval covers source balance, locators, causal discipline, vulnerability/capacity/institution/sector/group coverage, dossier balance, pathway usefulness, and compact statements.

- [ ] **Step 2: Apply approved edits and record the decision**

Set retained records and pathways to `approved`. Set review status `approved`, reviewer `Lindsey Jones`, reviewed date `2026-07-30`, and review due date `2027-07-30`. Rejected items must not enter release-builder inputs.

- [ ] **Step 3: Write the failing release acceptance test**

```python
# tests/test_south_sudan_release.py
import json
from pathlib import Path


RELEASE = Path(__file__).resolve().parents[1] / "releases" / "current" / "runtime.json"


def test_release_contains_only_approved_south_sudan_content() -> None:
    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    assert set(release["countries"]) == {"SSD"}
    assert release["countries"]["SSD"]["review_status"] == "approved"
    assert all(item["review_status"] == "approved"
               for item in release["evidence_records"])
    assert all(item["review_status"] == "approved"
               for item in release["pathways"])
    assert "general-knowledge" not in RELEASE.read_text(encoding="utf-8")
```

- [ ] **Step 4: Build and verify the release**

```powershell
C:/WBG/Python313/python.exe -m scripts.build_release --generated-at 2026-07-30T00:00:00Z
C:/WBG/Python313/python.exe -m scripts.validate_bank
C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider
```

Expected: the deterministic runtime release contains only approved South Sudan content and all tests pass.

- [ ] **Step 5: Commit, push, and open a pull request**

```powershell
git add countries/SSD releases/current/runtime.json tests/test_south_sudan_release.py
git commit -m "data: approve South Sudan runtime release"
git push
gh pr create --base main --head feat/south-sudan-pilot --title "data: South Sudan climate-FCV pilot release" --body "Adds the reviewed South Sudan source registry, evidence ledger, mediated pathways, dossier, and approved runtime release."
```

Expected: a reviewable pull request exists. Merge only after content review and CI pass.

## Pilot Completion Gate

The track is complete when the public repository exists; all tests pass; the dossier is human-reviewed; only approved records enter the release; checksum generation is deterministic; no raw PDF, secret, restricted OPCS content, or model self-citation is tracked; and the approved release SHA is available for FCV-AGENT.

This plan intentionally stops after the South Sudan pilot. A comparison-country set and FY26 coverage require a separate plan after Lindsey reviews the pilot parameters, evidence balance, and runtime usefulness.
