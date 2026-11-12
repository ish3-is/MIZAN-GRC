from datetime import date, timedelta
from pathlib import Path
import os
from sqlalchemy import select
from app.db import Session, Activity, Evidence
from app.methodology import risk_score
from conftest import login


def edit(client, a, status="Compliant"):
    result = client.put(
        f"/api/assessments/{a['id']}",
        json={
            "status": status,
            "rationale": "Sample inspected and documented with synthetic supporting evidence.",
            "version": a["version"],
        },
    )
    assert result.status_code == 200, result.text
    return result.json()


def upload(client, id, stale=False):
    due = (date.today() + timedelta(days=-1 if stale else 90)).isoformat()
    result = client.post(
        f"/api/assessments/{id}/evidence",
        files={
            "file": (
                "sample.txt",
                b"SYNTHETIC access review approval sample",
                "text/plain",
            )
        },
        data={"review_due": due},
    )
    assert result.status_code == 201, result.text
    return result.json()


def test_complete_vertical_slice(client):
    owner = login(client)
    c = client.get("/api/records/control").json()[0]
    asset = client.get("/api/records/asset").json()[0]
    a = client.post(
        "/api/assessments", json={"control_id": c["id"], "asset_id": asset["id"]}
    ).json()
    a = edit(client, a, "Non-Compliant")
    e = upload(client, a["id"])
    assert client.get(f"/api/evidence/{e['id']}/download").content.startswith(
        b"SYNTHETIC"
    )
    with Session() as s:
        stored = s.get(Evidence, e["id"])
        ciphertext = (
            Path(os.environ["EVIDENCE_DIR"]) / stored.storage_key
        ).read_bytes()
        assert b"SYNTHETIC" not in ciphertext
    login(client, "risk")
    risk = client.post(
        "/api/risks",
        json={
            "title": "Sensitive dataset investigation",
            "department": "Technology",
            "asset_id": asset["id"],
            "inherent_likelihood": 4,
            "inherent_impact": 5,
            "residual_likelihood": 2,
            "residual_impact": 4,
            "inherent_rationale": "Exposed synthetic dataset before access safeguards.",
            "control_effectiveness_rationale": "Access review sample indicates incomplete control operation.",
            "residual_rationale": "Independent assessment after proposed mitigations, subject to retest.",
            "treatment": "mitigate",
        },
    )
    assert risk.status_code == 201
    login(client)
    finding = client.post(
        "/api/findings",
        json={
            "assessment_id": a["id"],
            "risk_id": risk.json()["id"],
            "title": "Access governance evidence missing",
            "action": "Approve scoped access review and retest sampled permissions.",
            "owner_id": owner["id"],
            "due": "2027-01-01",
        },
    )
    assert finding.status_code == 201
    id = finding.json()["id"]
    assert (
        client.post(
            f"/api/findings/{id}/transition",
            json={
                "state": "Closed",
                "rationale": "Unreviewed closure must be blocked.",
            },
        ).status_code
        == 403
    )
    assert client.post(f"/api/assessments/{a['id']}/submit").status_code == 200
    login(client, "auditor")
    review = client.post(
        f"/api/assessments/{a['id']}/review",
        json={
            "decision": "approve",
            "rationale": "Evidence confirms a gap; noncompliant rating independently verified.",
        },
    )
    assert review.status_code == 200, review.text
    login(client)
    assert (
        client.post(
            f"/api/findings/{id}/transition",
            json={
                "state": "In Progress",
                "rationale": "Accountable owner begins corrective action.",
            },
        ).status_code
        == 200
    )
    a = client.post(f"/api/assessments/{a['id']}/reopen").json()
    edit(client, a)
    upload(client, a["id"])
    assert (
        client.post(
            f"/api/findings/{id}/transition",
            json={
                "state": "Ready for Retest",
                "rationale": "Corrective action completed; new sample attached.",
            },
        ).status_code
        == 200
    )
    assert client.post(f"/api/assessments/{a['id']}/submit").status_code == 200
    login(client, "auditor")
    assert (
        client.post(
            f"/api/assessments/{a['id']}/review",
            json={
                "decision": "approve",
                "rationale": "Independent retest confirms access review operates within sampled scope.",
            },
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/findings/{id}/transition",
            json={
                "state": "Closed",
                "rationale": "Independent retest and approved assessment support closure.",
            },
        ).status_code
        == 200
    )
    report = client.get("/api/reports/management").json()
    assert any(f["id"] == id and f["state"] == "Closed" for f in report["findings"])
    assert report["summary"]["risks"] == 41
    assert report["evidence_manifest"][-1]["sha256"]
    assert client.get("/api/activity/verify").json()["valid"] is True


def test_auth_rbac_csrf_and_sessions(client):
    assert client.get("/api/dashboard").status_code == 401
    login(client, "executive")
    assert client.get("/api/dashboard").status_code == 200
    assert (
        client.post(
            "/api/assessments", json={"control_id": 1, "asset_id": 1}
        ).status_code
        == 403
    )
    assert client.get("/api/activity").status_code == 403
    assert (
        client.post(
            "/api/logout", headers={"Origin": "https://evil.example"}
        ).status_code
        == 403
    )
    assert (
        client.post("/api/logout", headers={"X-Mizan-Request": ""}).status_code == 403
    )
    assert client.post("/api/logout").status_code == 200
    assert client.get("/api/me").status_code == 401


def test_validation_evidence_and_version_conflict(client):
    login(client)
    a = client.get("/api/assessments").json()[0]
    assert client.post(f"/api/assessments/{a['id']}/submit").status_code == 409
    updated = edit(client, a)
    assert (
        client.put(
            f"/api/assessments/{a['id']}",
            json={
                "status": "Compliant",
                "rationale": "Concurrent old version must fail.",
                "version": a["version"],
            },
        ).status_code
        == 409
    )
    assert (
        client.post(
            f"/api/assessments/{a['id']}/evidence",
            files={"file": ("bad.exe", b"bad")},
            data={"review_due": "2027-01-01"},
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"/api/assessments/{a['id']}/evidence",
            files={"file": ("bad.pdf", b"bad")},
            data={"review_due": "2027-01-01"},
        ).status_code
        == 422
    )
    upload(client, a["id"], True)
    assert client.post(f"/api/assessments/{a['id']}/submit").status_code == 200
    login(client, "auditor")
    assert (
        client.post(
            f"/api/assessments/{a['id']}/review",
            json={
                "decision": "approve",
                "rationale": "Stale evidence should block approval.",
            },
        ).status_code
        == 409
    )
    assert updated["version"] == a["version"] + 1


def test_separation_of_duties_and_tamper_detection(client):
    login(client, "manager")
    c = client.get("/api/records/control").json()[0]
    asset = client.get("/api/records/asset").json()[0]
    a = client.post(
        "/api/assessments", json={"control_id": c["id"], "asset_id": asset["id"]}
    ).json()
    edit(client, a, "Not Applicable")
    assert client.post(f"/api/assessments/{a['id']}/submit").status_code == 200
    assert (
        client.post(
            f"/api/assessments/{a['id']}/review",
            json={
                "decision": "approve",
                "rationale": "Attempt self approval should fail.",
            },
        ).status_code
        == 403
    )
    with Session() as s:
        e = s.scalar(select(Activity).order_by(Activity.id))
        e.action = "tampered"
        s.commit()
    assert client.get("/api/activity/verify").json()["valid"] is False


def test_seed_totals_and_formula_bounds(client):
    login(client)
    d = client.get("/api/dashboard").json()
    assert (d["risks"], d["assets"], d["compliance"]["eligible"]) == (40, 25, 5)
    assert d["compliance"]["score"] == 0
    assert d["compliance"]["verified"] == 0
    assert d["compliance"]["evidence_coverage"] == 0
    assert len(client.get("/api/records/vendor").json()) == 10
    assert len(client.get("/api/records/department").json()) == 5
    for l in range(1, 6):
        for i in range(1, 6):
            assert risk_score(l, i)["score"] == l * i
    import pytest

    with pytest.raises(ValueError):
        risk_score(0, 5)


def test_na_exclusion_requires_approval(client):
    login(client)
    a = client.get("/api/assessments").json()[0]
    edit(client, a, "Not Applicable")
    assert client.get("/api/dashboard").json()["compliance"]["eligible"] == 5
    client.post(f"/api/assessments/{a['id']}/submit")
    login(client, "auditor")
    assert (
        client.post(
            f"/api/assessments/{a['id']}/review",
            json={
                "decision": "approve",
                "rationale": "Documented scope exclusion reviewed and justified.",
            },
        ).status_code
        == 200
    )
    assert client.get("/api/dashboard").json()["compliance"]["eligible"] == 4


def test_evidence_tampering_blocks_download(client):
    login(client)
    a = client.get("/api/assessments").json()[0]
    e = upload(client, a["id"])
    with Session() as s:
        stored = s.get(Evidence, e["id"])
        (Path(os.environ["EVIDENCE_DIR"]) / stored.storage_key).write_bytes(b"tampered")
    assert client.get(f"/api/evidence/{e['id']}/download").status_code == 409


def test_login_rate_limit(client):
    for _ in range(10):
        assert (
            client.post(
                "/api/login", json={"username": "owner", "password": "wrong"}
            ).status_code
            == 401
        )
    assert (
        client.post(
            "/api/login", json={"username": "owner", "password": "wrong"}
        ).status_code
        == 429
    )


def test_audit_pack_contains_verified_evidence(client):
    import io, json, zipfile, hashlib

    login(client)
    a = client.get("/api/assessments").json()[0]
    e = upload(client, a["id"])
    assert client.get("/api/reports/audit-pack.zip").status_code == 403
    login(client, "auditor")
    response = client.get("/api/reports/audit-pack.zip")
    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        doc = manifest["evidence"][0]
        assert (
            doc["sha256"]
            == hashlib.sha256(archive.read(doc["path"])).hexdigest()
            == e["sha256"]
        )
        report = json.loads(archive.read("management-report.json"))
        assert report["source_references"][0]["payload"][
            "official_source_url"
        ].startswith("https://")


def test_risk_acceptance_and_assessor_ownership(client):
    login(client, "manager")
    a = client.get("/api/assessments").json()[0]
    assert (
        client.put(
            f"/api/assessments/{a['id']}",
            json={
                "status": "Compliant",
                "rationale": "Manager cannot act as another assessor.",
                "version": a["version"],
            },
        ).status_code
        == 403
    )
    asset = client.get("/api/records/asset").json()[0]
    risk = client.post(
        "/api/risks",
        json={
            "title": "Acceptance test scenario",
            "department": "Technology",
            "asset_id": asset["id"],
            "inherent_likelihood": 3,
            "inherent_impact": 3,
            "residual_likelihood": 2,
            "residual_impact": 2,
            "inherent_rationale": "Initial test risk assessment rationale.",
            "control_effectiveness_rationale": "Independent control operation test rationale.",
            "residual_rationale": "Residual judgment requires future review.",
            "treatment": "accept",
        },
    ).json()
    data = {
        "rationale": "Authorized risk acceptance with future review.",
        "review_date": (date.today() + timedelta(days=90)).isoformat(),
    }
    assert client.post(f"/api/risks/{risk['id']}/accept", json=data).status_code == 409
    login(client, "risk")
    assert client.post(f"/api/risks/{risk['id']}/accept", json=data).status_code == 403
