import csv
import io
import json
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path
from fastapi import Depends, Response
from sqlalchemy import select, func
from .db import Record, Assessment, Evidence, Finding, now
from .methodology import metrics, risk_score
from .core import lock, app, db, actor, permit, activity
from .registry import records
from .compliance import assessments
from .remediation import findings
from .evidence import evidence, decrypt_evidence


@app.get("/api/dashboard")
def dashboard(user=Depends(actor), s=Depends(db)):
    aa = list(s.scalars(select(Assessment)))
    ee = list(s.scalars(select(Evidence)))
    ff = list(s.scalars(select(Finding)))
    rr = list(s.scalars(select(Record).where(Record.kind == "risk")))
    counts = defaultdict(int)
    for e in ee:
        counts[e.assessment_id] += 1
    today = date.today().isoformat()
    return {
        "compliance": metrics(aa, counts),
        "risks": len(rr),
        "assets": s.scalar(select(func.count(Record.id)).where(Record.kind == "asset")),
        "open_findings": sum(f.state != "Closed" for f in ff),
        "overdue": sum(f.state != "Closed" and f.due < today for f in ff),
        "stale_evidence": sum(e.review_due < today for e in ee),
        "heatmap": [
            {
                "id": r.id,
                "likelihood": r.payload["residual_likelihood"],
                "impact": r.payload["residual_impact"],
                **risk_score(
                    r.payload["residual_likelihood"], r.payload["residual_impact"]
                ),
            }
            for r in rr
        ],
        "timestamp": now(),
    }


@app.get("/api/reports/management")
def management(user=Depends(actor), s=Depends(db)):
    summary = dashboard(user, s)
    return {
        "title": "MIZAN management report / تقرير الإدارة",
        "scope": "Synthetic Mizan Services; 2026-Q4; selected ECC controls only",
        "owner": user.username,
        "limitations": "Self-assessment and internal review; not regulatory certification, approval or legal advice. No claim of full ECC or PDPL coverage.",
        "summary": summary,
        "assessments": assessments(user, s),
        "findings": findings(user, s),
        "source_references": records("source", user, s),
        "controls": records("control", user, s),
        "evidence_manifest": evidence(user, s),
    }


@app.get("/api/reports/risks.csv")
def export_csv(user=Depends(actor), s=Depends(db)):
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(
        [
            "id",
            "title",
            "department",
            "inherent",
            "residual",
            "treatment",
            "exported_at",
        ]
    )
    for r in s.scalars(select(Record).where(Record.kind == "risk")):
        p = r.payload
        safe = lambda value: (
            "'" + value
            if isinstance(value, str)
            and value.startswith(("=", "+", "-", "@", "\t", "\r"))
            else value
        )
        writer.writerow(
            [
                r.id,
                safe(r.title),
                safe(r.department),
                p["inherent_likelihood"] * p["inherent_impact"],
                p["residual_likelihood"] * p["residual_impact"],
                p["treatment"],
                now(),
            ]
        )
    return Response(
        "\ufeff" + out.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="mizan-risks.csv"'},
    )


@app.get("/api/reports/audit-pack.zip")
def audit_pack(user=Depends(actor), s=Depends(db)):
    permit(user, {"Super Admin", "GRC Manager", "Internal Auditor"})
    report = management(user, s)
    output = io.BytesIO()
    manifest = []
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "management-report.json", json.dumps(report, ensure_ascii=False, indent=2)
        )
        for e in s.scalars(select(Evidence).order_by(Evidence.id)):
            content = decrypt_evidence(e)
            filename = f"evidence/{e.id}{Path(e.filename).suffix.lower()}"
            archive.writestr(filename, content)
            manifest.append(
                {
                    "path": filename,
                    "original_name": e.filename,
                    "sha256": e.sha256,
                    "assessment_id": e.assessment_id,
                    "created": e.created,
                    "review_due": e.review_due,
                }
            )
        archive.writestr(
            "manifest.json",
            json.dumps(
                {
                    "exported_at": now(),
                    "scope": report["scope"],
                    "exporter": user.username,
                    "evidence": manifest,
                },
                indent=2,
            ),
        )
        archive.writestr(
            "README.txt",
            "MIZAN synthetic audit pack. Evidence is decrypted for this authorized export. Protect the archive. Source references and verification states are in management-report.json. Internal assessment is not certification, regulatory approval or legal advice. No full proprietary standards are included.",
        )
    with lock:
        activity(
            s,
            user,
            "report.audit_pack_exported",
            "organization",
            {"documents": len(manifest)},
        )
        s.commit()
    return Response(
        output.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="mizan-audit-pack.zip"'},
    )
