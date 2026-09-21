# Production-readiness design: Climate recommendation routing

**Date:** 2026-08-14
**Status:** Approved direction, implementation pending

## Problem

The Somalia DPF PID smoke and quality runs each produced four climate
recommendation candidates, then suppressed all four with
`DRAFTING_CURRENT_TARGET_INVALID`. The verified pipeline returned HTTP 200 and
the reader described the Recommendations Note as generated even though it
contained no ranked recommendations.

The immediate cause is incomplete coverage in the operational-guidance
registry. It supports DPF Program Documents but not DPF PIDs. The broader route
matrix shows equivalent gaps for several other supported document and
instrument combinations. A one-route patch would leave the same failure mode
elsewhere.

## Required outcome

Every supported Climate Preview preparation or mid-cycle route must either:

1. receive instrument-appropriate guidance with valid targets in the current
   document and be capable of returning grounded recommendations; or
2. stop visibly as an incomplete/unsupported recommendation analysis.

The application must never report a Recommendations Note as successfully
generated when recommendation candidates existed but all were suppressed.

## Supported route matrix

| Base instrument | Documents requiring recommendation support |
|---|---|
| IPF | PCN, PID, PAD, Project Paper, Additional Financing, Restructuring Paper |
| DPF/DPO | PCN, PID, PAD, Program Document |
| PforR/P4R | PCN, PID, PAD, Program Paper |
| MPA | Overlay on any supported base-instrument route above when the base instrument is resolved |

`Unknown`, unresolved MPA base instruments, TA, and ISR/implementation-review
routes are not silently converted into a supported preparation route. They
remain fail-closed and must show a clear unsupported/incomplete status if
recommendations cannot be safely produced.

## Design

### 1. Complete the guidance registry

Extend the existing instrument-specific guidance entries with the missing
current-document types and their real section families. Reuse existing guidance
IDs and validation behavior where the analytical route is the same. Add a new
entry only when a distinct lifecycle document requires materially different
targets.

The registry remains non-authoritative: it provides bounded drafting locations,
not policy mandates. DPF targets remain prior-action, distributional,
environmental/natural-resource, policy-program, and results oriented. PforR
targets remain program design, ESSA/PAP, DLI, results, and verification oriented.
IPF targets remain project design, implementation, risk, E&S, and results
oriented. MPA adds the program/phase layer without replacing the base route.

### 2. Keep target validation strict

The validator continues to require drafting in the current document. It may
canonicalize a section-label variant only when cited registered guidance maps it
unambiguously to a valid current-document target. It will not broadly retarget
recommendations to arbitrary sections merely to preserve a non-zero count.

### 3. Add a fail-loud invariant

When the compiler returns one or more parseable recommendation candidates but
the final priority count is zero, the pipeline records a bounded
`RECOMMENDATIONS_ALL_SUPPRESSED` condition. The reader must not display the
normal generated/ready state. It must display that the recommendation stage is
incomplete and direct the user to rerun or seek support, while retaining
privacy-safe reason codes for diagnosis.

A genuinely evidence-free run may still return no recommendations when there
were no viable candidates. That state must be distinguished from candidates
being generated and then rejected.

### 4. Verification

Automated checks will cover:

- every supported route in the matrix has a non-empty, instrument-correct
  guidance packet;
- every registered target belongs to the current document type;
- DPF guidance excludes IPF and PforR terminology;
- PforR guidance excludes IPF/ESF routing;
- MPA always retains its resolved base-instrument guidance;
- a Somalia-style DPF PID candidate survives normalization and validation;
- an all-suppressed compiler result produces the fail-loud condition and cannot
  render the normal ready state;
- unresolved routes remain fail-closed;
- existing full-suite behavior remains green.

Representative local QA files will cover IPF, DPF PID, DPF Program Document,
PforR PID/PAD, and MPA PID/PAD routes. After deployment, bounded live runs will
verify the original Somalia case on both Render smoke and quality services and
at least one representative route for each other base instrument, subject to
the configured run limits and API availability.

## Production-readiness acceptance criteria

- Original Somalia DPF PID produces at least one ranked priority in smoke and
  quality modes.
- Render diagnostics show non-zero `valid_candidate_count` and
  `final_priority_count` for those runs.
- No supported route has an empty guidance packet.
- All-suppressed runs are visibly incomplete, never falsely successful.
- Targeted regression tests and the full test suite pass from a clean branch.
- Final diff contains no unrelated changes or secrets.
- The deployed commit matches the tested commit.
- ITS handover records the supported matrix, known exclusions, rollback point,
  tests, live evidence, and any residual limitations.

## Limitations

No finite test suite can prove the absence of every future model or
infrastructure failure. Production readiness here means complete known-route
coverage, strict validation, explicit handling of suppression failures,
representative live verification, and diagnostic evidence sufficient to fail
safely when an unanticipated condition occurs.
