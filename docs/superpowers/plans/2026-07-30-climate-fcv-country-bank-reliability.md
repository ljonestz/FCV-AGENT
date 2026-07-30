# Climate-FCV Country Bank & Reliability Re-architecture — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Climate-FCV lens always produce a substantive, climate-led assessment by grounding it in a bundled, pre-generated per-country climate-FCV bank (with live web search as always-attempted-but-non-fatal enrichment) and by giving climate mode a dedicated Stage 2 prompt so the diagnostic is the primary output instead of a dropped trailing block.

**Architecture:** Three grounding layers in reliability order — (1) bundled `climate_country_bank.json` floor, (2) bundled thematic KB (`sector_lenses/modules/climate/source_notes/*.md` + `climate_question_bank.py`), (3) live web search as enrichment. Climate Stage 2 switches from "generic FCV engine + climate suffix" to a dedicated climate-native prompt. A live-search failure falls back to the bank with a visible note instead of collapsing the run.

**Tech Stack:** Python 3.13 / Flask, Anthropic SDK (`claude-sonnet-4-6`), pytest, vanilla JS frontend, python-docx exports. Worktree: `.worktrees/climate-country-bank`, branch `feat/climate-country-bank` (off `feat/climate-readout-redesign`, v9.22).

**Spec:** `docs/superpowers/specs/2026-07-30-climate-fcv-reliability-country-bank-design.md`

**Machine notes (this environment):** run Python as `C:/WBG/Python313/python.exe`; run tests with `-p no:cacheprovider --ignore-glob=pytest-cache-files-*` (OneDrive pytest-cache crash otherwise); the Edit tool can silently no-op on the OneDrive path — re-read after editing; git staging is lost between tool calls, so **chain `git add` + `git commit` in one call**; `docs/superpowers/` is gitignored — commit with `git add -f`; **no `Co-Authored-By` trailer**; the dev guide is tracked lowercase as `claude.md` (so `git add claude.md`, not `CLAUDE.md`).

**Baseline before starting:** `C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*` → expect **457 passed**. Record the number; every task must keep it green (plus its own new tests).

---

## Shared contract: the country-bank profile schema

Every task references this. One profile object per country in `climate_country_bank.json` (top-level: `{"bank_version": "1", "generated": "<date>", "profiles": {"<iso3>": {…}}}`):

```python
# Canonical profile shape (validated by validate_country_profile in Task 1)
{
    "country": "South Sudan",
    "iso3": "SSD",
    "fcs_category": "Conflict",            # Conflict | Institutional and Social Fragility | High-Intensity Conflict | not-FCS
    "climate_vulnerability": "Very high",  # qualitative band + basis in `climate_vulnerability_basis`
    "climate_vulnerability_basis": "ND-GAIN bottom decile; low adaptive capacity.",
    "primary_hazards": ["Seasonal flooding", "Drought", "Extreme heat"],
    "climate_fragility_pathways": [
        "Flood displacement pushes communities into armed-group-controlled areas, compounding insecurity.",
        "Pastoralist-farmer competition over shrinking water points escalates communal violence."
    ],
    "hotspot_regions": ["Sudd wetlands / Unity State", "Jonglei", "Northern Bahr el Ghazal"],
    "displacement_and_resource_dynamics": "One short paragraph.",
    "adaptation_entry_points": ["Community flood-resilient landing sites", "Conflict-sensitive water-point siting"],
    "key_uncertainties": ["Flood-projection horizons are contested", "Weak sub-national data"],
    "sources": ["peace_social_dividends", "defueling_conflict", "general-knowledge"],
    "generated_with": "claude-sonnet-4-6",
    "bank_version": "1"
}
```

Field rules: all keys required; list fields may be empty lists but must be present; strings non-null; `fcs_category` from the enum above; `sources[]` entries are either a `source_notes` stem (e.g. `peace_social_dividends`) or the literal `general-knowledge`. The profile is **analytical, not OPCS policy, not an official WBG classification** — a disclaimer string is added at injection time (Task 4), not stored per profile.

---

## Phase 1 — Country bank module, loader, and offline generator

### Task 1: `climate_country_bank_data.py` loader module + schema validation + seed data

**Files:**
- Create: `climate_country_bank_data.py` (loader + validator; repo root, alongside `climate_question_bank.py`)
- Create: `climate_country_bank.json` (seed with 2 real profiles now; full bank generated in Task 2)
- Test: `tests/test_climate_country_bank_data.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_climate_country_bank_data.py
import pytest
from climate_country_bank_data import (
    load_country_bank, get_country_profile, validate_country_profile,
    REQUIRED_PROFILE_KEYS,
)

def test_bank_loads_and_has_profiles():
    bank = load_country_bank()
    assert bank["bank_version"]
    assert isinstance(bank["profiles"], dict)
    assert len(bank["profiles"]) >= 2  # seed

def test_get_profile_exact_name():
    p = get_country_profile("South Sudan")
    assert p is not None
    assert p["iso3"] == "SSD"
    assert p["fcs_category"] == "Conflict"
    assert p["climate_fragility_pathways"]  # non-empty

def test_get_profile_is_alias_and_case_insensitive():
    # reuses FCS_COUNTRY_ALIASES-style matching
    assert get_country_profile("south sudan")["iso3"] == "SSD"
    assert get_country_profile("Democratic Republic of Congo") is not None or \
           get_country_profile("DRC") is not None

def test_unknown_country_returns_none():
    assert get_country_profile("Narnia") is None

def test_validate_rejects_missing_key():
    bad = {"country": "X"}  # missing everything else
    ok, errors = validate_country_profile(bad)
    assert not ok
    assert any("primary_hazards" in e for e in errors)

def test_every_seed_profile_is_valid():
    bank = load_country_bank()
    for iso3, prof in bank["profiles"].items():
        ok, errors = validate_country_profile(prof)
        assert ok, f"{iso3}: {errors}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_climate_country_bank_data.py -v -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL — `ModuleNotFoundError: climate_country_bank_data`.

- [ ] **Step 3: Create the seed `climate_country_bank.json`**

Write two real, complete profiles conforming to the shared schema: `SSD` (South Sudan — use the schema example above, fleshed out) and `TCD` (Chad — Sahel drought/flood, pastoralist-farmer conflict, Lake Chad Basin hotspot, cross-border displacement). Top-level `{"bank_version":"1","generated":"2026-07-30","profiles":{"SSD":{…},"TCD":{…}}}`. Ground the content in the distilled notes under `sector_lenses/modules/climate/source_notes/` (read `defueling_conflict.md`, `peace_social_dividends.md`, `fcv_climate_compendium.md`). Do **not** invent precise statistics.

- [ ] **Step 4: Write minimal implementation**

```python
# climate_country_bank_data.py
"""Bundled per-country climate-FCV grounding bank (offline-generated, runtime read-only).

The bank is the reliable grounding floor for the Climate-FCV lens: it guarantees a
substantive, country-specific assessment with zero live calls. Live web research
enriches it at runtime; the thematic KB (sector_lenses/modules/climate/source_notes)
supplies mechanisms. Regenerate via scripts/build_climate_country_bank.py.
"""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

# Reuse the app's canonical FCS name/alias tables for country matching.
from background_docs import FCS_COUNTRY_ALIASES  # {alias_lower: canonical_name}

_BANK_PATH = Path(__file__).parent / "climate_country_bank.json"

REQUIRED_PROFILE_KEYS = (
    "country", "iso3", "fcs_category", "climate_vulnerability",
    "climate_vulnerability_basis", "primary_hazards", "climate_fragility_pathways",
    "hotspot_regions", "displacement_and_resource_dynamics",
    "adaptation_entry_points", "key_uncertainties", "sources",
)
_LIST_KEYS = (
    "primary_hazards", "climate_fragility_pathways", "hotspot_regions",
    "adaptation_entry_points", "key_uncertainties", "sources",
)
_FCS_CATEGORIES = {
    "Conflict", "Institutional and Social Fragility",
    "High-Intensity Conflict", "not-FCS",
}


def validate_country_profile(profile: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    for key in REQUIRED_PROFILE_KEYS:
        if key not in profile:
            errors.append(f"missing key: {key}")
    if not errors:
        for key in _LIST_KEYS:
            if not isinstance(profile[key], list):
                errors.append(f"{key} must be a list")
        if profile.get("fcs_category") not in _FCS_CATEGORIES:
            errors.append(f"invalid fcs_category: {profile.get('fcs_category')}")
        for key in ("country", "iso3", "climate_vulnerability",
                    "displacement_and_resource_dynamics"):
            if not isinstance(profile.get(key), str) or not profile[key].strip():
                errors.append(f"{key} must be a non-empty string")
    return (not errors, errors)


@lru_cache(maxsize=1)
def load_country_bank() -> dict[str, Any]:
    with _BANK_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def _name_index() -> dict[str, str]:
    """Map lowercased country name / alias -> iso3."""
    bank = load_country_bank()
    index: dict[str, str] = {}
    for iso3, prof in bank["profiles"].items():
        index[prof["country"].lower()] = iso3
        index[iso3.lower()] = iso3
    # Fold in the app's alias table where the canonical name is in the bank.
    canon_to_iso = {prof["country"].lower(): iso3
                    for iso3, prof in bank["profiles"].items()}
    for alias_lower, canonical in FCS_COUNTRY_ALIASES.items():
        iso3 = canon_to_iso.get(str(canonical).lower())
        if iso3:
            index[str(alias_lower).lower()] = iso3
    return index


def get_country_profile(country_name: str | None) -> dict[str, Any] | None:
    if not country_name or not str(country_name).strip():
        return None
    key = str(country_name).strip().lower()
    iso3 = _name_index().get(key)
    if not iso3:
        return None
    return load_country_bank()["profiles"].get(iso3)
```

If `FCS_COUNTRY_ALIASES` is not a dict of `{alias: canonical}`, adapt the fold-in loop to its real shape (read `background_docs.py` around the `FCS_COUNTRY_ALIASES` definition first). The test only requires alias/case-insensitive matching to work for the seed countries.

- [ ] **Step 4b: Run test to verify it passes**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_climate_country_bank_data.py -v -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS (all 6).

- [ ] **Step 5: Commit**

```bash
git add climate_country_bank_data.py climate_country_bank.json tests/test_climate_country_bank_data.py
git commit -m "feat: climate country bank loader, schema validation, and seed data"
```

---

### Task 2: Offline bank generator script (`scripts/build_climate_country_bank.py`)

**Files:**
- Create: `scripts/build_climate_country_bank.py`
- Test: `tests/test_build_climate_country_bank.py`

The script is run **offline by the maintainer** with `ANTHROPIC_API_KEY`; its output (`climate_country_bank.json`) is committed. Tests must run without network — mock the Anthropic client and assert deterministic country-list derivation, resumable merge, and schema-valid output.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_build_climate_country_bank.py
import json, importlib
from pathlib import Path
import scripts.build_climate_country_bank as gen
from climate_country_bank_data import validate_country_profile

def test_country_list_is_deterministic_and_covers_fcs():
    countries = gen.target_country_list()
    assert countries == sorted(set(countries))          # sorted, de-duped
    assert "Chad" in countries and "South Sudan" in countries
    # ND-GAIN supplement is explicit and merged in:
    assert "Bangladesh" in countries

def test_supplement_excludes_countries_already_in_fcs():
    # A supplement entry that is also FCS must not appear twice
    countries = gen.target_country_list()
    assert countries.count("Chad") == 1

def test_merge_per_country_files(tmp_path):
    (tmp_path / "SSD.json").write_text(json.dumps(_valid_profile("South Sudan","SSD")))
    (tmp_path / "TCD.json").write_text(json.dumps(_valid_profile("Chad","TCD")))
    bank = gen.merge_country_files(tmp_path, bank_version="1", generated="2026-07-30")
    assert set(bank["profiles"]) == {"SSD", "TCD"}
    for prof in bank["profiles"].values():
        ok, errors = validate_country_profile(prof); assert ok, errors

def test_generate_one_uses_client_and_returns_valid_profile(monkeypatch):
    fake = _FakeClient(_valid_profile("Chad", "TCD"))
    prof = gen.generate_one_profile("Chad", client=fake, thematic_kb="…notes…")
    ok, errors = validate_country_profile(prof); assert ok, errors
    assert fake.called

def _valid_profile(name, iso3):
    return {
        "country": name, "iso3": iso3, "fcs_category": "Conflict",
        "climate_vulnerability": "Very high", "climate_vulnerability_basis": "x",
        "primary_hazards": ["Drought"], "climate_fragility_pathways": ["p"],
        "hotspot_regions": ["r"], "displacement_and_resource_dynamics": "d",
        "adaptation_entry_points": ["a"], "key_uncertainties": ["u"],
        "sources": ["general-knowledge"], "generated_with": "test", "bank_version": "1",
    }

class _FakeClient:
    def __init__(self, profile): self._p = profile; self.called = False
    def generate_profile_json(self, prompt):   # adapter method the script calls
        self.called = True
        import json as _j; return _j.dumps(self._p)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_build_climate_country_bank.py -v -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL — `ModuleNotFoundError: scripts.build_climate_country_bank`.

- [ ] **Step 3: Write the implementation**

Create `scripts/__init__.py` (empty) if `scripts/` is not yet a package, then `scripts/build_climate_country_bank.py`:

```python
"""Offline generator for climate_country_bank.json. Run by the maintainer:

    ANTHROPIC_API_KEY=... C:/WBG/Python313/python.exe -m scripts.build_climate_country_bank \
        --workdir .bank_work --out climate_country_bank.json

Resumable: writes one <ISO3>.json per country into --workdir; re-running skips
countries already present, then merges into --out. Never reads the restricted OPCS
corpus — grounds only in sector_lenses/modules/climate/source_notes/*.md + general
knowledge. Regenerate to add countries or refresh literature.
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from background_docs import FCS_COUNTRIES_CURRENT           # list[str]
from climate_country_bank_data import validate_country_profile

# Fragile, climate-vulnerable economies to cover in addition to FY26 FCS.
# Maintainer confirms/edits this list; de-duped against FCS at build time.
NDGAIN_SUPPLEMENT = [
    "Bangladesh", "Pakistan", "Zimbabwe", "Madagascar", "Malawi", "Nepal",
    "Kenya", "Uganda", "Tanzania", "Angola", "Guatemala", "Honduras",
    "Bolivia", "Djibouti", "Kiribati", "Tuvalu", "Vanuatu", "Timor-Leste",
]
_NOTES_DIR = Path(__file__).resolve().parents[1] / "sector_lenses" / "modules" / "climate" / "source_notes"


def target_country_list() -> list[str]:
    return sorted(set(FCS_COUNTRIES_CURRENT) | set(NDGAIN_SUPPLEMENT))


def load_thematic_kb() -> str:
    parts = []
    for md in sorted(_NOTES_DIR.glob("*.md")):
        parts.append(f"### {md.stem}\n{md.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def build_profile_prompt(country: str, thematic_kb: str) -> str:
    return (
        "You are compiling an ANALYTICAL climate-FCV country profile for an internal "
        "World Bank FCV screening tool. This is not an official WBG classification and "
        "not OPCS policy. Ground strictly in the curated climate-FCV literature below "
        "and well-established general knowledge; do NOT invent precise statistics.\n\n"
        f"COUNTRY: {country}\n\nCURATED CLIMATE-FCV LITERATURE:\n{thematic_kb[:60000]}\n\n"
        "Return ONE JSON object only, matching exactly these keys: country, iso3, "
        "fcs_category (Conflict|Institutional and Social Fragility|High-Intensity Conflict|not-FCS), "
        "climate_vulnerability, climate_vulnerability_basis, primary_hazards[], "
        "climate_fragility_pathways[], hotspot_regions[] (named sub-national areas), "
        "displacement_and_resource_dynamics (one paragraph), adaptation_entry_points[], "
        "key_uncertainties[], sources[] (source-note stems used, or 'general-knowledge'). "
        "Keep each list to 3-6 concrete, country-specific items."
    )


def generate_one_profile(country: str, client: Any, thematic_kb: str) -> dict[str, Any]:
    raw = client.generate_profile_json(build_profile_prompt(country, thematic_kb))
    profile = json.loads(raw)
    profile.setdefault("generated_with", getattr(client, "model", "claude-sonnet-4-6"))
    profile.setdefault("bank_version", "1")
    ok, errors = validate_country_profile(profile)
    if not ok:
        raise ValueError(f"{country}: invalid profile: {errors}")
    return profile


def merge_country_files(workdir: Path, bank_version: str, generated: str) -> dict[str, Any]:
    profiles: dict[str, Any] = {}
    for fp in sorted(Path(workdir).glob("*.json")):
        prof = json.loads(fp.read_text(encoding="utf-8"))
        profiles[prof["iso3"]] = prof
    return {"bank_version": bank_version, "generated": generated, "profiles": profiles}


class _AnthropicAdapter:
    """Thin real-client adapter; only used when the script actually runs (not in tests)."""
    model = "claude-sonnet-4-6"
    def __init__(self):
        import anthropic
        self._c = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    def generate_profile_json(self, prompt: str) -> str:
        msg = self._c.messages.create(
            model=self.model, max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        start, end = text.find("{"), text.rfind("}")
        return text[start:end + 1]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default=".bank_work")
    ap.add_argument("--out", default="climate_country_bank.json")
    ap.add_argument("--generated", default="2026-07-30")
    args = ap.parse_args(argv)
    workdir = Path(args.workdir); workdir.mkdir(exist_ok=True)
    thematic_kb = load_thematic_kb()
    client = _AnthropicAdapter()
    for country in target_country_list():
        # Resumable: skip countries already written.
        existing = list(workdir.glob("*.json"))
        if any(json.loads(fp.read_text(encoding="utf-8"))["country"] == country
               for fp in existing):
            continue
        try:
            prof = generate_one_profile(country, client, thematic_kb)
        except Exception as exc:  # noqa: BLE001 - log and continue; re-run resumes
            print(f"[skip] {country}: {exc}", file=sys.stderr); continue
        (workdir / f"{prof['iso3']}.json").write_text(json.dumps(prof, indent=2))
        print(f"[ok] {country} -> {prof['iso3']}")
    bank = merge_country_files(workdir, bank_version="1", generated=args.generated)
    Path(args.out).write_text(json.dumps(bank, indent=2, ensure_ascii=False))
    print(f"wrote {len(bank['profiles'])} profiles to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Confirm `FCS_COUNTRIES_CURRENT` is a `list[str]` of country names (grep `background_docs.py`); if it is a dict/other shape, adapt `target_country_list()` accordingly.

- [ ] **Step 4: Run test to verify it passes**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_build_climate_country_bank.py -v -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS (4).

- [ ] **Step 5: Commit**

```bash
git add scripts/__init__.py scripts/build_climate_country_bank.py tests/test_build_climate_country_bank.py
git commit -m "feat: offline resumable climate country-bank generator"
```

- [ ] **Step 6 (maintainer, out-of-band — not a code step): generate the full bank.**

The maintainer runs the generator with an API key to produce the full ~50-60 country bank, reviews a sample of profiles for quality, and commits the regenerated `climate_country_bank.json`. Until then, the seed bank (2 countries) keeps tests green and the runtime paths exercised. **Flag this to the user at execution handoff.**

---

## Phase 2 — Runtime lookup + graceful degradation

### Task 3: Attach the bank profile to Stage 1 / `AnalysisState`

**Files:**
- Modify: `app.py` (the Stage 1 handler where the country is detected and `AnalysisState` is populated — grep `classify_country(` and `researchCountry`/country extraction in `/api/run-express` and `/api/run-stage`)
- Modify: `app.py` `AnalysisState` definition (add a field)
- Test: `tests/test_climate_country_bank_runtime.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_climate_country_bank_runtime.py
from app import attach_country_climate_profile

def test_attach_profile_for_in_bank_country():
    state = {}  # or a lightweight AnalysisState-like stub if the fn takes the state
    prof = attach_country_climate_profile("South Sudan")
    assert prof is not None and prof["iso3"] == "SSD"

def test_attach_profile_returns_none_out_of_bank():
    assert attach_country_climate_profile("Narnia") is None
```

- [ ] **Step 2: Run to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_climate_country_bank_runtime.py -v -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL — `ImportError: cannot import name 'attach_country_climate_profile'`.

- [ ] **Step 3: Implement the helper + wire it**

Add near `classify_country` in `app.py`:

```python
from climate_country_bank_data import get_country_profile as _get_climate_country_profile

def attach_country_climate_profile(country_name: str | None) -> dict | None:
    """Return the bundled climate-FCV bank profile for a country, or None if not banked."""
    return _get_climate_country_profile(country_name)
```

Add a `climate_country_profile: dict | None = None` field to `AnalysisState` (find its definition — likely a dataclass). In **both** run routes (`/api/run-express`, `/api/run-stage`), after the country is resolved for Stage 1, set `state.climate_country_profile = attach_country_climate_profile(<resolved country>)` (use the same country string passed to `classify_country`). This runs regardless of lens selection (cheap dict lookup) and is only *consumed* when the climate lens is active.

- [ ] **Step 4: Run to verify it passes**

Run the same command. Expected: PASS (2). Then run the full suite to confirm no regression:
`C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*` → 457 + new tests.

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_climate_country_bank_runtime.py
git commit -m "feat: attach bundled climate country profile to analysis state"
```

---

### Task 4: Inject the bank profile + degradation note into the climate Stage 2 context

**Files:**
- Modify: `app.py` `build_lens_stage_context` (Stage 2 climate branch, ~line 1050+ where `if "climate" in active_ids:` composes `compact_claims` from `climate_research`)
- Modify: `app.py` signature of `build_lens_stage_context` — add `climate_country_profile: dict | None = None`
- Modify: both call sites that pass `climate_research=` into `build_lens_stage_context` — also pass `climate_country_profile=state.climate_country_profile`
- Test: extend `tests/test_climate_country_bank_runtime.py`

- [ ] **Step 1: Write the failing test**

```python
def test_climate_stage2_prompt_includes_bank_profile_when_present(monkeypatch):
    from app import build_climate_grounding_block
    prof = {"country": "South Sudan", "iso3": "SSD",
            "primary_hazards": ["Seasonal flooding"],
            "climate_fragility_pathways": ["Flood displacement into armed-group areas"],
            "hotspot_regions": ["Sudd wetlands"], "adaptation_entry_points": ["Flood-resilient sites"],
            "key_uncertainties": ["Flood horizons contested"],
            "displacement_and_resource_dynamics": "…",
            "fcs_category": "Conflict", "climate_vulnerability": "Very high",
            "climate_vulnerability_basis": "…", "sources": ["general-knowledge"]}
    block = build_climate_grounding_block(prof, research_succeeded=True)
    assert "Sudd wetlands" in block
    assert "Flood displacement" in block
    assert "not an official WBG classification" in block  # disclaimer present
    assert "curated climate-FCV knowledge base" not in block  # no fallback note when research ok

def test_climate_grounding_block_adds_fallback_note_when_research_failed():
    prof = {"country":"Chad","iso3":"TCD","primary_hazards":["Drought"],
            "climate_fragility_pathways":["p"],"hotspot_regions":["Lake Chad"],
            "adaptation_entry_points":["a"],"key_uncertainties":["u"],
            "displacement_and_resource_dynamics":"d","fcs_category":"Conflict",
            "climate_vulnerability":"High","climate_vulnerability_basis":"b","sources":["general-knowledge"]}
    block = build_climate_grounding_block(prof, research_succeeded=False)
    assert "curated climate-FCV knowledge base" in block  # amber fallback note text

def test_climate_grounding_block_handles_no_profile():
    block = build_climate_grounding_block(None, research_succeeded=False)
    assert "country-specific" in block.lower()  # bank-miss note; still non-empty, never raises
```

- [ ] **Step 2: Run to verify it fails**

Expected: FAIL — `ImportError: cannot import name 'build_climate_grounding_block'`.

- [ ] **Step 3: Implement `build_climate_grounding_block` and inject it**

Add to `app.py`:

```python
_CLIMATE_BANK_DISCLAIMER = (
    "The following country climate-FCV profile is an internal analytical grounding "
    "aid, not an official WBG classification and not OPCS policy."
)
_CLIMATE_BANK_FALLBACK_NOTE = (
    "NOTE FOR THIS RUN: live country research was unavailable, so country grounding is "
    "drawn from the curated climate-FCV knowledge base. Prefer the project document for "
    "specifics; flag where current or sub-national detail could not be verified."
)
_CLIMATE_NO_BANK_NOTE = (
    "No bundled country profile is available; ground the climate-FCV analysis in the "
    "project document and the thematic climate-FCV knowledge, and state where "
    "country-specific external grounding was unavailable."
)

def build_climate_grounding_block(profile: dict | None, research_succeeded: bool) -> str:
    if not profile:
        return _CLIMATE_NO_BANK_NOTE
    lines = [
        _CLIMATE_BANK_DISCLAIMER,
        f"COUNTRY CLIMATE-FCV PROFILE — {profile.get('country','')} "
        f"({profile.get('fcs_category','')}; climate vulnerability {profile.get('climate_vulnerability','')}):",
        "Primary hazards: " + "; ".join(profile.get("primary_hazards", [])),
        "Climate-fragility pathways: " + " | ".join(profile.get("climate_fragility_pathways", [])),
        "Named hotspot regions: " + "; ".join(profile.get("hotspot_regions", [])),
        "Displacement & resource dynamics: " + str(profile.get("displacement_and_resource_dynamics", "")),
        "Adaptation entry points: " + "; ".join(profile.get("adaptation_entry_points", [])),
        "Key uncertainties (do not over-claim): " + "; ".join(profile.get("key_uncertainties", [])),
    ]
    if not research_succeeded:
        lines.append(_CLIMATE_BANK_FALLBACK_NOTE)
    return "\n".join(lines)
```

In `build_lens_stage_context`: add the `climate_country_profile` parameter; compute `research_succeeded` from the normalized bundle (e.g. `bool(research.get("claims") or research.get("sources"))`); and **prepend** `build_climate_grounding_block(climate_country_profile, research_succeeded)` to the climate Stage 2 grounding (before the compact research claims). Cap the injected block length to protect the Stage 2 budget (see Task 6 budget note). Update both call sites to pass `climate_country_profile=state.climate_country_profile`.

- [ ] **Step 4: Run to verify it passes** (the 3 new tests + full suite green).

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_climate_country_bank_runtime.py
git commit -m "feat: inject climate country-bank grounding with graceful research-fallback note"
```

---

## Phase 3 — Dedicated climate Stage 2 prompt (Fix B)

### Task 5: Failing full-prompt isolation test (pin the contract first)

**Files:**
- Test: `tests/test_climate_native_stage2_prompt.py`

- [ ] **Step 1: Write the failing test**

This test builds the assembled Stage 2 prompt for a climate-active state and asserts the generic FCV engine is **absent** and the dedicated climate structure is **present**. Use the smallest real entry point that returns the composed Stage 2 prompt text for a climate-active state — most likely calling `build_lens_stage_context(state, stage=2, ..., compose_prompt=True)` and inspecting `["prompt"]`, OR the higher-level Stage 2 prompt assembler if the generic engine lives in `DEFAULT_PROMPTS["2"]` and is concatenated elsewhere. Read how `/api/run-express` assembles the Stage 2 user prompt when a lens is active, and target that assembler; if it is inline, extract it into a named function `assemble_stage2_prompt(state, ...)` in this task so it is testable, and have the route call the new function (pure refactor, no behavior change for non-climate).

```python
# tests/test_climate_native_stage2_prompt.py
from app import assemble_stage2_prompt  # extracted in Step 3 if not already present

GENERIC_ENGINE_MARKERS = [
    "12-rec", "12 OST", "RECS_TABLE", "DNH_CHECKLIST", "QUESTIONS_MAP",
    "25 key questions", "25 diagnostic",
]

def _climate_state():
    # Minimal climate-active state stub; mirror the real AnalysisState fields the
    # assembler reads (active_lenses=['climate'], instrument='IPF', doc_type='PCN', etc.)
    ...

def test_climate_mode_prompt_excludes_generic_engine():
    prompt = assemble_stage2_prompt(_climate_state(), climate_active=True)
    low = prompt.lower()
    for marker in GENERIC_ENGINE_MARKERS:
        assert marker.lower() not in low, f"generic engine leaked: {marker}"

def test_climate_mode_prompt_requests_primary_diagnostic():
    prompt = assemble_stage2_prompt(_climate_state(), climate_active=True)
    assert "LENS_DIAGNOSTIC" in prompt  # the diagnostic delimiter is requested
    assert "integration_rating" in prompt  # dedicated climate readout contract
    assert "strengths_weaknesses" in prompt

def test_non_climate_mode_prompt_keeps_generic_engine():
    prompt = assemble_stage2_prompt(_climate_state(), climate_active=False)
    assert "RECS_TABLE" in prompt or "UNDER_HOOD" in prompt  # generic engine intact
```

- [ ] **Step 2: Run to verify it fails**

Expected: FAIL — import error or assertion (the current climate prompt still contains the generic engine because it is generic + suffix).

- [ ] **Step 3: Commit the failing test only (red baseline)**

```bash
git add tests/test_climate_native_stage2_prompt.py
git commit -m "test: pin climate-native Stage 2 prompt contract (currently red)"
```

---

### Task 6: Implement the dedicated climate-native Stage 2 prompt

**Files:**
- Modify: `app.py` — extract/introduce `assemble_stage2_prompt(state, climate_active)` and a `DEFAULT_PROMPTS`-adjacent constant `CLIMATE_NATIVE_STAGE2_PROMPT`
- Modify: both Stage 2 call sites (`/api/run-express`, `/api/run-stage`) to route through `assemble_stage2_prompt`
- Test: `tests/test_climate_native_stage2_prompt.py` (from Task 5) must go green; full suite stays green

- [ ] **Step 1: Author `CLIMATE_NATIVE_STAGE2_PROMPT`**

A dedicated climate-led Stage 2 prompt that **replaces** the generic engine when climate is active. It MUST:
- NOT include the 12-OST recs table, DNH-9 checklist, 25-question map, or the `%%%UNDER_HOOD%%%`/`RECS_TABLE`/`QUESTIONS_MAP`/`DNH_CHECKLIST` blocks.
- Request, as the **primary** output, the climate diagnostic between `LENS_DIAGNOSTIC_START`/`LENS_DIAGNOSTIC_END` with the v9.22 dedicated-module contract: `integration_rating` (6-tier), `strengths_weaknesses[]` (side/title/text), `reflections[]` (per-theme, with `source`, two-paragraph `text`), both directional interaction pathways with stable IDs, `less_central`, and separate `sensitivity_evidence`/`responsiveness_evidence`.
- Carry a **compact internal FCV baseline** only: a short instruction to internally weigh S/R and produce the two ratings, without emitting the verbose tables.
- Consume the grounding block from Task 4 (bank profile + research + thematic KB + triggered question bank from `select_triggered_questions`).
- Keep the OPCS §12/§12.9 climate calibration guardrails already present in the v9.22 climate suffix (instrument-route recs; PA/CDRS flag-not-determine; asset-appropriate horizon; IPF-only ESS map; conditional compound-risk wording; analytical-source labelling; advisory boundary).

Reuse the existing v9.22 climate suffix text as the seed for the diagnostic-contract portion — the change is that this content becomes the *base* prompt (not a suffix after the generic engine), and the generic engine is dropped in climate mode.

- [ ] **Step 2: Implement `assemble_stage2_prompt`**

```python
def assemble_stage2_prompt(state, climate_active: bool, **kwargs) -> str:
    """Return the Stage 2 user prompt. Climate-active runs use the dedicated
    climate-native base prompt (diagnostic as primary output); all other runs use the
    existing generic FCV engine unchanged."""
    if climate_active:
        return build_climate_native_stage2_prompt(state, **kwargs)  # bank block + CLIMATE_NATIVE_STAGE2_PROMPT + calibration
    return build_generic_stage2_prompt(state, **kwargs)  # the existing assembly, extracted verbatim
```

Extract the **current** generic Stage 2 assembly into `build_generic_stage2_prompt` **verbatim** (pure refactor — the non-climate tests must not move). Implement `build_climate_native_stage2_prompt` to concatenate: the Task 4 grounding block → `CLIMATE_NATIVE_STAGE2_PROMPT` → triggered question bank → OPCS calibration guardrails. Route both API call sites through `assemble_stage2_prompt(state, climate_active=("climate" in active_ids))`.

- [ ] **Step 3: Run the Task 5 tests + full suite**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_climate_native_stage2_prompt.py -v -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: the 3 isolation tests PASS. Then full suite green (457 + all new). If any prior climate test asserted the generic engine appears in climate mode, update it to the new contract and note it in the commit (expected: the climate suffix tests move to the native-prompt contract).

- [ ] **Step 4: Budget check**

Confirm the climate-native Stage 2 prompt (bank block + native prompt + question bank + calibration) is **materially smaller** than the old generic(45k)+suffix(13k)=58k. Cap the injected bank block (Task 4) and question bank so the assembled climate prompt stays within `PLATFORM_STAGE_BUDGETS.stage2` (3300 token target) headroom. Add an assertion test:

```python
def test_climate_native_prompt_smaller_than_legacy_combo():
    prompt = assemble_stage2_prompt(_climate_state(), climate_active=True)
    assert len(prompt) < 45000  # must not reproduce the generic-engine bulk
```

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_climate_native_stage2_prompt.py
git commit -m "feat: dedicated climate-native Stage 2 prompt (diagnostic as primary output)"
```

---

## Phase 4 — Reliability safeguards & observability

### Task 7: Recovery becomes exception-only; single research deadline owner; typed logging

**Files:**
- Modify: `app.py` `extract_or_repair_lens_diagnostic` (2023), `repair_lens_diagnostic` (1818), `_iter_stage1_research` (7288) / `run_climate_web_research` (6935)
- Test: `tests/test_climate_native_stage2_prompt.py` + `tests/test_climate_diagnostic_completeness.py` (existing) extended

- [ ] **Step 1: Write the failing tests**

```python
def test_happy_path_primary_diagnostic_skips_recovery(monkeypatch):
    # A complete primary climate diagnostic must NOT trigger a recovery call.
    calls = {"n": 0}
    monkeypatch.setattr("app.repair_lens_diagnostic", lambda *a, **k: calls.__setitem__("n", calls["n"]+1) or {})
    from app import extract_or_repair_lens_diagnostic
    complete = _complete_climate_diagnostic()  # helper: reflections + integration_summary present
    out = extract_or_repair_lens_diagnostic(_stage2_text_with(complete), active_ids=["climate"], ...)
    assert calls["n"] == 0

def test_research_retry_respects_parent_budget(monkeypatch):
    # A retry must not be issued when the remaining Stage 1 research budget is exhausted.
    from app import _climate_research_should_retry
    assert _climate_research_should_retry(elapsed=149, budget=150) is False
    assert _climate_research_should_retry(elapsed=40, budget=150) is True
```

- [ ] **Step 2: Run to verify they fail** (import errors / current behavior triggers recovery on the complete path if the primary was being ignored).

- [ ] **Step 3: Implement**

- In `extract_or_repair_lens_diagnostic`: ensure a *complete* primary climate diagnostic is adopted with **no** recovery call (Fix B makes the primary reliable, so recovery must be a true exception). Keep the v9.20 "recover on incomplete-but-usable, never downgrade a usable primary" behavior; just make the complete-primary path provably recovery-free.
- Add `_climate_research_should_retry(elapsed, budget)` and use it in `_iter_stage1_research`/`run_climate_web_research` so a retry is issued only when `budget - elapsed` exceeds a minimum floor (e.g. 25s), preventing the parent-timeout/discard mismatch (spec §5).
- Ensure `repair_lens_diagnostic` emits SSE heartbeats or runs in the streamed queue rather than a silent ~120s block (reuse the `_stream_stage` keepalive pattern). If a full streaming refactor is out of scope, at minimum bound its `max_tokens`/timeout and log start/end with the `assessment_id` and a typed status (`recovery_started`/`recovery_ok`/`recovery_timeout`).
- Add typed, low-cardinality log lines at each failure mode: `research_empty`, `diagnostic_omitted`, `recovery_timeout`, `provider_529`, each with `assessment_id`.

- [ ] **Step 4: Run tests + full suite** → green.

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_climate_native_stage2_prompt.py tests/test_climate_diagnostic_completeness.py
git commit -m "feat: recovery exception-only, budgeted research retry, typed climate failure logging"
```

---

## Phase 5 — Exports, docs, and live acceptance

### Task 8: Frontend/DOCX fallback-note parity + docs

**Files:**
- Modify: `index.html` (`renderClimateModuleNotice` / the climate readout renderers) — surface the "live country research unavailable — bank grounding used" amber note when the run used the fallback
- Modify: `app.py` DOCX `add_climate_notice` (or equivalent) — same note in the downloaded report
- Modify: SSE payloads for Stage 2 climate to carry a `climate_grounding: "bank+research" | "bank-only" | "thematic-only"` flag the frontend renders
- Modify: `claude.md` (lowercase) version history — add a v9.23 entry; `docs/reference/*` where the climate contract is documented; `~/.claude/FCV_BUILD_PARITY.md` note (bank + dedicated-prompt contract)
- Test: `tests/test_climate_lens_frontend.py` (extend — the note renders when `climate_grounding == "bank-only"`)

- [ ] **Step 1: Write the failing frontend test**

Extend the existing frontend contract test (`tests/test_climate_lens_frontend.py`, which spawns `node`) to assert that when the Stage 2 payload has `climate_grounding: "bank-only"`, `renderClimateModuleNotice` output contains the fallback wording; when `"bank+research"`, it does not.

- [ ] **Step 2: Run to verify it fails.**

- [ ] **Step 3: Implement** the `climate_grounding` flag end-to-end: set it in the Stage 2 backend hook based on `research_succeeded` + profile presence; thread it into the SSE `stage_complete`/diagnostic payload; render the amber note in `renderClimateModuleNotice` and in the DOCX `add_climate_notice`. Reuse the existing amber-notice CSS/DOCX styling.

- [ ] **Step 4: Run frontend test + full suite** → green.

- [ ] **Step 5: Update docs**

Add the v9.23 entry to `claude.md` (bank grounding + dedicated climate Stage 2 prompt + graceful research fallback), update the climate sections of `docs/reference/reference_prompt_architecture.md` and `reference_backend_routes.md`, and add the parity surface to `~/.claude/FCV_BUILD_PARITY.md`.

- [ ] **Step 6: Commit**

```bash
git add index.html app.py claude.md docs/reference tests/test_climate_lens_frontend.py
git commit -m "feat: climate grounding-provenance note in UI+DOCX; docs v9.23"
```

- [ ] **Step 7: Live acceptance (maintainer, out-of-band)**

Push the branch → Render preview redeploys → wake the free-tier service → run **South Sudan PCN** (in bank) and one **CCDR-context** run in Express. Confirm: (a) the climate diagnostic renders on the **primary** path (Render log shows no load-bearing recovery); (b) live search enriches when it returns; (c) the amber "bank grounding used" note appears when search fails and the assessment still completes and is specific; (d) `climate_grounding` flag matches reality. Capture the downloaded HTML + Render log slice by `assessment_id`.

---

## Self-review — spec coverage

- Spec §3 Fix A (three-layer grounding) → Tasks 1, 2 (bank), 4 (injection + layering), thematic KB reused. ✅
- Spec §3 Fix B (dedicated Stage 2 prompt) → Tasks 5, 6. ✅
- Spec §4.1 bank data + schema → Task 1. §4.2 generator (offline, resumable, regenerable, no restricted paths) → Task 2. §4.3 thematic KB reuse → Task 6. §4.4 runtime wiring → Tasks 3, 4. §4.5 degradation matrix → Task 4 (+ Task 8 provenance flag). ✅
- Spec §5 reliability (single deadline owner, retry budget, primary-required, bounded observable recovery, typed failures) → Task 7. ✅
- Spec §6 testing (full-prompt isolation, bank lookup, degradation, happy-path-no-recovery, observable recovery, generator, no regression) → Tasks 1–8 tests. ✅
- Spec §7 branch/integration + §8 phasing → this plan's structure; live acceptance → Task 8 Step 7. ✅
- Spec §9 open items: ND-GAIN supplement enumerated in Task 2; profile token/budget cap in Tasks 4 & 6; Stage-2-only injection default in Task 4; deadline-owner boundary in Task 7. ✅

**Note for executor:** the full ~50-60 country bank is generated **out-of-band by the maintainer** (Task 2 Step 6) with an API key; code tasks run against the 2-country seed so the suite stays green and CI-safe. Do not attempt to call the live Anthropic API from tests.
