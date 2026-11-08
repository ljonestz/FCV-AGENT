"""Render-only analytical prose layer for verified Climate-FCV reader text.

Applied to assembled stage prompts by build_verified_stage_prompt. It moves the
on-screen climate prose from a plain-language inventory ("The project already
builds ... The main remaining challenge is ... accepted priorities") to connected
expert judgment, mirroring the 2026-11-08 normal-route Stage 3 layer. The
fact-checking contracts (evidence binding, reviewer, correction) are unchanged.

On by default; CLIMATE_PROSE_STYLE=legacy restores the previous wording. The ITS build is not touched (only the ITS team edits it).
"""
from __future__ import annotations

import os

# (old, new) pairs per stage. Each old string must exist exactly once in that
# stage's prompt; tests assert this so wording drift is caught.
_REPLACEMENTS: dict[str, list[tuple[str, str]]] = {
    "reader_compiler": [
        (
            "Begin with a clear overall assessment of what the project already recognizes and\n"
            "addresses. Explain the material remaining challenge and\n"
            "bridge to categories of accepted priorities without enumerating every action.",
            "Open SUM-001 with a crafted analytical judgment, not an inventory: in one or two\n"
            "sentences name the project's central climate-FCV tension (what the design depends\n"
            "on that its climate and fragility context may not sustain) and what is at stake.\n"
            "Then explain how the main climate hazards and fragility dynamics interact with the\n"
            "design, crediting what the design provides together with the condition on which\n"
            "its value depends. Use SUM-002 for the most consequential remaining risk, why it\n"
            "matters for people and delivery, and how the priority actions in this note respond,\n"
            "by category and without enumerating every action.",
        ),
        (
            "Explain the causal connection in ordinary words.",
            "Explain the causal connection in clear expert prose.",
        ),
        (
            "Explain uncertainty and unfamiliar concepts in ordinary language.",
            "Explain uncertainty, and any technical concept briefly, in clear expert prose\n"
            "rather than simplified language.",
        ),
    ],
    "bounded_analysis": [
        (
            "Write each gap as two or three plain-language sentences, 35 to 65 words:",
            "Write each gap as two or three connected analytical sentences, 35 to 65 words:",
        ),
        (
            "Write every existing_responses description as two or three plain-language\n"
            "sentences. Use a short, self-contained first sentence that states the response\n"
            "clearly for a non-specialist reader. In the remaining sentence or sentences,\n"
            "name a concrete project anchor and explain why the response matters for\n"
            "climate-FCV risk, resilience, inclusion, or delivery.",
            "Write every existing_responses description as two or three connected analytical\n"
            "sentences: say what the design choice does, why it suits this project's\n"
            "climate-FCV context, and the condition or limit on which its value depends.\n"
            "Name a concrete project anchor. Describe planned features as planned (is designed\n"
            "to, is intended to), never as delivered.",
        ),
    ],
    "judgment_review": [
        (
            "Explain unfamiliar concepts in ordinary language for a first-time reader.",
            "Explain any technical concept briefly in clear expert prose.",
        ),
    ],
    "drafting_compiler": [
        (
            "For advisory_proposal, make new roles, decision rules and timing visibly proposed\n"
            "in the prose using conditional language, subject to the team's agreement.",
            "Write every block in the project document's own voice, as text the team could\n"
            "paste into the named section, never as advice to the team: do not write 'the team\n"
            "could', 'we recommend', 'consider' or 'it may be useful'. For advisory_proposal,\n"
            "keep new roles, decision rules, methods and timing visibly proposed within that\n"
            "voice: use 'The project proposes to', 'would' and 'to be agreed during preparation',\n"
            "never 'will' for anything not already in the document. End every block with a full\n"
            "sentence.",
        ),
    ],
}

_READER_ADDITION = """

READER REGISTER AND WORDING:
- Write for an experienced FCV and operations reader in the register of a senior peer
  reviewer: connected sentences that carry cause and consequence, typically 25 to 40
  words, with no list-like run of one-fact sentences.
- Do not open the Summary with formulas such as "The project already builds" or "The
  main remaining challenge is"; write a judgment specific to this project.
- Never use internal terms in reader prose: accepted priorities, accepted actions,
  accepted recommendations, admitted, support records, residual gap, pathway, or any
  ID. Refer to "the priority actions in this note" instead.
- Describe planned or designed features as planned (is designed to, is intended to,
  will), never as already delivered or working.
- Avoid repeating the same point across the Summary and the three findings; each
  finding adds analysis the Summary does not already give.
- Make firm qualitative judgments where the evidence supports them (what is strong,
  what is weak and why). Keep uncertainty where it is real, but do not stack could,
  may and depends on in one sentence until the judgment disappears.
- Spell out every acronym on first use in each record.
- Refer to the priority actions in your own words; do not end the Summary with a stock
  formula such as "The priority actions in this note respond by".
- Do not comment on document extraction, headings or file processing, and never write
  placeholder role or office names.
"""


def enabled() -> bool:
    # On by default since the 2026-11-08 production benchmark; "legacy" switches it off.
    return os.environ.get("CLIMATE_PROSE_STYLE", "analytical").strip().lower() != "legacy"


def apply(stage: str, prompt: str) -> str:
    """Return the stage prompt with the analytical prose layer when enabled."""
    if not enabled():
        return prompt
    for old, new in _REPLACEMENTS.get(stage, []):
        prompt = prompt.replace(old, new, 1)
    if stage == "reader_compiler":
        prompt += _READER_ADDITION
    return prompt
