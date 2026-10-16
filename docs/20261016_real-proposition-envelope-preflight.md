# Real replay envelope v2: offline verified, UNSENT

The user approved simplifying the response envelope after the 102-key provider
schema was rejected. This changes transport only; no paid call was made.

The provider schema now requires one string, judgments_json (135 serialized bytes,
down from 6,791). Its decoded value is an object containing all 66 proposition
judgments and 36 parent decisions as objects. Provider grammar no longer enforces
individual ID coverage. Local decoding rejects missing, extra or duplicate IDs,
and the unchanged evaluator validates every inner object and evidence quote.
Incomplete output remains a failed evaluation, with no automatic repair or retry.

The semantic prompt, all source and reader context, exact proposition spans, expected
labels, severity rules and parent handling rules are unchanged. Only the output
instruction differs. Input files are byte-identical to the previous attempt. The
previous scorer is reused and its file hash pinned for scoring. Original artifacts,
failed response, previous command and consumed lock remain untouched.

## Offline checks

31 unittest executions passed in 0.149 seconds (18 distinct behaviors; inherited
base tests run in both classes). New checks cover envelope round-trip, incomplete
and extra coverage, duplicate inner keys and malformed inner JSON. Existing checks
retain missed-major detection, false-premise parent blocking, minor-label tolerance,
fabricated/cross-case quote rejection, wrong binding, truncation and role escape.

Also checked the complete 102-ID transport round-trip; empty inner judgments still
fail strong validation. This is a mechanical test, not a simulated model pass.
Verified byte-identical frozen inputs, unchanged semantic prompt/input sections,
required ID equality, exact packaged-command/request equality, runner compilation
and exact reuse of the previously mock-tested runner template. No new SDK call or
live schema probe occurred. Provider acceptance and sufficient output budget remain
unproven until an authorized call completes.

## Prepared artifacts

Local, uncommitted:
- output/20261016_real_proposition_envelope.py
- output/20261016_test_real_envelope.py
- output/20261016-real-proposition-envelope-v2/: reviewer_inputs.json, expected.json,
  request.json, manifest.json, run_command.sh, offline_validation.json.

Experiment: `real-proposition-envelope-v2-b56105370523ac5c`.
Request SHA256: `443f7dd3ff1ce0a627b8fed3ed0ad9b8b44e35aecac7596cd04c1e58b8e6c507`.
Prompt SHA256: `2e35c553294462e13f985ee95ea557cf42336e80da6ae42d45158042e7fef7b1`.
Schema SHA256: `9a6918fcc48166cfc8d2c9b01b15fcec3177a6575011fbeff4cf0c30bca9cc0d`.
Command: 33,729 bytes; use chunked paste then one Enter on Windows.

## Next live boundary

A separately approved single Render-shell call would retain claude-sonnet-5-5,
adaptive/high, 16,384 output-token cap, 300-second timeout and zero retries. Verify
service/session and absence of the new exclusive lock before submission:
`/tmp/real-proposition-envelope-v2-b56105370523ac5c/started.lock`.
The runner checks payload/prompt/schema hashes and saves any provider error before
emitting the response envelope. One attempt consumes the lock, including rejection
or truncation. No fallback, correction-generation call or full assessment is included.

After capture, score offline with:

```powershell
& 'C:\WBG\Python313\python.exe' -X utf8 output/20261016_real_proposition_envelope.py score output/20261016-real-proposition-envelope-v2/response_blob.txt
```

Review actual evidence reasoning after scoring. Report real-case defects separately
from synthetic calibration, additional major findings, protected analysis and minor
label differences. No runtime changes, deployment, merge or publication.
publication_approved remains false. Previous paid authority is consumed; this
request has not been submitted.
