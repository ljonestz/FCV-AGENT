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

from fcv_snapshot_rules import SNAPSHOT_RULES

# (old, new) pairs per stage. Each old string must exist exactly once in that
# stage's prompt; tests assert this so wording drift is caught.
_REPLACEMENTS: dict[str, list[tuple[str, str]]] = {
    "reader_compiler": [
        (
            "Begin with a clear overall assessment of what the project already recognizes and\n"
            "addresses. Explain the material remaining challenge and\n"
            "bridge to categories of accepted priorities without enumerating every action.",
            # 2026-11-27 (owner): SUM-001 fills the readout's snapshot box; SUM-002 opens the main text.
            "Write SUM-001 and SUM-002 following the SNAPSHOT AND OPENING RULES at the end of\n"
            "these instructions.",
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
        # 2026-11-16 paragraph shape: fewer, fuller paragraphs (same hard ceilings).
        (
            "Summary: prefer two connected paragraphs of about 90-100 words each, targeting 190 words overall (editorial target 160-230); use a third only if essential.",
            # 2026-11-28 (owner): assessment-verdict snapshot (75-95w) + segue/opening (95-115w), shared with normal route.
            "Summary: write SUM-001 as the snapshot and SUM-002 as the segue plus opening paragraph,\n"
            "following the SNAPSHOT AND OPENING RULES at the end of these instructions; about\n"
            "175-210 words overall. Do not add a third paragraph.",
        ),
        (
            "Assessment narratives: three short question-led answers,",
            "Assessment narratives: three question-led answers,",
        ),
        (
            "Keep design to\n180-240 words, as for dividends and inclusion, in two or three connected\n"
            "paragraphs when the support is rich enough.",
            "Keep design to\n220-280 words, as for dividends and inclusion, in two connected paragraphs\n"
            "(a third only if essential), each building one argument over four to six sentences,\n"
            "when the support is rich enough.",
        ),
        (
            "Target 180-240 words;",
            "Target 220-280 words;",
        ),
        (
            "Aim for about 190 summary words.",
            "Aim for about 195 summary words.",
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
        (
            "executive_readout as two to three short paragraphs separated by a blank line,\n"
            "each covering one clear theme, so a reader can scan the key takeaways.",
            "executive_readout as two or three full paragraphs separated by a blank line,\n"
            "each developing one clear theme as connected argument, not a list of takeaways.",
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
- SUM-001 and SUM-002 follow the SNAPSHOT AND OPENING RULES below, not the next two
  points.
- Write for an experienced FCV and operations reader in the register of a senior peer
  reviewer: connected sentences that carry cause and consequence, typically 25 to 40
  words, with no list-like run of one-fact sentences.
- Build each paragraph around one line of reasoning carried across four to six
  sentences. Do not split one argument across separate short paragraphs, and do not
  end a paragraph after a single point.
- Do not open the Summary with formulas such as "The project already builds" or "The
  main remaining challenge is"; write a judgment specific to this project.
- Never use internal terms in reader prose: accepted priorities, accepted actions,
  accepted recommendations, admitted, support records, residual gap, pathway, or any
  ID. Refer to "the priority actions in this note" as proposed options instead.
- Describe planned or designed features as planned (is designed to, is intended to,
  will), never as already delivered or working.
- Avoid repeating the same point across the Summary and the three findings; each
  finding adds analysis the Summary does not already give.
- Make firm qualitative judgments where the evidence supports them (what is strong,
  what is weak and why). Keep uncertainty where it is real, but do not stack could,
  may and depends on in one sentence until the judgment disappears.
- Spell out every acronym on first use in each record.
- Refer to the priority actions in your own words as proposed suggestions, never as
  enacted changes; do not end the Summary with a stock formula such as "The priority
  actions in this note respond by" or "The priority actions in this note clarify".
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
        # The fact-checking contracts (reader_correction, reviewer) stay unchanged by design.
        prompt += _READER_ADDITION + SNAPSHOT_RULES
    return prompt
