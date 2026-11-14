"""Export the synthetic database into a read-only GitHub Pages showcase."""

import csv
import io
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path

from cryptography.fernet import Fernet
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
EXPORT_TEMP = tempfile.TemporaryDirectory(prefix="mizan-pages-")


def configure_export_environment():
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key, value)
    temporary_root = Path(EXPORT_TEMP.name)
    os.environ["DATABASE_URL"] = (
        f"sqlite:///{(temporary_root / 'mizan-pages.db').as_posix()}"
    )
    os.environ["EVIDENCE_DIR"] = str(temporary_root / "evidence")
    os.environ["EVIDENCE_KEY"] = Fernet.generate_key().decode()


configure_export_environment()
sys.path.insert(0, str(ROOT / "backend"))

from app.audit import audit_log, verify_log  # noqa: E402
from app.compliance import assessments  # noqa: E402
from app.db import Base, Record, Session, User, engine  # noqa: E402
from app.evidence import evidence  # noqa: E402
from app.operations import acknowledgements, relationships, work_items  # noqa: E402
from app.registry import records  # noqa: E402
from app.remediation import findings  # noqa: E402
from app.reporting import dashboard, management  # noqa: E402
from app.seed import seed  # noqa: E402


def main():
    output = ROOT / "frontend" / "public"
    downloads = output / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(engine)
    seed()
    try:
        with Session() as session:
            admin = session.scalar(select(User).where(User.username == "admin"))
            if not admin:
                raise SystemExit(
                    "The deterministic demonstration seed did not create admin"
                )
            kinds = list(
                session.scalars(select(Record.kind).distinct().order_by(Record.kind))
            )
            payload = {
                "generated_from": "MIZAN deterministic synthetic seed",
                "showcase_mode": "read-only",
                "users": [
                    {"id": user.id, "username": user.username, "role": user.role}
                    for user in session.scalars(select(User).order_by(User.id))
                ],
                "dashboard": dashboard(admin, session),
                "records": {kind: records(kind, admin, session) for kind in kinds},
                "assessments": assessments(admin, session),
                "evidence": evidence(admin, session),
                "findings": findings(admin, session),
                "work_items": work_items(None, None, None, admin, session),
                "policy_acknowledgements": acknowledgements(None, admin, session),
                "relationships": relationships(None, None, admin, session),
                "activity": audit_log(admin, session),
                "activity_verify": verify_log(admin, session),
                "management_report": management(admin, session),
            }
    finally:
        engine.dispose()
        EXPORT_TEMP.cleanup()

    (output / "demo-data.json").write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    risks = payload["records"].get("risk", [])
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["id", "title", "department", "inherent", "residual", "treatment"])
    for risk in risks:
        data = risk["payload"]
        writer.writerow(
            [
                risk["id"],
                risk["title"],
                risk["department"],
                data["inherent_likelihood"] * data["inherent_impact"],
                data["residual_likelihood"] * data["residual_impact"],
                data["treatment"],
            ]
        )
    (downloads / "mizan-demo-risks.csv").write_text(
        "\ufeff" + csv_buffer.getvalue(), encoding="utf-8"
    )

    notice = (
        "MIZAN GRC synthetic evidence placeholder.\n"
        "The GitHub Pages showcase is read-only and contains no uploaded evidence "
        "or real personal data. Run the FastAPI backend locally for encrypted evidence workflows.\n"
    )
    (downloads / "synthetic-evidence.txt").write_text(notice, encoding="utf-8")
    with zipfile.ZipFile(
        downloads / "mizan-demo-audit-pack.zip", "w", zipfile.ZIP_DEFLATED
    ) as archive:
        archive.writestr("README.txt", notice)
        archive.writestr(
            "management-report.json",
            json.dumps(payload["management_report"], ensure_ascii=False, indent=2),
        )
        archive.writestr(
            "manifest.json",
            json.dumps(
                {
                    "mode": "GitHub Pages read-only showcase",
                    "synthetic": True,
                    "evidence_files_included": 0,
                    "limitation": "Not certification, regulatory approval or legal advice.",
                },
                indent=2,
            ),
        )

    print(
        f"Exported {len(kinds)} record types, {len(payload['work_items'])} work items "
        f"and {len(payload['assessments'])} assessments to {output / 'demo-data.json'}"
    )


if __name__ == "__main__":
    main()
