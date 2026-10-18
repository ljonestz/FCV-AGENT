# Targeted verification notes implementation plan

Approved scope: retain unresolved prose with a precise nearby verification note;
remove a clearly defective sentence only when its remainder is independently useful;
otherwise withhold the affected argument. Apply to opening, all core answers and
recommendations. Invalid or missing reviews and block remain closed. No paid calls
or deployment. Existing tested archive remains unchanged.

1. Add failing tests for explicit review dispositions, unique quote anchors,
   sentence removal, malformed reviews, exports and recommendation re-review.
2. Extend existing review issue contracts with disposition and verification note.
   Legacy findings retain their old handling. Keep one bounded repair and re-review.
3. Apply display disposition centrally, preserving original prose and raw verdict
   in the assessment. Notes travel through existing escaped prose renderers into
   browser, standalone HTML, Word and snapshot binding. Recommendations retained
   after re-review remain marked and cannot support the final reader as accepted facts.
4. Allow three core-answer paragraphs and target 180-240 words where supported;
   keep 400-word hard ceiling and align generation/correction/schema/renderer.
5. Run focused tests, full suite excluding the four documented browser hangs,
   and saved-case offline export review. Update handoff and private parity status;
   commit/push only source/tests/docs. No generated reports or pre-existing test.

Completed offline: 1866 passed, four documented exclusions; saved-case Edge/Word
preview verified. No provider calls or deployments.
