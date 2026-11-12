# Risk and assessment methodology v1

## Risk

The initial matrix multiplies ordinal likelihood (1–5) by ordinal impact (1–5). This ranks scenarios; it is not an expected monetary loss, calibrated probability or statistical prediction. A score of 20 is not twice the objective risk of 10. Inherent and residual ratings are independent judgments. No percentage formula subtracts effectiveness from inherent risk.

| Level | Likelihood definition | Impact definition |
|---|---|---|
| 1 | Exceptional initiating conditions | Local reversible disruption |
| 2 | Limited opportunity | Department impact |
| 3 | Credible initiating conditions | Multiple business processes affected |
| 4 | Recurring exposure | Essential service impact or sensitive-data harm |
| 5 | Active/repeated exposure | Sustained organization-wide harm |

These are synthetic organizational criteria. They need business-specific financial, service, safety, privacy and reputational thresholds before real use. The baseline configuration stores definitions, but in-app configuration editing is not yet implemented.

Bands: 1–5 Low; 6–11 Moderate; 12–19 High; 20–25 Critical. Demo appetite: 9, an organization choice rather than a regulatory threshold. Example: inherent L=4, I=5 → 20 Critical. After tested mitigation, an analyst might independently judge residual L=2, I=4 → 8 Moderate. The rationale must explain why; the system does not infer effectiveness from those numbers.

Risk creation stores inherent rationale, control-effectiveness rationale, residual rationale, owner and assessment timestamp. The initial model uses narrative rationales; separate evidence attachments and dated effectiveness observations per risk are planned. Do not claim the seeded scenarios are evidenced risk judgments. Risk acceptance is pending until an independent GRC Manager approves with a future review date. The API forbids owner self-acceptance. Expiration date is persisted; automatic expiration/escalation is not yet implemented.

Treatments: mitigate, avoid, transfer, accept. A transfer does not erase retained obligations. What-if analysis, risk histories, configurable appetite editing and trend snapshots are planned. Matrix counts derive from persisted residual dimensions.

## Compliance

Six ratings are supported: Not Assessed, Not Applicable, Compliant, Partially Compliant, Non-Compliant, Pending Verification. Lifecycle: Draft/Returned → Submitted → Approved/Returned. Reopening an approved assessment starts reassessment and records its preceding state in the activity log.

For the selected starter set all controls have equal weight. Eligibility includes every assessment except approved, justified N/A. Unapproved N/A remains in the denominator. Only approved ratings receive score credit: Compliant=1, Partially Compliant=0.5, all others=0. The denominator includes unassessed eligible items. Empty eligibility returns null, not 100%.

`score = 100 × sum(approved rating credit) / eligible assessment count`

`coverage = 100 × assessed eligible count / eligible assessment count`

`verified = 100 × approved eligible count / eligible assessment count`

`evidence coverage = 100 × eligible assessments with any evidence / eligible assessment count`

Evidence coverage describes presence, not evidence quality or confidence. Evidence confidence scoring is not implemented. Freshness is separately calculated from organization-chosen review dates. A control may have evidence while remaining Non-Compliant. A submitted rating is not an independently verified rating. A reviewer approving a Non-Compliant assessment verifies its conclusion; it does not make it compliant.

Baseline example: five assessments, two assessed ratings, zero approvals and zero evidence. Score=0%, coverage=40%, verified=0%, evidence coverage=0%. An unapproved N/A does not improve the denominator. Approving it changes eligible count from five to four. Multiple assessments are currently counted independently; the score is an assessment-set indicator, not deduplicated framework-wide compliance.

## Independent review and remediation

The owner records a rationale, attaches evidence and submits. Reviewers must inspect evidence content, sample scope, dates and completeness. The API requires fresh decryptable evidence for non-N/A approval and rejects self-approval. Human review of content remains necessary; file presence and a digest do not establish correctness.

Finding states: Open → In Progress → Ready for Retest → Closed. The accountable owner advances work. Closure requires an independent reviewer, an approved Compliant linked assessment and a recorded rationale. An approved noncompliant assessment can be reopened, corrected, evidenced, submitted and independently retested. There is no automatic gap closure from file upload.

## Arabic summary

مصفوفة المخاطر أداة لترتيب الأولويات وليست نموذج احتمالات إحصائياً. تقدير الخطر المتبقي مستقل ويحتاج مبررات. درجات الامتثال تخص مجموعة التقييمات المختارة، ولا تعني امتثال المنشأة الكامل أو اعتمادها من جهة تنظيمية. وجود دليل لا يساوي جودة الدليل، ويظل فحص المحتوى والعينة مسؤولية المراجع المستقل.
