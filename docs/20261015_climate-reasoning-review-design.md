# Reasoning-enabled reviewer comparison

## Approved objective and decision

The user approved proceeding with a different factual-review approach after the
explicit-premise check failed. Preserve qualified analysis and test against the
corrected source adjudication. Do not deploy or start another full assessment.

Three options were considered: add clause classification to the same reviewer;
construct a separate source-relationship ledger then compare claims; or first test
the existing reviewer with up-front reasoning enabled. The ledger could clarify
relationships but adds source extraction, coverage checks and model calls. The
client currently explicitly suppresses up-front thinking for semantic reviews,
treating them as deterministic extraction. Test this smaller execution change
before adding a new review architecture or further prompt restrictions.

This is a hypothesis, not a diagnosis established by experiment. Provider docs
confirm the setting's behavior, not that changing it fixes these cases.

## Isolated experiment

- Keep the exact saved full-context case bytes, model, prompts, native schemas and
  final-answer word constraint from candidate8b1039c. No expected labels in input.
- Change only the experimental request configuration: adaptive thinking, high
  effort, omitted thinking display, 8,192 total output tokens and 180-second timeout.
  The previous calls used between_tools, 2,500 tokens and 120 seconds. The larger
  budget accompanies reasoning; this is not a one-variable causal experiment.
- Maximum two reviewer-only calls, zero SDK/application retries. Explicit paid
  invocation required; default mode only prepares request JSON. One exclusive
  output directory/start lock prevents accidental repeat execution.
- Preserve parsed response and usage per call. Record whether thinking blocks were
  returned, without persisting their content/signatures. Truncation or malformed
  responses fail; never extend the budget or retry silently.
- Keep runtime client, prompts, schemas, call budgets and production unchanged.
  This prototype is a script with fake-SDK regression tests, not a new app path.

## Acceptance

Use a new adjudicated manifest alongside, never overwriting, historical labels.
Core001/005 must fail for study/funding scope; core002/003/004 remain eligible.
Reader dividends must identify planned-versus-delivered status; inclusion must
narrow the exclusion-specific safeguard claim. SUM001/002 remain valid. Design's
works/resources precision may be suggested, but not treated as a reason to discard
supported analysis. Only readiness002 is a material inconsistency; rounded figures
are not contradictions. Check exact objection targets, reason and cited sources,
not just object-level accept/reject agreement. One passing sample is still not a
reliability estimate or a substitute for a full correction/re-review acceptance.

If the experiment fails, stop paid calls and retain the result. If it improves,
record the remaining defects rather than calling it production ready. Integrating
reasoning into the app would require separate timeout/streaming/cost consideration
and successful full correction and export acceptance.

## References

Provider thinking behavior and output-budget accounting:
https://platform.claude.com/docs/en/build-with-claude/thinking
Current reasoning and structured-output guidance:
https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

Local evidence: climate_verified_client.py explicitly sends between_tools for
Sonnet/Opus, supplies no tools, and documents that this suppresses up-front thinking.
The prior response metrics confirm that configuration for both reviewed calls.
