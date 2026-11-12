"""Explicit deterministic demo seed; secrets supplied locally, never hardcoded."""

import json
import os
from pathlib import Path
from sqlalchemy import select
from argon2 import PasswordHasher
from .db import (
    Session,
    Record,
    User,
    Assessment,
    Finding,
    WorkItem,
    Relationship,
    PolicyAcknowledgement,
    now,
)

ROLES = {
    "admin": "Super Admin",
    "manager": "GRC Manager",
    "analyst": "GRC Analyst",
    "compliance": "Compliance Officer",
    "risk": "Risk Manager",
    "riskowner": "Risk Owner",
    "privacy": "Privacy Officer",
    "owner": "Control Owner",
    "auditor": "Internal Auditor",
    "executive": "Executive Viewer",
}
DEPARTMENTS = [
    "Executive Management",
    "Human Resources",
    "Finance",
    "Information Technology",
    "Cybersecurity",
    "Sales",
    "Operations",
    "Legal & Privacy",
]


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
            "Namaa Digital Solutions / نماء للحلول الرقمية",
            {
                "synthetic": True,
                "period": "2026-Q4",
                "risk_appetite": 9,
                "environment": "MIZAN DEMO — NAMAA DIGITAL SOLUTIONS",
                "scope": "Fictional Saudi technology and digital-services enterprise; hybrid cloud and on-premises",
                "employees": 150,
                "cybersecurity_team": 4,
                "it_team": 12,
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
        for i in range(5):
            add(
                "vendor",
                ["Riyadh Cloud Services", "Najd Payroll", "Tuwaiq CRM", "Gulf Mail Gateway", "Desert Backup"] [i],
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
        internal_controls = [
            "Account provisioning approval",
            "Multifactor authentication enforcement",
            "Privileged access authorization",
            "Joiner mover leaver processing",
            "Quarterly access recertification",
            "Information classification labels",
            "Approved encryption configuration",
            "Security event logging",
            "Alert triage and escalation",
            "Vulnerability scanning",
            "Patch deployment governance",
            "Secure change approval",
            "Backup monitoring",
            "Restore testing",
            "Incident classification",
            "Incident containment evidence",
            "Supplier due diligence",
            "Contract security clauses",
            "Processing activity inventory",
            "Retention schedule approval",
            "Privacy impact triage",
            "Data subject request routing",
            "Security awareness completion",
            "Policy acknowledgement tracking",
            "Continuity exercise review",
        ]
        for index, title in enumerate(internal_controls, start=1):
            ref = f"NAM-CTRL-{index:03}"
            controls.append(
                add(
                    "control",
                    title,
                    {
                        "framework_id": "NAMAA-ORG",
                        "publisher": "Namaa Digital Solutions (fictional)",
                        "official_source_url": None,
                        "source_title": "Namaa organizational control catalogue",
                        "version": "1.0 simulation",
                        "effective_date": None,
                        "last_verified_date": "2026-11-12",
                        "legal_applicability": "Organizational control; not presented as a legal or regulatory obligation.",
                        "exact_reference_id": ref,
                        "source_excerpt": None,
                        "requirement_summary": f"Operate and retain evidence for {title.lower()} within the approved scope.",
                        "interpretation": "Original internal control statement for the fictional demonstration organization.",
                        "implementation_guidance": "Assign an accountable owner, define the population and frequency, operate the control, and retain dated evidence.",
                        "evidence_requirements": ["Approved procedure", "Dated operating sample", "Independent test result"],
                        "verification_status": "ORGANIZATIONAL_CONTROL",
                        "weight": 1,
                    },
                    "Cybersecurity",
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
        for i in range(18):
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
                    DEPARTMENTS[i % len(DEPARTMENTS)],
                )
            )
        for i, c in enumerate(controls):
            a = Assessment(
                control_id=c.id,
                asset_id=assets[i % len(assets)].id,
                owner_id=users["owner"].id,
                status=[
                    "Partially Compliant",
                    "Not Assessed",
                    "Non-Compliant",
                    "Pending Verification",
                    "Compliant",
                    "Partially Compliant",
                ][i % 6],
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
        for i in range(8):
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
                    "controller": "Namaa Digital Solutions (fictional)",
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

        # Representative employee sample. It demonstrates workflow scale without creating real people.
        for i in range(20):
            add(
                "employee",
                f"Fictional employee {i + 1:03}",
                {
                    "synthetic": True,
                    "employee_ref": f"EMP-SIM-{i + 1:03}",
                    "department": DEPARTMENTS[i % len(DEPARTMENTS)],
                    "sample_note": "Representative fictional sample of a 150-person organization; not a real person.",
                },
                DEPARTMENTS[i % len(DEPARTMENTS)],
            )

        def add_item(
            uid,
            domain,
            record_type,
            title_ar,
            title_en,
            status,
            owner="manager",
            reviewer="analyst",
            approver="auditor",
            due_date=None,
            payload=None,
        ):
            item = WorkItem(
                uid=uid,
                domain=domain,
                record_type=record_type,
                title_ar=title_ar,
                title_en=title_en,
                status=status,
                owner_id=users[owner].id,
                reviewer_id=users[reviewer].id if reviewer else None,
                approver_id=users[approver].id if approver else None,
                due_date=due_date,
                payload={
                    "simulation_label": "SIMULATED DATA — NOT REAL ORGANIZATIONAL EVIDENCE",
                    **(payload or {}),
                },
                simulated=True,
                created_by=users["analyst"].id,
                updated_by=users["analyst"].id,
                created_at=now(),
                updated_at=now(),
            )
            s.add(item)
            s.flush()
            return item

        governance_items = [
            ("NAM-GOV-001", "ميثاق برنامج الحوكمة والمخاطر والامتثال", "GRC Program Charter", "Published"),
            ("NAM-GOV-002", "السياق التنظيمي", "Organizational Context", "Published"),
            ("NAM-GOV-003", "نطاق برنامج الحوكمة", "GRC Scope Statement", "Approved"),
            ("NAM-GOV-004", "هيكل الحوكمة واللجان", "Governance and Committee Structure", "Published"),
            ("NAM-GOV-005", "مصفوفة المسؤوليات", "RACI Matrix", "Approved"),
            ("NAM-GOV-006", "شهية المخاطر وحدود التحمل", "Risk Appetite and Tolerance", "Under Review"),
            ("NAM-GOV-007", "تقويم الحوكمة السنوي", "Governance Calendar", "Published"),
            ("NAM-GOV-008", "مراجعة الإدارة للربع الرابع", "Q4 Management Review", "Draft"),
        ]
        for uid, ar, en, status in governance_items:
            add_item(
                uid, "governance", "governance_document", ar, en, status,
                due_date="2027-01-31",
                payload={
                    "classification": "Internal",
                    "scope": "Namaa Digital Solutions, all business departments and in-scope information services",
                    "decision_records": [],
                    "revision_history": [{"version": 1, "date": "2026-11-12", "change": "Initial simulation baseline"}],
                },
            )

        policy_names = [
            ("سياسة أمن المعلومات", "Information Security Policy"),
            ("سياسة التحكم في الوصول", "Access Control Policy"),
            ("سياسة تصنيف المعلومات والتعامل معها", "Information Classification and Handling Policy"),
            ("سياسة الهوية والمصادقة", "Identity and Authentication Policy"),
            ("سياسة الاستخدام المقبول", "Acceptable Use Policy"),
            ("سياسة إدارة الأصول", "Asset Management Policy"),
            ("سياسة إدارة الثغرات والتحديثات", "Vulnerability and Patch Management Policy"),
            ("سياسة الاستجابة للحوادث", "Incident Response Policy"),
            ("سياسة استمرارية الأعمال والنسخ الاحتياطي", "Business Continuity and Backup Policy"),
            ("سياسة إدارة التغيير", "Change Management Policy"),
            ("سياسة أمن الأطراف الثالثة والموردين", "Third-Party and Vendor Security Policy"),
            ("سياسة إدارة المخاطر", "Risk Management Policy"),
            ("سياسة حماية البيانات والخصوصية", "Data Protection and Privacy Policy"),
            ("سياسة الاحتفاظ بالبيانات والتخلص منها", "Data Retention and Disposal Policy"),
            ("سياسة الوصول عن بعد", "Remote Access Policy"),
            ("سياسة التسجيل والمراقبة", "Logging and Monitoring Policy"),
        ]
        policies = []
        for i, (ar, en) in enumerate(policy_names, start=1):
            status = "Published" if i <= 8 else "Approved" if i <= 11 else "Under Review" if i <= 14 else "Draft"
            policies.append(
                add_item(
                    f"NAM-POL-{i:03}", "policy", "policy", ar, en, status,
                    due_date="2027-11-12",
                    payload={
                        "purpose": f"Define mandatory organizational expectations for {en.lower()} in the fictional Namaa environment.",
                        "scope": "Employees, contractors, information assets, business services and applicable suppliers.",
                        "definitions": ["Control owner", "Evidence", "Exception", "Restricted information"],
                        "mandatory_requirements": [
                            "An accountable owner shall maintain the operating procedure and in-scope population.",
                            "Operation shall be evidenced with dated, attributable records.",
                            "Exceptions require documented risk assessment, approval and an expiry date.",
                        ],
                        "responsibilities": {"Owner": "Operate and monitor", "GRC": "Challenge and track", "Internal Audit": "Independently test"},
                        "exceptions": "Submit a reason, affected scope, risk assessment, compensating controls and expiry date for independent approval.",
                        "enforcement": "Violations are triaged through management, HR, Legal and GRC processes as applicable.",
                        "procedure": [
                            "Identify the in-scope population and responsible owner.",
                            "Perform the required activity through an approved ticket or register.",
                            "Collect synthetic demonstration evidence and record the period covered.",
                            "Review exceptions, overdue actions and control results.",
                        ],
                        "implementation_checklist": [
                            {"step": "Assign owner", "role": "GRC Manager", "verification": "Approved owner record"},
                            {"step": "Publish procedure", "role": "Control Owner", "verification": "Versioned procedure"},
                            {"step": "Run control", "role": "System Owner", "verification": "Dated operating sample"},
                            {"step": "Test effectiveness", "role": "Internal Auditor", "verification": "Independent test result"},
                        ],
                        "evidence_requirements": ["Approval record", "Operating sample", "Exception register", "Independent test result"],
                        "control_ids": [controls[(i - 1) % len(controls)].id, controls[(i + 4) % len(controls)].id],
                        "risk_ids": [risks[(i - 1) % len(risks)].id],
                        "compliance_tests": ["Inspect approval", "Sample operating records", "Trace exceptions", "Reperform one control check"],
                        "review_frequency": "Annual organizational cycle; not a claimed regulatory deadline",
                        "classification": "Internal",
                        "effective_date": "2026-11-12" if status in {"Published", "Approved"} else None,
                        "review_date": "2027-11-12",
                        "revision_history": [{"version": 1, "date": "2026-11-12", "change": "Initial simulated policy"}],
                        "procedure_implemented": i <= 10,
                        "control_operating": i in {1, 3, 5, 6, 8, 10},
                        "evidence_verified": i in {1, 3, 6},
                        "independently_tested": i in {1, 3},
                        "test_frequency": "Annual",
                        "next_test_date": "2027-06-30",
                    },
                )
            )

        for i in range(10):
            s.add(
                PolicyAcknowledgement(
                    policy_id=policies[0].id,
                    subject_ref=f"EMP-SIM-{i + 1:03}",
                    subject_name=f"Fictional employee {i + 1:03}",
                    department=DEPARTMENTS[i % len(DEPARTMENTS)],
                    status="Acknowledged" if i < 7 else "Assigned",
                    assigned_at="2026-11-12T08:00:00+00:00",
                    acknowledged_at="2026-11-12T10:00:00+00:00" if i < 7 else None,
                    recorded_by=users["analyst"].id,
                )
            )

        privacy_items = []
        privacy_services = [
            "Customer portal account management", "Employee lifecycle administration", "CRM sales pipeline",
            "Customer support tickets", "Supplier onboarding", "Security monitoring",
            "Marketing preference management", "Payroll administration",
        ]
        for i, service in enumerate(privacy_services, start=1):
            privacy_items.append(
                add_item(
                    f"NAM-PRV-{i:03}", "privacy", "processing_activity",
                    f"نشاط معالجة تجريبي {i:02}", service,
                    "Under Review" if i in {1, 4} else "Approved" if i in {2, 6} else "Draft",
                    owner="privacy", due_date="2027-02-28",
                    payload={
                        "purpose": service,
                        "data_categories": ["Fictional identifiers", "Fictional contact data"],
                        "data_subjects": ["Fictional customers" if i % 2 else "Fictional employees"],
                        "legal_basis": "Requires documented legal validation; no legal basis is inferred by the platform.",
                        "sources": ["Synthetic web form"],
                        "recipients": ["Authorized Namaa teams"],
                        "processors": ["Synthetic supplier" if i in {1, 5, 8} else "None recorded"],
                        "storage_locations": ["Saudi Arabia"],
                        "international_transfers": "Assessment required" if i == 1 else "None identified in simulation",
                        "retention": "Pending approved schedule" if i in {1, 3, 7} else "Organizational schedule RS-01",
                        "security_measures": ["Role-based access", "Encryption", "Logging"],
                        "legal_review_required": True,
                    },
                )
            )

        vendor_profiles = [
            ("Riyadh Cloud Services", "Critical", "Pending Verification"),
            ("Najd Payroll", "High", "Approved"),
            ("Tuwaiq CRM", "High", "In Progress"),
            ("Gulf Mail Gateway", "Moderate", "Approved"),
            ("Desert Backup", "Critical", "Under Review"),
        ]
        vendors = []
        for i, (name, rating, status) in enumerate(vendor_profiles, start=1):
            vendors.append(
                add_item(
                    f"NAM-VEN-{i:03}", "vendor", "vendor_assessment",
                    f"تقييم المورد {i:02}", name, status,
                    due_date="2026-10-31" if i in {1, 5} else "2027-03-31",
                    payload={
                        "service": ["Cloud hosting", "Payroll", "CRM", "Email security", "Backup platform"][i - 1],
                        "risk_rating": rating,
                        "questionnaire_completion": [62, 100, 78, 100, 55][i - 1],
                        "due_diligence": "Insufficient evidence" if i in {1, 5} else "Reviewed",
                        "contract_security_requirements": "Under legal review" if i in {1, 3} else "Included",
                        "data_processing_agreement": "Required — pending" if i in {1, 2, 3} else "Not required by current scope decision",
                        "next_review": "2027-05-31",
                    },
                )
            )

        incidents = []
        incident_data = [
            ("اشتباه اختراق حساب موظف", "Simulated employee account compromise", "Pending Verification", "High"),
            ("إنذار برمجية ضارة غير مؤكد", "Unconfirmed malware alert", "Closed", "Low"),
            ("إرسال ملف إلى مستلم خاطئ", "Misdirected synthetic document", "In Progress", "Moderate"),
        ]
        for i, (ar, en, status, severity) in enumerate(incident_data, start=1):
            incidents.append(
                add_item(
                    f"NAM-INC-{i:03}", "incident", "security_incident", ar, en, status,
                    due_date="2026-11-30",
                    payload={
                        "description": "Fictional scenario only. No real account, customer or security telemetry is represented.",
                        "detection_source": "Synthetic security alert",
                        "category": "Account compromise" if i == 1 else "Security event",
                        "severity": severity,
                        "affected_asset_id": assets[1].id,
                        "data_involved": "Assessment required; no real personal data",
                        "business_impact": "Potential unauthorized access and service disruption",
                        "timeline": ["Detected", "Triaged", "Escalated", "Contained", "Investigated", "Recovered"] if i == 1 else ["Detected", "Triaged"],
                        "response_actions": ["Disable fictional session", "Reset simulated credentials", "Enforce MFA", "Review excessive privileges"],
                        "notification_assessment": "Requires Privacy and Legal review; the platform does not determine statutory notification.",
                        "root_cause": "Phishing scenario combined with excessive privileges and missing MFA" if i == 1 else "Under review",
                        "lessons_learned": ["Prioritize MFA coverage", "Revalidate remote access groups"],
                    },
                )
            )

        continuity_items = []
        for i, (service, rto, rpo) in enumerate(
            [("Customer Portal", "4 hours", "1 hour"), ("Identity Management", "2 hours", "15 minutes"), ("ERP and Payroll", "8 hours", "4 hours")],
            start=1,
        ):
            continuity_items.append(
                add_item(
                    f"NAM-BCM-{i:03}", "continuity", "critical_service",
                    f"خدمة حرجة {i:02}", service, "Approved" if i < 3 else "Under Review",
                    due_date="2027-04-30",
                    payload={
                        "business_impact": "Customer or workforce operations are disrupted beyond the approved tolerance.",
                        "rto": rto, "rpo": rpo,
                        "dependencies": ["Identity", "Network", "Cloud or on-premises platform", "Service owner"],
                        "continuity_plan": "BCP-SIM-01",
                        "last_test": "2026-10-15",
                        "test_result": "Failed restore test; corrective action opened" if i == 1 else "Passed with observations",
                        "lessons_learned": ["Verify restore credentials before exercise", "Record recovery evidence"],
                    },
                )
            )

        add_item(
            "NAM-TRN-001", "training", "awareness_campaign", "حملة التوعية بالتصيد", "Phishing Awareness Campaign",
            "In Progress", due_date="2026-12-31",
            payload={"population": 150, "representative_records": 20, "assigned": 20, "completed": 14, "passed": 12, "overdue": 6, "scaling_note": "20 fictional sample records represent the 150-person scenario; rates are calculated only from the sample."},
        )
        add_item(
            "NAM-TRN-002", "training", "policy_campaign", "إقرار سياسة أمن المعلومات", "Information Security Policy Acknowledgement",
            "In Progress", due_date="2026-12-15",
            payload={"assigned": 10, "acknowledged": 7, "overdue": 3, "policy_id": policies[0].id},
        )

        for i in range(2):
            add_item(
                f"NAM-AUD-{i + 1:03}", "audit", "audit_exercise",
                f"تمرين تدقيق داخلي {i + 1}", ["Access Governance Review", "Backup and Recovery Review"][i],
                "Pending Verification" if i == 0 else "In Progress", due_date="2027-01-31",
                payload={"scope": ["Remote access and privileged accounts", "Backup jobs and restore tests"][i], "procedures": ["Inspect design", "Sample operating evidence", "Interview owner", "Document observation"], "sampling": "Five synthetic items selected from the in-scope population", "independent": True},
            )

        gaps = []
        remediations = []
        gap_titles = [
            "Remote users without enforced MFA", "Incomplete customer-service RoPA", "Cloud supplier assurance evidence",
            "Excessive employee account privileges", "Failed customer portal restore test", "Overdue access recertification",
            "Unclassified shared dataset", "Missing retention approval", "Incomplete incident evidence",
            "Unreviewed privileged account", "Policy acknowledgements overdue", "Vendor contract clause pending",
        ]
        for i, title in enumerate(gap_titles, start=1):
            gap = add_item(
                f"NAM-GAP-{i:03}", "gap", "control_gap", f"فجوة تجريبية {i:02}", title,
                "Closed" if i in {7, 9} else "Pending Verification" if i in {1, 5} else "In Progress" if i < 9 else "Open",
                due_date="2026-10-31" if i in {3, 6, 8} else "2027-02-28",
                payload={
                    "requirement": controls[(i - 1) % len(controls)].payload["exact_reference_id"],
                    "control_id": controls[(i - 1) % len(controls)].id,
                    "current_state": "Control is inconsistently operated or lacks sufficient evidence.",
                    "expected_state": "Approved control operates across the documented scope with dated evidence.",
                    "root_cause": "Ownership and evidence expectations were not consistently established.",
                    "risk_id": risks[(i - 1) % len(risks)].id,
                    "business_impact": "Uncertainty over protection, compliance and service resilience.",
                    "priority": "Critical" if i in {1, 4, 5} else "High" if i < 9 else "Moderate",
                    "evidence_required": ["Completion ticket", "Configuration or register export", "Independent test"],
                    "verification_criteria": "Reviewer traces the change to the full population and reperforms a sample.",
                    "completion_evidence_ids": [1] if i in {7, 9} else [],
                    "verification_result": "Passed" if i in {7, 9} else None,
                },
            )
            gaps.append(gap)
            remediations.append(
                add_item(
                    f"NAM-REM-{i:03}", "remediation", "corrective_action",
                    f"إجراء تصحيحي {i:02}", f"Remediate: {title}",
                    "Closed" if i in {7, 9} else "Pending Verification" if i in {1, 5} else "In Progress" if i < 9 else "Planned",
                    due_date=gap.due_date,
                    payload={
                        "gap_id": gap.id,
                        "priority": gap.payload["priority"],
                        "dependencies": ["System owner availability", "Change approval"],
                        "estimated_cost_sar": 5000 + i * 1250,
                        "plan": f"Implement and independently verify corrective action for {title.lower()}.",
                        "completion_evidence_ids": [1] if i in {7, 9} else [],
                        "verification_result": "Passed" if i in {7, 9} else None,
                        "closure_approval": "Internal auditor" if i in {7, 9} else None,
                    },
                )
            )

        evidence_types = [
            "Configuration Export", "Audit Log", "Screenshot", "Approval Record", "Ticket",
            "Policy", "Procedure", "Training Record", "Meeting Minutes", "Test Result",
        ]
        evidence_items = []
        for i, evidence_type in enumerate(evidence_types, start=1):
            evidence_items.append(
                add_item(
                    f"NAM-EVD-{i:03}", "evidence", "evidence_metadata",
                    f"دليل تجريبي {i:02}", f"Synthetic {evidence_type}",
                    "Approved" if i in {1, 4, 6, 10} else "Pending Verification" if i < 9 else "Draft",
                    due_date="2027-05-31",
                    payload={
                        "description": "Metadata-only synthetic demonstration evidence; no real configuration or personal data.",
                        "evidence_type": evidence_type,
                        "source": "MIZAN scenario simulator",
                        "collection_date": "2026-11-12",
                        "period_covered": "2026-Q4",
                        "related_control_id": controls[(i - 1) % len(controls)].id,
                        "related_risk_id": risks[(i - 1) % len(risks)].id,
                        "related_policy_id": policies[(i - 1) % len(policies)].id,
                        "related_gap_id": gaps[(i - 1) % len(gaps)].id,
                        "integrity_notes": "No file attached. A real upload uses encrypted storage and SHA-256 verification.",
                        "classification": "Internal — Synthetic",
                        "redaction_status": "Not required; generated data only",
                        "review_status": "Verified" if i in {1, 4, 6, 10} else "Awaiting review",
                        "retention": "Demonstration retention schedule; not a statutory period",
                        "evidence_class": "Demonstration Evidence" if i < 9 else "Missing Evidence",
                    },
                )
            )

        def link(source_type, source_id, target_type, target_id, relation, rationale):
            s.add(
                Relationship(
                    source_type=source_type, source_id=source_id,
                    target_type=target_type, target_id=target_id,
                    relation=relation, rationale=rationale,
                    status="Approved", created_by=users["analyst"].id,
                    reviewed_by=users["auditor"].id, created_at=now(),
                )
            )

        # Scenario 4 trace: incident → risk → control → policy → gap → remediation → evidence.
        link("work_item", incidents[0].id, "record", risks[0].id, "causes_reassessment", "Compromised-account scenario changes the access risk rationale.")
        link("work_item", incidents[0].id, "record", controls[6].id, "control_failure", "MFA control did not cover the selected remote-user group.")
        link("work_item", incidents[0].id, "work_item", policies[1].id, "policy_violation", "Access policy requires approved authentication safeguards.")
        link("work_item", incidents[0].id, "work_item", gaps[3].id, "creates_gap", "Excessive privilege and missing MFA are documented as a control gap.")
        link("work_item", gaps[3].id, "work_item", remediations[3].id, "remediated_by", "Corrective action removes excess privilege and enforces MFA.")
        link("work_item", remediations[3].id, "work_item", evidence_items[0].id, "supported_by", "Synthetic configuration export supports retest.")
        link("work_item", privacy_items[0].id, "work_item", gaps[1].id, "creates_gap", "Incomplete processing inventory creates the privacy governance gap.")
        link("work_item", vendors[0].id, "work_item", gaps[2].id, "creates_gap", "Supplier assurance remains incomplete.")
        link("work_item", continuity_items[0].id, "work_item", gaps[4].id, "creates_gap", "Failed restore test creates a continuity corrective action.")
        s.commit()


if __name__ == "__main__":
    seed()
