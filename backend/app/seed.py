"""Explicit deterministic demo seed; secrets supplied locally, never hardcoded."""

import json
import os
from pathlib import Path
from sqlalchemy import select
from argon2 import PasswordHasher
from .db import Session, Record, User, Assessment, Finding

ROLES = {
    "admin": "Super Admin",
    "manager": "GRC Manager",
    "compliance": "Compliance Officer",
    "risk": "Risk Manager",
    "privacy": "Privacy Officer",
    "owner": "Control Owner",
    "auditor": "Internal Auditor",
    "executive": "Executive Viewer",
}
DEPARTMENTS = ["Technology", "Human Resources", "Finance", "Operations", "Governance"]


def seed():
    password = os.environ.get("DEMO_PASSWORD")
    if not password or len(password) < 14:
        raise RuntimeError("Set a local DEMO_PASSWORD of at least 14 characters")
    with Session() as s:
        if s.scalar(select(User.id).limit(1)):
            return
        users = {}
        for name, role in ROLES.items():
            u = User(username=name, role=role, password=PasswordHasher().hash(password))
            s.add(u)
            s.flush()
            users[name] = u

        def add(kind, title, payload, department="Governance"):
            r = Record(kind=kind, title=title, department=department, payload=payload)
            s.add(r)
            s.flush()
            return r

        source_path = (
            Path(__file__).resolve().parents[2] / "regulatory" / "sources.json"
        )
        if not source_path.exists():
            source_path = Path("/app/regulatory/sources.json")
        sources = json.loads(source_path.read_text(encoding="utf-8"))
        for source in sources:
            add("source", source["source_title"], source)
        for dep in DEPARTMENTS:
            add("department", dep, {"synthetic": True, "owner_role": "GRC Manager"})
        add(
            "configuration",
            "Mizan Services / خدمات ميزان",
            {
                "synthetic": True,
                "period": "2026-Q4",
                "risk_appetite": 9,
                "scope": "Single Saudi private services demonstration organization",
                "assessment_weight": "equal",
                "likelihood": [
                    "Rare: exceptional initiating conditions",
                    "Unlikely: limited opportunity",
                    "Possible: credible conditions",
                    "Likely: recurring exposure",
                    "Almost certain: active/repeated exposure",
                ],
                "impact": [
                    "Minor: local reversible disruption",
                    "Limited: department impact",
                    "Material: multiple process impact",
                    "Major: essential service or sensitive data harm",
                    "Severe: sustained organization-wide harm",
                ],
                "note": "Organizational demo criteria, not regulatory thresholds.",
            },
        )
        assets = []
        for i in range(25):
            dep = DEPARTMENTS[i % 5]
            assets.append(
                add(
                    "asset",
                    [
                        "Employee records",
                        "Customer portal",
                        "Finance ledger",
                        "Supplier exchange",
                        "Policy repository",
                    ][i % 5]
                    + f" {i // 5 + 1:02}",
                    {
                        "synthetic": True,
                        "owner_id": users["owner"].id,
                        "classification": "Unclassified"
                        if i % 6 == 0
                        else "Confidential",
                        "location": "Saudi Arabia",
                        "process": "Shared services",
                        "personal_data": i % 3 == 0,
                    },
                    dep,
                )
            )
        for i in range(10):
            add(
                "vendor",
                f"Synthetic supplier {i + 1:02}",
                {
                    "synthetic": True,
                    "service": "Managed business services",
                    "risk_review": "Overdue" if i in (1, 4) else "Pending",
                    "processor_assessment": "Required; not completed",
                    "agreement": "Draft",
                },
            )
        base = sources[0]
        controls = []
        # Summaries are original concise paraphrases, not redistributed source control wording.
        entries = [
            (
                "1-3-1",
                "Approved cybersecurity policies",
                "Document cybersecurity policies, obtain authorized approval, and communicate them.",
                16,
            ),
            (
                "1-5-1",
                "Cyber risk methodology",
                "Document and approve a cybersecurity risk method addressing confidentiality, integrity and availability.",
                17,
            ),
            (
                "2-1-1",
                "Asset governance requirements",
                "Define, document and approve cybersecurity requirements for managing technology and information assets.",
                21,
            ),
            (
                "2-1-5",
                "Asset classification",
                "Classify, label and handle assets according to applicable requirements.",
                21,
            ),
            (
                "2.2.3.5",
                "Identity and access review",
                "Review identities and access rights periodically.",
                22,
            ),
        ]
        for ref, title, summary, page in entries:
            controls.append(
                add(
                    "control",
                    title,
                    base
                    | {
                        "exact_reference_id": ref,
                        "requirement_summary": summary,
                        "verification_status": "REFERENCE_VERIFIED",
                        "verification_note": f"English PDF page index {page}; specialist Arabic interpretation and applicability review pending.",
                        "interpretation": "Internal implementation interpretation; requires specialist review.",
                        "implementation_guidance": "Assign an owner, document scope and approval, test operation and retain review evidence. Review frequency is organizational unless a verified rule specifies otherwise.",
                        "evidence_requirements": [
                            "Approved scope and procedure",
                            "Dated implementation sample",
                            "Independent reviewer rationale",
                        ],
                        "source_excerpt": None,
                        "weight": 1,
                        "source_page_index": page,
                    },
                )
            )
        for i in range(5):
            add(
                "policy",
                [
                    "Access governance",
                    "Data classification",
                    "Risk management",
                    "Evidence retention",
                    "Privacy operations",
                ][i],
                {
                    "owner_id": users["manager"].id,
                    "scope": DEPARTMENTS[i],
                    "review_cycle_months": 12,
                    "state": "Draft",
                    "effective_date": None,
                    "approver_id": users["auditor"].id,
                    "supporting_controls": [controls[i].id],
                    "review_due": "2026-09-01" if i == 0 else "2027-01-01",
                    "acknowledgments": [],
                    "history": [{"version": 1, "state": "Draft"}],
                },
            )
        risks = []
        names = [
            "Unapproved access rights",
            "Sensitive data exposure",
            "Missing processing inventory",
            "Supplier assurance gap",
            "Unavailable recovery evidence",
        ]
        for i in range(40):
            risks.append(
                add(
                    "risk",
                    f"{names[i % 5]} · {i + 1:02}",
                    {
                        "synthetic": True,
                        "asset_id": assets[i % 25].id,
                        "owner_id": users["risk"].id,
                        "inherent_likelihood": i % 5 + 1,
                        "inherent_impact": (i * 3) % 5 + 1,
                        "residual_likelihood": max(1, i % 5),
                        "residual_impact": (i * 3) % 5 + 1,
                        "inherent_rationale": "Synthetic scenario estimate before safeguards; no statistical probability claimed.",
                        "control_effectiveness_rationale": "Synthetic control test not yet independently evidenced; effectiveness is uncertain.",
                        "residual_rationale": "Independent illustrative analyst rating; not derived by subtracting a percentage.",
                        "assessed_at": "2026-10-01",
                        "treatment": "mitigate",
                        "category": [
                            "Cyber",
                            "Privacy",
                            "Compliance",
                            "Vendor",
                            "Operational",
                        ][i % 5],
                    },
                    DEPARTMENTS[i % 5],
                )
            )
        for i, c in enumerate(controls):
            a = Assessment(
                control_id=c.id,
                asset_id=assets[i].id,
                owner_id=users["owner"].id,
                status=[
                    "Partially Compliant",
                    "Not Assessed",
                    "Non-Compliant",
                    "Not Assessed",
                    "Pending Verification",
                ][i],
                rationale="Synthetic baseline: supporting evidence and independent review remain outstanding.",
                stage="Draft",
            )
            s.add(a)
            s.flush()
            if i in (0, 2):
                s.add(
                    Finding(
                        assessment_id=a.id,
                        risk_id=risks[i].id,
                        title=[
                            "Missing approved access governance",
                            "",
                            "Unclassified information assets",
                        ][i],
                        action="Identify data owner, classify affected dataset, document and retest the corrective action.",
                        owner_id=users["owner"].id,
                        due="2026-10-01",
                        state="Open",
                    )
                )
        for i in range(5):
            add(
                "ropa",
                f"Synthetic processing activity {i + 1:02}",
                {
                    "synthetic": True,
                    "asset_id": assets[i].id,
                    "purpose": "Business service administration",
                    "categories": ["Synthetic employee identifiers"],
                    "sensitive_data": i == 0,
                    "subjects": "Synthetic employees",
                    "controller": "Mizan Services (synthetic)",
                    "processor": "Assessment pending",
                    "lawful_basis": "Pending documented legal review; consent not assumed",
                    "retention": "Pending approved schedule",
                    "locations": ["Saudi Arabia"],
                    "status": "Incomplete",
                    "owner_id": users["privacy"].id,
                },
            )
        add(
            "privacy_case",
            "Sensitive dataset discovery / اكتشاف بيانات حساسة",
            {
                "synthetic": True,
                "type": "PIA triage",
                "asset_id": assets[0].id,
                "owner_id": users["privacy"].id,
                "state": "Triage",
                "applicability": "Pending specialist review",
                "deadline": None,
                "deadline_rule": "Disabled until rule verification",
                "steps": [
                    "Identify owner",
                    "Review PDPL applicability",
                    "Assess harm",
                    "Request evidence",
                    "Retest mitigation",
                ],
                "risk_id": risks[1].id,
                "notes": "No real personal data. This record does not determine notification obligations.",
            },
        )
        s.commit()


if __name__ == "__main__":
    seed()
