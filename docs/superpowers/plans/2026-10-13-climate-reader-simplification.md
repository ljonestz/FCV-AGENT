# Climate reader simplification implementation plan

Approved by the user after the concrete proposal on 13 October.

Goal: a first-reader-friendly Climate report with flowing context, three concise
assessment answers and clear operational priority cards.

Architecture: retain the existing evidence and admission contracts. Update the
existing generation instructions and browser/Python HTML/Word presentation only.
Use the first recommendation narrative paragraph for why it matters and remaining
paragraphs for action. Older saves without paragraphs use existing structured
fields. No extra model calls or dependencies.

- [x] Add failing tests for removed visible supporting analysis, retained internal
  evidence, priority sections, and prose instructions.
- [x] Update climate_verified_prompts.py and prompt versions. Remove framework
  recaps, semicolons and literal completion labels from narrative instructions.
- [x] Update index.html and climate_verified_render.py: remove detail disclosures
  and supporting appendix, retain compact method/sources, align priority sections
  and place structured details/drafting in the recommendation disclosure.
- [x] Update affected assertions; run focused tests then the full suite once.
- [x] Produce a new explicitly editorial saved-case preview without changing the
  original run or adding recommendations. Inspect browser and HTML download.
- [x] Record checks and limitations, commit and push the existing draft branch.

No paid runs remain authorized. Fresh generation and analytical acceptance remain
outstanding; preview wording is editorial evidence-based content, not a new run.
