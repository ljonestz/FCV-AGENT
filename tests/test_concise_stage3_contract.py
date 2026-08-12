import app


def test_step_by_step_core_prompt_gets_concise_contract_but_lens_prompt_does_not():
    base = app.DEFAULT_PROMPTS["3"]
    core_prompt = app.append_core_concise_stage3_contract(
        base, "PCN", {"processing_track": "standard"}, []
    )
    lens_prompt = app.append_core_concise_stage3_contract(
        base, "PCN", {"processing_track": "standard"}, [{"id": "climate"}]
    )

    assert '"concise_readout"' not in base
    assert '"concise_readout"' in core_prompt
    assert '"concise"' in core_prompt
    assert "same findings, ratings, priority order, and actions" in core_prompt
    assert "700-1,000 words" in core_prompt
    assert '"concise_readout"' not in lens_prompt


def test_express_core_prompt_gets_concise_contract_but_lens_prompt_does_not():
    base = app.DEFAULT_PROMPTS["3"]
    core_prompt = app.append_core_concise_stage3_contract(
        base, "PAD", {"processing_track": "standard"}, []
    )
    lens_prompt = app.append_core_concise_stage3_contract(
        base, "PAD", {"processing_track": "standard"}, [{"id": "agriculture"}]
    )

    assert '"concise_readout"' in core_prompt
    assert "Resolve before the review gate" in core_prompt
    assert '"concise_readout"' not in lens_prompt


def test_concise_lifecycle_context_for_standard_pcn():
    text = app.build_concise_lifecycle_context(
        "PCN", {"processing_track": "standard"}
    )
    assert "Commit in the PCN" in text
    assert "Develop during preparation" in text


def test_concise_lifecycle_context_for_consolidated_pcn():
    text = app.build_concise_lifecycle_context(
        "PCN", {"processing_track": "consolidated_condensed"}
    )
    assert "Resolve by Decision Review" in text
    assert "Complete in parallel" in text


def test_concise_lifecycle_context_for_pad_does_not_defer():
    text = app.build_concise_lifecycle_context(
        "PAD", {"processing_track": "standard"}
    )
    assert "Resolve before the review gate" in text
    assert "Do not defer" in text


def test_concise_lifecycle_context_for_pid_does_not_defer():
    text = app.build_concise_lifecycle_context(
        "PID", {"processing_track": "standard"}
    )
    assert "Resolve before the review gate" in text
    assert "Do not defer" in text


def test_concise_lifecycle_context_unknown_is_conservative():
    text = app.build_concise_lifecycle_context("PCN", {})
    assert "When to address" in text
    assert "do not assert an unverified procedural gate" in text
