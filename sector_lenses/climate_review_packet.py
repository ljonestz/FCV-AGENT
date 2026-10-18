"""Package a validated Climate draft for approval in an external workflow."""
from io import BytesIO
import hashlib
import json
from zipfile import ZIP_DEFLATED, ZipFile

from sector_lenses.climate_verified_render import render_reader_html, write_reader_docx


INSTRUCTIONS = """EXTERNAL HUMAN REVIEW

This packet is a draft, not an approval. The app has not authenticated a reviewer.
1. Preserve this packet. Obtain the original project/context documents and verify
   their versions against the supplied metadata. Original uploads are not bundled;
   missing provenance or unavailable sources must be resolved before approval.
2. Review all consequential claims, including unflagged claims, and the premises
   behind recommendations. Check status, funding/recipient scope, sites/populations,
   safeguards, quantities/dates, causal benefits and policy applicability. Preserve
   valid qualified advice. Minor wording inconsistencies need not block release.
3. Record unresolved consequential issues and their dispositions. Do not approve
   while any major issue remains unresolved. A model pass is not human sign-off.
4. If corrections are needed, change the canonical assessment and regenerate the
   packet. Do not approve a Word-only edit against the old snapshot. A changed
   report, source set or model/prompt version requires a new packet and review.
5. Use review_record_template.json as a checklist. In your existing authenticated
   organisational workflow record the actual reviewer identity, decision, time,
   snapshot_sha256 and hashes of the exact files approved. Attach the packet.
   Preserve that workflow's permanent record/reference with the shared report.
6. Before sharing, compare actual file SHA-256 hashes with those recorded in the
   authenticated approval, not just the editable manifest inside this ZIP.
   On PowerShell: Get-FileHash -Algorithm SHA256 -LiteralPath './report.docx'
   Repeat for report.html and snapshot.json. Any mismatch invalidates use of that
   approval for the changed files. A new packet never inherits an older approval.

The app always labels these exports as drafts: external approval does not change
app status. Share the approved files together with the external approval reference.
A name typed into the template is not authenticated. Checksums detect changes;
they are not signatures and do not establish source accuracy or reviewer identity.
"""


def _json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def build_review_packet(assessment: dict, snapshot: dict) -> bytes:
    """Called only after the route has validated the assessment/reader pair."""
    digest = snapshot["sha256"]
    reader = snapshot["reader"]
    docx = BytesIO()
    write_reader_docx(reader, docx, snapshot_sha256=digest)
    page = ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Climate-FCV draft for human review</title>'
            '<style>body{font:16px/1.55 system-ui,sans-serif;max-width:960px;'
            'margin:32px auto;padding:0 24px}table{border-collapse:collapse}'
            'td,th{padding:8px;border:1px solid #ccc}p{overflow-wrap:anywhere}'
            '</style></head><body>'
            + render_reader_html(reader, snapshot_sha256=digest) + '</body></html>')
    files = {"report.docx": docx.getvalue(), "report.html": page.encode("utf-8"),
             "snapshot.json": _json_bytes({"assessment": assessment, "reader": reader})}
    # Assert the packaged inputs are exactly those checked by the export gate.
    if hashlib.sha256(files["snapshot.json"]).hexdigest() != digest:
        raise ValueError("Review packet does not match the validated snapshot")
    hashes = {name: hashlib.sha256(value).hexdigest() for name, value in files.items()}
    manifest = {"schema_version": "climate-external-review-v1", "status": "draft",
                "publication_approved": False, "snapshot_sha256": digest, "files": hashes}
    record = {"snapshot_sha256": digest, "files": hashes, "decision": "pending",
              "reviewer_name": None, "decision_timestamp": None,
              "authenticated_workflow_record": None,
              "consequential_claims_including_unflagged_checked": False,
              "recommendation_premises_checked": False,
              "original_sources_and_versions_checked": False,
              "unresolved_major_issues": None, "minor_issues": [], "review_notes": None}
    files.update({"manifest.json": _json_bytes(manifest),
                  "review_record_template.json": _json_bytes(record),
                  "REVIEW_INSTRUCTIONS.txt": INSTRUCTIONS.encode("utf-8")})
    output = BytesIO()
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return output.getvalue()
