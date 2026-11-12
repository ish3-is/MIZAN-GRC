# Synthetic Saudi investigation case

Namaa Digital Solutions / نماء للحلول الرقمية is a fictional Saudi technology and digital-services organization. Eight departments support 25 information assets and five suppliers. A 20-record fictional employee sample represents the 150-person organization profile. No real organization, employee, customer or incident is represented. The 18 seeded risks are illustrative analyst scenarios without independently substantiated effectiveness claims.

## Discovery

A discovery exercise identifies a sensitive employee dataset in the Technology scope. The inventory record is Unclassified, and the linked processing record is incomplete. The privacy discovery case is in Triage. The accountable privacy role must identify the actual business/data owner and document processing facts before making a PDPL applicability decision. The application does not infer a legal basis, notification duty or timer.

## Assessment chain

1. Inspect the asset registry and its synthetic owner. Inspect the RoPA baseline and the incomplete processing facts.
2. Open the selected ECC asset-governance assessment. Inspect its exact reference, source revision and legal-applicability caveat. A classification issue may be investigated against the separate selected classification reference; the issue itself is not automatic proof of a legal breach.
3. Document the gap as Non-Compliant within the selected assessment scope and explain the sample limitation. Upload only synthetic classification/procedure evidence.
4. Register a risk with asset link, inherent L=4/I=5 (20 Critical), effectiveness rationale and independently justified residual L=2/I=4 (8 Moderate). These are organizational judgments, not probabilities.
5. Register a finding linking the assessment and risk; assign owner and an organizational target date. Start remediation.
6. Auditor verifies the initial gap conclusion. Owner documents corrective work, reopens the assessment, attaches a fresh synthetic approved classification sample, and submits a Compliant rating for retest.
7. Independent auditor inspects content and scope, approves the new conclusion, and closes the Ready for Retest finding. Generate a scoped report and audit ZIP.

The API regression `test_complete_vertical_slice` executes the assessment, evidence, risk, finding, remediation, reassessment, independent retest and report chain. Additional tests exercise operational record lifecycles, policy counts, calculated KPIs, risk bands, separation of duties and the evidence requirement for remediation closure. Privacy records are editable workflows, while legal-basis and statutory-deadline decisions remain flagged for specialist review rather than automated conclusions.

## Executive findings at clean seed

| Observation | Persisted basis | Decision needed |
|---|---|---|
| Missing approved access governance | Open seeded finding 1; draft assessment | Obtain scoped approved procedure and evidence |
| Unclassified information assets | Open seeded finding 2; inventory classification | Identify owners and classify affected assets |
| No independently approved assessments | Five starter assessments, zero approval | Assign independent evidence review |
| Incomplete processing records | Five RoPA records marked Incomplete | Confirm purposes, basis, retention, processors and locations |
| Overdue policy review | Access-governance draft has past organizational review date | Approve lifecycle and review scope |
| Supplier assurance backlog | Two vendors labelled review overdue | Obtain documented third-party risk review |

Dates are fixed synthetic organizational dates, not Saudi regulatory deadlines. Overdue dashboard values are computed relative to execution date. Evidence baseline is empty, so evidence coverage and approved compliance score begin at 0%; stale-evidence behavior is exercised in tests rather than implying a nonexistent seed attachment.

## Audit pack

The authorized export contains management-report.json, manifest.json, an explanatory README and decrypted synthetic evidence documents referenced by assessment ID. SHA-256 digests can be recomputed against each extracted document. Do not treat the exported ZIP as encrypted. It includes timestamps, source provenance, verification states, scope and limitations. The sample pack in `docs/sample-audit-pack.zip` was generated from the local exercised demonstration, so its assessment count may exceed the clean five-assessment seed.
