"""Bounded source-first prompt for Climate-FCV analysis."""

from __future__ import annotations

import json


def build_analysis_prompt(
    project_facts: list[dict[str, object]],
    derived_assertions: list[dict[str, object]],
    context_evidence: list[dict[str, object]],
) -> str:
    inputs = json.dumps(
        {
            "project_fact_registry": project_facts,
            "derived_assertion_register": derived_assertions,
            "context_evidence": context_evidence,
        },
        ensure_ascii=False,
    )
    return f"""Build a bounded Climate-FCV analysis from the supplied registers.
The project fact registry is authoritative for project design claims.
Derived assertions remain analysis and never become project facts.
Country evidence may support plausible context and pathways but must not establish a project site fact, beneficiary fact, instrument, commitment, or gap.
Guidance may support options, not proof that the project has a gap.

Produce these typed products in order:
1. existing_response_register
2. climate_fcv_pathway_register
3. residual_gap_register
4. opportunities_and_unintended_consequences
5. evidence_limitations

Represent every material documented response relevant to a proposed pathway.
Treat functionally equivalent documented controls as existing responses even when a generic label is absent.
Keep preparation and implementation milestones separate; do not imply dependency unless an explicit project fact establishes it.
Use a maximum three pathways in each direction and a maximum eight residual gaps.
A pathway must contain a mediated chain and at least one project anchor.
A residual gap must show what remains after existing responses are considered.
Use confirmed_omission only with an explicit negative project fact.
Use not_yet_specified or evidence_gap when the document is incomplete.
Return one delimited JSON object and preserve all referenced IDs.

INPUT REGISTERS
{inputs}
"""
