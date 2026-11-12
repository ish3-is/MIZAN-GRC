# Delivery phases and acceptance

This record tracks the actual first release. “Prepared” and “planned” are not completion claims. All phase commands are in OPERATIONS.md. Exact executed results are in VERIFICATION.md.

| Phase | Implemented in this release | Files | Migration | Acceptance / known limits |
|---|---|---|---|---|
| 0 — Sources | Official-source research, seven provenance records, five checked ECC references, verification states, manual Git update workflow | regulatory/sources.json, app/seed.py, REGULATORY.md, verify-register.py | Source/control records in 0001 | Structure checks; legal applicability and complete Arabic/PDPL review pending |
| 1 — Architecture | SRS, current/target ERD, component/data flow, RBAC, threat model, OpenAPI, Arabic design | docs architecture/security/requirements/API; frontend styles; OpenAPI snapshot | 0001 schema | Documents reflect real implementation; PostgreSQL runtime/concurrency pending |
| 2 — Identity and baseline | Eight roles, sessions, organizational/configuration and policy baseline, catalogue | app/core.py, identities.py, registry.py, seed.py; React workspace | 0001 | Auth/authorization tests pass; policy approval/committee/RACI not implemented |
| 3 — Core slice | Risk creation/acceptance, assessment lifecycle, encrypted evidence, linked remediation/retest, activity | app/risk.py, compliance.py, evidence.py, remediation.py, audit.py, methodology.py | 0001 | End-to-end API and browser checks; evidence retention/version UI and risk trends pending |
| 4 — Privacy/audit/reporting | Read-only processing/discovery records, scoped JSON/CSV/audit ZIP, print action | app/reporting.py, React registries/reports, CASE_STUDY.md | 0001 | Manifest hashes tested; operational privacy, audit planning and high-quality PDF pending |
| 5 — Automation/intelligence | Request-time overdue and stale-evidence calculations, matrix/chart aggregation | app/reporting.py, methodology.py | none additional | No scheduler, external reminders, cross-framework suggestions, AI or simulator |
| 6 — Verification/deployment | Tests, screenshots, dependency audits, CI, Compose, startup health, runbook | backend/tests, frontend/e2e, workflows, Dockerfiles, scripts | Alembic 0001 | Native tested; Docker runtime subject to verification record; accessibility, load tests and production hardening incomplete |

## Next acceptance slices

1. **Regulatory scope:** independent Arabic specialist review of authoritative PDPL/IR/transfer texts and ECC applicability; source revisions, explicit requirement entities and approved mappings. Activate a deadline only after its exact legal basis and exception rules are reviewed.
2. **Privacy operations:** normalized RoPA and case schemas; rights identity verification, PIA applicability/approval, breach triage and transfer safeguards; role checks and full negative tests. Never infer that consent is universally required.
3. **Governance:** policy versions, independent approval, acknowledgment, exceptions, committees and RACI. Normalize relationships instead of extending free-form JSON indefinitely.
4. **Audit operations:** plans, test procedures, sampling/workpapers and signed evidence conclusions; report snapshots and validated Arabic PDF layout.
5. **Automation:** durable scheduler/outbox, reminder/escalation policies, evidence lifecycle, source change-impact graph and reviewed mapping suggestions. Offline core must remain functional.
6. **Production gates:** deployment/TLS, SSO/MFA, database authorization design, external log anchoring, scanner, KMS rotation, PostgreSQL concurrency/backup recovery, accessibility and performance test evidence.

The complete original Definition of Done is not declared satisfied while Docker/PostgreSQL runtime verification and the broader domain requirements remain outstanding. The initial functional slice is independently reviewable and runnable through the native fallback.
