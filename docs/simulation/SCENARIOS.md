# Repeatable connected scenarios

All records are marked **SIMULATED DATA — NOT REAL ORGANIZATIONAL EVIDENCE**.

## 1. Remote-access MFA failure

Initial state: a selected fictional remote-user group lacks enforced MFA. Trace: `NAM-INC-001` → access risk → organizational MFA control → `NAM-POL-002` → `NAM-GAP-001`/`004` → `NAM-REM-001`/`004` → `NAM-EVD-001`. The analyst records the control gap and risk rationale; remediation enforces MFA and removes excessive privilege; an independent reviewer examines the configuration export and access sample before closure. Residual risk is reassessed explicitly and is never reduced merely because the plan exists.

## 2. Personal-data governance gap

Initial state: customer-service processing is incomplete in the RoPA. Trace: `NAM-PRV-001` → privacy risk → processing-inventory control → `NAM-POL-013` → `NAM-GAP-002` → `NAM-REM-002`. Legal basis and transfer validity remain flagged for Legal/Privacy review. Final state requires completed data flow, retention decision, access safeguards and verified evidence.

## 3. Supplier assurance gap

Initial state: `NAM-VEN-001` lacks sufficient control evidence. The supplier is classified Critical, due diligence is incomplete, contract clauses and DPA are tracked, and `NAM-GAP-003` drives treatment. Acceptance, if selected, requires an authorized decision and future review date; supplier evidence is not treated as verified merely because a questionnaire exists.

## 4. Compromised fictional account

Initial state: a phishing scenario combines missing MFA with excessive privilege. `NAM-INC-001` records detection, triage, escalation, containment, investigation, recovery, notification assessment, root cause and lessons learned. Relationship edges connect Incident → Risk → Control → Policy → Gap → Remediation → Evidence. Any notification conclusion requires Privacy/Legal review and is not automated.

## 5. Failed restore test

Initial state: the Customer Portal restore exercise fails. `NAM-BCM-001` links its recovery objectives and dependencies to `NAM-GAP-005` and `NAM-REM-005`. Corrective work validates credentials and reruns the restore. Closure requires a synthetic test result and independent verification.

## Reset and repeatability

Backend tests recreate an isolated database before every test. For the local demonstration, back up `mizan.db`, keep `.env` and `data/evidence`, then recreate the database with Alembic and `python -m app.seed`. The procedure is intentionally outside the UI to prevent an accidental destructive click. Never reset a database that contains records not labelled as simulated.
