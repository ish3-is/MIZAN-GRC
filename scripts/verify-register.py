"""Validate provenance completeness without claiming legal correctness."""

import json
from pathlib import Path
from urllib.parse import urlparse

root = Path(__file__).resolve().parents[1]
rows = json.loads((root / "regulatory/sources.json").read_text(encoding="utf-8"))
required = {
    "framework_id",
    "publisher",
    "official_source_url",
    "source_title",
    "version",
    "effective_date",
    "last_verified_date",
    "legal_applicability",
    "exact_reference_id",
    "source_excerpt",
    "requirement_summary",
    "interpretation",
    "implementation_guidance",
    "evidence_requirements",
    "verification_status",
}
for row in rows:
    assert required <= row.keys(), (row.get("framework_id"), required - row.keys())
    host = urlparse(row["official_source_url"]).hostname
    assert host and (host.endswith(".gov.sa") or host == "www.iso.org"), host
    assert row["source_excerpt"] is None, (
        "Excerpts require an explicit licensing review"
    )
    assert row["verification_status"] in {
        "UNVERIFIED",
        "SOURCE_ACCESSED",
        "METADATA_VERIFIED",
        "REFERENCE_VERIFIED",
    }
assert len({r["framework_id"] for r in rows}) == len(rows)
print(
    f"{len(rows)} source records passed provenance structure and publisher-host checks. This does not verify legal meaning or source currency."
)
