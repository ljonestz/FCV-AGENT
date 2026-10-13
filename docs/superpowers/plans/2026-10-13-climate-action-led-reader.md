# Climate action-led reader implementation plan

Approved by Lindsey on 13 October 2026.

Goal: make the assessment concise and connected to three to five substantive, grounded priorities where evidence supports them.
Architecture: retain the existing canonical assessment and question checklist. Derive themed findings and priority links from admitted gaps and existing evidence IDs. Reuse recommendation compilation for one bounded correction only after an explicit revise verdict, with shared validation and independent re-review under the original deadline.
Tech stack: existing Python, JavaScript, pytest and browser/export tooling; no dependencies.

- [x] Reproduce revise suppression with offline pipeline fixtures, including correction success, rejection, timeout and cancellation.
- [x] Share normalization/validation between original and corrected candidates; preserve passed actions, scope, ranking and audit trail. No correction on block or unresolved targets.
- [x] Derive short thematic findings from canonical gaps, link to accepted priorities or evidence follow-up, and preserve full questions as supporting analysis.
- [x] Apply matching compact five-point ratings to browser and Python HTML/Word exports; keep overview text outside ratings.
- [x] Test canonical content preservation, ordering, links, unscored states and saved results. Inspect local rendered replay without invoking providers.
- [ ] Update reference docs, readiness status and parity notes; run focused checks then the required full suite, commit and push the existing draft branch.

Acceptance: no fabricated third recommendation or relaxed grounding. Saved runs retain their actual action count. Live analytical acceptance remains pending a separately authorized run; both additional paid runs are exhausted. Production and ITS rollout remain held.
