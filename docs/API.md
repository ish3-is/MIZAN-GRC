# API contract

## Operational-domain API (v0.2)

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/work-items?domain=&status=&q=` | Search versioned governance, policy, privacy, vendor, incident, continuity, training, audit, gap, remediation and evidence-metadata records |
| POST | `/api/work-items` | Create a simulated operational record with owner, reviewer and approver separation |
| GET / PUT | `/api/work-items/{id}` | Read or update a version-checked record |
| POST | `/api/work-items/{id}/transition` | Apply a validated lifecycle transition with rationale and approval history |
| GET / POST | `/api/relationships` | Read or create reviewed cross-domain traceability edges |
| GET | `/api/policies/effectiveness` | Report document, approval, publication, acknowledgement, procedure, operation, evidence and independent-test states separately |
| GET | `/api/policy-acknowledgements` | List the representative acknowledgement sample |
| POST | `/api/policy-acknowledgements/{id}/acknowledge` | Record an attributable policy acknowledgement |
| PUT | `/api/users/{id}/role` | Super Admin role assignment; self-role change is blocked |

Every mutation requires the authenticated HttpOnly session and `X-Mizan-Request: 1`. Approval/closure transitions are enforced on the server and reject owner or reviewer self-approval. Operational records use optimistic version checks. Domain-specific payloads remain JSON in v0.2; production specialization and generated response schemas remain follow-up work.

FastAPI produces the live contract at `/openapi.json` and interactive `/docs`. A generated snapshot accompanies this release. No API token is embedded in the frontend.

Authentication: POST `/api/login` with username/password; HttpOnly cookie `mizan_session`. Mutations require `X-Mizan-Request: 1`, and browser Origin must match configured APP_ORIGIN. Eight-hour session. Use same-origin proxy. JSON errors have `detail`; access errors 401/403, workflow/version conflicts 409, validation 422. Upload oversize 413, rate limit 429. Domain routes authorize users before mutations.

| Group | Endpoints |
|---|---|
| Identity | POST login/logout, GET me/users/health |
| Registry | GET records/{kind}; kinds source/control/asset/risk/vendor/policy/ropa/privacy_case/configuration/department |
| Assessment | GET/POST assessments; PUT assessments/{id}; POST submit/review/reopen |
| Evidence | POST assessments/{id}/evidence; GET evidence; GET evidence/{id}/download |
| Risk | POST risks; POST risks/{id}/accept |
| Remediation | GET/POST findings; POST findings/{id}/transition |
| Reporting | GET dashboard; GET reports/management; GET reports/risks.csv; GET reports/audit-pack.zip |
| Audit | GET activity; GET activity/verify |

Assessment update requires status, rationale (10–4000 characters) and expected version. Owner-only mutation in Draft/Returned. Submit requires evidence for non-N/A. Review is separate role/identity with explicit rationale. A fresh, decryptable evidence item is required; reviewer decides whether it supports the entire conclusion. Older files remain available; they are not automatically treated as proof.

Risk creation requires asset ID, department/title, inherent/residual dimensions (1–5), three independent narrative rationales and treatment. Acceptance requires an independent GRC Manager, rationale and future review date. There is no automatic legal acceptance authority inference.

Finding creation links assessment, risk, owner, due date, title and corrective action. Its state transition API validates owner progression and independent closure conditions.

The initial OpenAPI response types for registry/report dictionaries are broad; richer typed response contracts and pagination are planned. Source/control payload provenance shape is validated separately. No tenant API exists. The frontend and backend enforce a single-organization scope.
