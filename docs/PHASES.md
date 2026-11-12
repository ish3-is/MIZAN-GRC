# Delivery phases and acceptance

This record tracks the actual v0.2 release. “Prepared” and “planned” are not completion claims. All phase commands are in OPERATIONS.md. Exact executed results are in VERIFICATION.md.

| Phase | Implemented in this release | Files | Migration | Acceptance / known limits |
|---|---|---|---|---|
| 0 — Sources | Official-source research, ten provenance records, five checked ECC references, conditional CSCC and ISO catalogue metadata | regulatory/sources.json, app/seed.py, REGULATORY.md, verify-register.py | Source/control records in 0001 | Structure checks; legal applicability and complete Arabic/PDPL review pending |
| 1 — Architecture | SRS, current/target ERD, component/data flow, RBAC, threat model, OpenAPI, Arabic design | docs architecture/security/requirements/API; frontend styles; OpenAPI snapshot | 0001 schema | Documents reflect real implementation; PostgreSQL runtime/concurrency pending |
| 2 — Identity and baseline | Ten roles, sessions, role administration, Namaa organization and 30-control catalogue | app/core.py, identities.py, registry.py, seed.py; React workspace | 0001 + 0002 | Auth/authorization tests pass; enterprise SSO remains planned |
| 3 — Core slice | Risk creation/acceptance, assessment lifecycle, encrypted evidence, linked remediation/retest, activity | app/risk.py, compliance.py, evidence.py, remediation.py, audit.py, methodology.py | 0001 | End-to-end API and browser checks; evidence retention/version UI and risk trends pending |
| 4 — Privacy/audit/reporting | Writable privacy, policy, supplier, incident, continuity, training and audit records; JSON/CSV/audit ZIP/print | operations.py, reporting.py, React operational centers, bilingual policies | 0002 | Lifecycle and closure guards tested; legal engines, working papers and native PDF pending |
| 5 — Automation/intelligence | Request-time overdue and stale-evidence calculations, matrix/chart aggregation | app/reporting.py, methodology.py | none additional | No scheduler, external reminders, cross-framework suggestions, AI or simulator |
| 6 — Verification/deployment | Tests, screenshots, dependency audits, CI, Compose, startup health, runbook | backend/tests, frontend/e2e, workflows, Dockerfiles, scripts | Alembic 0001 | Native tested; Docker runtime subject to verification record; accessibility, load tests and production hardening incomplete |

## Next acceptance slices

1. **Regulatory scope:** independent Arabic specialist review of authoritative PDPL/IR/transfer texts and ECC applicability; source revisions, explicit requirement entities and approved mappings. Activate a deadline only after its exact legal basis and exception rules are reviewed.
2. **Privacy operations:** specialize the current versioned processing records into normalized rights-request, PIA, breach and transfer schemas with identity verification, safeguard decisions and full negative tests. Never infer that consent is universally required.
3. **Governance:** add immutable policy-version content snapshots, committee attendance/quorum and dedicated exception-expiry automation to the implemented approval, acknowledgement and RACI baseline.
4. **Audit operations:** plans, test procedures, sampling/workpapers and signed evidence conclusions; report snapshots and validated Arabic PDF layout.
5. **Automation:** durable scheduler/outbox, reminder/escalation policies, evidence lifecycle, source change-impact graph and reviewed mapping suggestions. Offline core must remain functional.
6. **Production gates:** deployment/TLS, SSO/MFA, database authorization design, external log anchoring, scanner, KMS rotation, PostgreSQL concurrency/backup recovery, accessibility and performance test evidence.

The complete original Definition of Done is not declared satisfied while Docker/PostgreSQL runtime verification, native Arabic PDF/Excel, production identity controls and specialized legal-decision workflows remain outstanding. The v0.2 simulation is independently reviewable and runnable through the native fallback.
