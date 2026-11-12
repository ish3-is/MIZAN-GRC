# MIZAN implementation checklist

Last updated: 2026-11-12  
Environment: **MIZAN DEMO — NAMAA DIGITAL SOLUTIONS**  
All seeded organizational records are fictional and carry a simulation label.

## Implemented and tested

- [x] React/TypeScript bilingual shell with Arabic RTL and English LTR.
- [x] FastAPI, SQLAlchemy, Alembic, SQLite demonstration and PostgreSQL Compose architecture.
- [x] Argon2id local credentials, opaque sessions, CSRF request header, origin validation and endpoint RBAC.
- [x] Ten demo roles with server-enforced separation of owner, reviewer and approver duties.
- [x] Versioned operational records for governance, policies, privacy, vendors, incidents, continuity, training, audit, gaps, remediation and evidence metadata.
- [x] Controlled lifecycle transitions, approval history, optimistic version checks and tamper-evident activity events.
- [x] 5×5 inherent and residual risk scoring with documented 1–4 / 5–9 / 10–16 / 17–25 bands.
- [x] Evidence-based assessment submission, encrypted file storage, integrity hashes, freshness and independent review.
- [x] Remediation closure guard requiring completion evidence and verification.
- [x] Sixteen policy lifecycle records with procedures, checklists, evidence expectations and distinct effectiveness states.
- [x] Policy acknowledgement sample with numerator, denominator and representative-sample caveat.
- [x] Privacy processing activities with legal-review flags; no legal basis or statutory timer is inferred.
- [x] Connected access, privacy, supplier, incident and restore-test simulation records.
- [x] Live executive KPIs calculated from persisted records.
- [x] UTF-8 risk CSV, management JSON, browser-print report and authorized audit ZIP.
- [x] Production build, API tests, component tests and Playwright workflow executed.

## Partially implemented

- [~] Policy documents: operational content is stored in the application; bilingual repository editions are generated for portfolio review, but formal legal/HR approval is outside the simulation.
- [~] Reports: management JSON, CSV, print-to-PDF and audit ZIP work; native server-side Arabic PDF and Excel generation are not implemented.
- [~] Privacy: RoPA and processing records work; data-subject request, breach notification and transfer decisions remain generic operational records until verified deadline and legal rules are approved.
- [~] User management: Super Admin can change demo roles; user creation, password reset and enterprise identity federation are not implemented.
- [~] Framework mappings: selected ECC references are source-checked; ISO clause mappings are not loaded without a licensed copy.
- [x] Recoverable local demo reset requires an exact confirmation phrase, refuses non-simulated work items, creates a timestamped backup and preserves local secrets/evidence files; no destructive in-app button is exposed.

## Not implemented / requires external authority

- [ ] Legal opinion on PDPL applicability, lawful basis, notification timing or transfer validity.
- [ ] Complete ECC, CSCC or ISO licensed control library.
- [ ] Regulatory approval, certification or external audit opinion.
- [ ] Production tenant isolation, SSO/MFA, managed key vault and object-storage malware scanning.
- [ ] Server-side Arabic PDF rendering and Excel workbooks.
- [ ] Performance/load testing, penetration testing and independent accessibility certification.
- [ ] GitHub push. The remote is configured, but publishing is intentionally not performed without explicit authorization/authentication.

## Acceptance evidence

| Gate | Evidence |
|---|---|
| API and workflow tests | `python -m pytest backend/tests -q` |
| Source-register structure | `python scripts/verify-register.py` |
| Frontend unit tests | `npm test -- --run` |
| TypeScript and production build | `npm run build` |
| Browser workflow | `npm run test:e2e` |
| UI source rules | `node .../lint.mjs --app frontend/src` |
| Production visual inspection | `.taste-skill/production-2/report.json` |
