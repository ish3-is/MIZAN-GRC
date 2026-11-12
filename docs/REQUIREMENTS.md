# System requirements and acceptance baseline

Release 0.2 extends the tested vertical slice with connected operational-domain workflows. Requirements labelled planned are not delivered features.

| ID | Requirement | State | Verification |
|---|---|---|---|
| AUTH-01 | Local generated credentials, ten roles, Argon2id, server sessions | Implemented | Backend auth tests |
| AUTH-02 | Independent assessment review and risk acceptance | Implemented | Review checks tested; acceptance regression added |
| REG-01 | Mandatory provenance on seeded source/control documents | Implemented | Register validator |
| REG-02 | Full verified PDPL article catalogue and deadline rules | Planned | Disabled; specialist review needed |
| REG-03 | Version-controlled source update procedure | Documented manual procedure | Git diff and register validation |
| REG-04 | In-app regulatory updates and change-impact automation | Planned | No feature claim |
| CMP-01 | Create, rate, evidence, submit, approve/return assessment | Implemented | Backend full chain + browser test |
| CMP-02 | Independent N/A exclusion and disclosed score methodology | Implemented | N/A and score regression |
| CMP-03 | Versioned reassessment and history | Partial | Current row + prior-state audit event, not normalized immutable revisions |
| RSK-01 | Register inherent and independent residual risk with rationales | Implemented | API and 25 matrix combinations |
| RSK-02 | Configure matrix definitions and appetite interactively | Planned | Seed configuration only |
| RSK-03 | What-if simulation, scenario generator, trend snapshots | Planned | No fake simulator |
| REM-01 | Assign gap to risk/assessment/owner, progress, retest, close | Implemented | Full-chain API test |
| EVD-01 | Authenticated encrypted evidence and integrity checking | Implemented | Ciphertext and tamper tests |
| EVD-02 | Evidence version comparison, antivirus and retention deletion | Planned | Uploads are append-only evidence rows; no scanning |
| AUD-01 | Chained event log and validation | Implemented | Tamper test; admin rewrite caveat |
| AUD-02 | Audit exercises with scope, procedures, sampling and lifecycle | Partial | Two operational exercises; dedicated working-paper editor remains planned |
| GOV-01 | Charter, context, scope, RACI, calendar and management review | Implemented | Operational records, bilingual docs and lifecycle tests |
| GOV-02 | Sixteen policy lifecycles, approvals and acknowledgements | Implemented | Seed counts, UI actions and separation-of-duties tests |
| PRV-01 | Eight synthetic processing activities / RoPA records | Implemented | Operational UI, seed and count tests |
| PRV-02 | PIA, rights, breach, transfer and retention workflows | Partial | Generic operational workflow; no unverified statutory deadlines or legal conclusions |
| TPR-01 | Five supplier assessments, due diligence and contract/DPA tracking | Implemented simulation | Operational UI and seed tests |
| INC-01 | Three incident records and connected compromised-account scenario | Implemented simulation | Relationship edges and scenario documentation |
| BCM-01 | Three critical services with RTO/RPO and exercise results | Implemented simulation | Operational UI and seed tests |
| TRN-01 | Training campaign and policy acknowledgement sample | Implemented simulation | Calculated dashboard rate and acknowledgement API |
| RPT-01 | Scoped JSON management report, UTF-8 CSV and audit ZIP | Implemented | Report and manifest tests |
| RPT-02 | Polished Arabic PDF generation | Planned | Browser print is available, not a validated reporting engine |
| UX-01 | Arabic RTL/English LTR, responsive navigation and dense workspaces | Implemented | Chromium desktop/mobile flow + screenshots |
| UX-02 | Full Arabic data translations and WCAG audit | Partial | Bilingual titles and RTL/LTR implemented; formal WCAG audit remains planned |
| OPS-01 | Compose, migrations, health checks and seed | Implemented | SQLite migration locally; Docker/Postgres runtime pending |
| OPS-02 | Scheduled alerts, backups tested, load/performance testing | Planned | Request-time overdue/freshness only; backup guidance documented |

## Functional acceptance script

1. Generate local secrets, migrate, seed and start services.
2. Sign in as owner, inspect exact selected ECC reference and its verification limits.
3. Create or open an assessment; record rating and rationale.
4. Upload synthetic UTF-8 evidence with organizational review date; save and submit.
5. Register an identified gap linked to a risk and accountable owner.
6. Sign in as auditor in a separate session; inspect evidence and verify the noncompliant conclusion.
7. Owner progresses remediation, reopens approved assessment, records improved rating and fresh supporting evidence, then submits for retest.
8. Independent auditor approves the Compliant conclusion and closes the Ready for Retest finding.
9. Generate management JSON, export audit ZIP and verify evidence hashes; export CSV.
10. Verify chained activity. Reload to confirm persisted state.

The automated backend test executes this sequence on an isolated SQLite database. The browser test executes create/save/reload/upload/submit/independent-approve and responsive language navigation. Docker and PostgreSQL operation must be independently verified before treating the overall requested Definition of Done as satisfied.
