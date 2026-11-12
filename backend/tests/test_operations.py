from app.methodology import risk_score
from conftest import login


def test_operating_system_seed_and_kpis(client):
    login(client, "manager")
    assert len(client.get("/api/work-items?domain=policy").json()) == 16
    assert len(client.get("/api/work-items?domain=privacy").json()) == 8
    assert len(client.get("/api/work-items?domain=vendor").json()) == 5
    assert len(client.get("/api/work-items?domain=incident").json()) == 3
    assert len(client.get("/api/work-items?domain=gap").json()) == 12
    assert len(client.get("/api/work-items?domain=remediation").json()) == 12
    assert len(client.get("/api/work-items?domain=evidence").json()) == 10
    dashboard = client.get("/api/dashboard").json()
    assert dashboard["risks"] == 18
    assert dashboard["open_gaps"] == 10
    assert dashboard["policy_acknowledgement"] == {
        "acknowledged": 7,
        "assigned": 10,
        "rate": 70.0,
    }
    assert dashboard["overdue_remediation"] == 3


def test_work_item_lifecycle_and_separation_of_duties(client):
    login(client, "manager")
    users = {item["username"]: item for item in client.get("/api/users").json()}
    created = client.post(
        "/api/work-items",
        json={
            "domain": "governance",
            "record_type": "decision",
            "title_ar": "قرار حوكمة تجريبي",
            "title_en": "Synthetic governance decision",
            "owner_id": users["manager"]["id"],
            "reviewer_id": users["analyst"]["id"],
            "approver_id": users["auditor"]["id"],
            "payload": {"decision": "Approve a fictional review scope"},
        },
    )
    assert created.status_code == 201, created.text
    item = created.json()
    assert (
        client.post(
            f"/api/work-items/{item['id']}/transition",
            json={"status": "Under Review", "rationale": "Owner submits the documented decision for independent review."},
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/work-items/{item['id']}/transition",
            json={"status": "Approved", "rationale": "The owner must not approve the decision they submitted."},
        ).status_code
        == 403
    )
    login(client, "auditor")
    approved = client.post(
        f"/api/work-items/{item['id']}/transition",
        json={"status": "Approved", "rationale": "Independent reviewer confirms scope and accountable ownership."},
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "Approved"
    assert len(approved.json()["approvals"]) == 2


def test_remediation_closure_requires_evidence_and_verification(client):
    login(client, "manager")
    item = next(
        row for row in client.get("/api/work-items?domain=remediation").json()
        if row["status"] == "Pending Verification" and not row["payload"]["completion_evidence_ids"]
    )
    login(client, "auditor")
    response = client.post(
        f"/api/work-items/{item['id']}/transition",
        json={"status": "Closed", "rationale": "Attempting closure without evidence must be rejected."},
    )
    assert response.status_code == 409


def test_required_risk_bands():
    assert risk_score(1, 4)["band"] == "Low"
    assert risk_score(1, 5)["band"] == "Moderate"
    assert risk_score(2, 5)["band"] == "High"
    assert risk_score(4, 4)["band"] == "High"
    assert risk_score(5, 4)["band"] == "Critical"


def test_super_admin_role_change_and_self_change_guard(client):
    login(client, "admin")
    users = {item["username"]: item for item in client.get("/api/users").json()}
    changed = client.put(
        f"/api/users/{users['analyst']['id']}/role",
        json={"role": "Executive Viewer"},
    )
    assert changed.status_code == 200
    assert changed.json()["role"] == "Executive Viewer"
    assert (
        client.put(
            f"/api/users/{users['admin']['id']}/role",
            json={"role": "Executive Viewer"},
        ).status_code
        == 409
    )
