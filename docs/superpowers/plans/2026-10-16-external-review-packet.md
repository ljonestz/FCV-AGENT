# External review packet implementation plan

Approved boundary: user selected an existing authenticated organisational workflow
on 2026-10-16. The app prepares a version-bound packet, not authenticated approval.

Design: reuse the existing exact assessment/reader snapshot check. Add a Climate
review-packet ZIP endpoint and download control. Include Detailed HTML, Word,
snapshot JSON, checksum manifest, blank named-review template and instructions.
Bind the full normalized assessment/reader to the existing snapshot SHA-256 and
hash the actual report files. The external workflow records reviewer identity,
decision, timestamp, unresolved major issues, snapshot ID and artifact checksums.
No signing token, claimed identity, approval import, login or database is added.
The original source files are not automatically bundled. Any missing source access
or provenance must be resolved by the reviewer. Raw packets stay outside Git.

Render draft status unconditionally in Climate Summary, Detailed, HTML and Word.
A client-supplied approval flag cannot remove it. External approval is recorded
separately and never upgrades the app's publication_approved=false. Changes require
a new packet and external review; hashes detect drift but do not authenticate it.
Keep the existing analytical text, ratings and source evidence unchanged.

- [x] Add failing route, artifact-hash, tamper and draft-status tests.
- [x] Build packet with standard-library ZIP/JSON/hash tools and existing renderers.
- [x] Wire the gated browser download; test failure and changed-report cases.
- [x] Run focused checks, review actual artifacts/diff, then full UTF-8 suite.
- [x] Record limitations and verification, commit and push existing draft PR branch.

## Verification record

The initial route test failed with 404 before implementation. Packet/export/gap
checks: 25 passed. Connected packet/renderer/routes: 187 passed after updating the
existing Word first-paragraph assertion to require draft status followed by the
unchanged country-evidence warning. Tests verify snapshot and actual artifact
hashes, empty review identity/pending decision, changed versions, rejected reader
drift, forged approval flags, browser error/race handling and button restoration.
Read-only code review found no blocking defect. Full UTF-8 suite: 1,732 passed in 1,605.74 seconds (26:45), with normal process permissions.
A synthetic generated ZIP and extracted artifacts are retained locally under
output/20261016-external-review-packet/; they are QA artifacts, not approved reports.
No live service test, provider call, authenticated sign-off or deployment is claimed.

Headless Edge artifact check passed at 1100px and 390px widths. Both screenshots
were inspected: draft status and full snapshot ID are legible, the phone layout
has no horizontal overflow. Local screenshots: packet-desktop.png and
packet-phone.png in the artifact directory above. DOCX content and checksum were
validated programmatically; no Word visual-layout verification is claimed.
