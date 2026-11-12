# Threat model and permissions

Assets: synthetic regulatory metadata, assessment decisions, uploaded evidence, session secrets, encryption key, audit-chain head and database. Trust boundaries: browser → proxy; proxy → API; API → database; API → filesystem; maintainer → source register. No internet-facing deployment is authorized or claimed by the local Compose configuration.

| Threat | Implemented measure | Residual risk / required next step |
|---|---|---|
| Account takeover | Argon2id; 8-hour opaque session; hashed session tokens; local generated credentials | No MFA or password recovery; add SSO/MFA before production |
| Cross-site mutation | Strict SameSite cookie, checked Origin when present, custom mutation header, no permissive CORS | Enable HTTPS and secure cookies outside localhost; review reverse-proxy trust |
| Brute force | 10 login attempts/IP/minute in memory | Single-process control; distributed rate limiter and eviction policy needed |
| Unauthorized mutation | Server role checks; ownership; validated states; independent approvals | Single organization; no tenant/RLS boundary. API service credential can access whole database |
| Injection/XSS | Pydantic validation; SQLAlchemy parameters; React escaping; Nginx CSP; no HTML rendering | Manual penetration testing and full dependency review still required |
| Malicious upload | 5 MB application limit; proxy request limit; extension/type checks; UTF-8 checks; PDF/PNG signatures; opaque encrypted files; forced downloads | No malware scanner/content disarm; don't use real sensitive evidence; PDFs can contain active payloads |
| Evidence disclosure | Fernet authenticated encryption; authenticated downloads; executive download denied | Shared encryption key, no KMS or key rotation; key loss makes evidence unrecoverable |
| Audit tampering | SHA-256 chain; verification endpoint; chained mutations | Admin can rewrite/truncate chain without external anchor; not immutable WORM storage |
| Concurrency | Optimistic expected version; row locks on PostgreSQL; advisory chain lock | PostgreSQL integration/concurrency test pending; SQLite serialized only inside process |
| CSV formula injection | Prefix dangerous starting characters before CSV serialization | Validate against target spreadsheet software if externally shared |
| Legal misinformation | Provenance fields and explicit unverified states; no unverified timers | Specialist Arabic/legal scope review remains mandatory for real operations |

No real personal data is bundled. Operators can upload arbitrary files, so local users must follow the synthetic-only demonstration policy. Avoid uploading secrets or personal data to this prototype.

## RBAC matrix

All eight roles can read organizational registry summaries, assessments, findings, risks and management reports in the single demonstration organization. Executive Viewer cannot download evidence or read activity details. The role name Privacy Officer corresponds to the requested DPO/Privacy Officer role without making an appointment determination.

| Capability | Admin | GRC manager | Compliance | Risk manager | Privacy officer | Control owner | Auditor | Executive |
|---|---|---|---|---|---|---|---|---|
| Create assessment | yes | yes | yes | no | no | yes | no | no |
| Edit draft | owner | owner | owner | no | no | owner | no | no |
| Submit / upload / reopen | owner | owner | owner | no | no | owner | no | no |
| Independent review | no | yes | no | no | no | no | yes | no |
| Register risk | yes | yes | no | yes | yes | no | no | no |
| Approve acceptance | no | independent | no | no | no | no | no | no |
| Register finding | yes | yes | yes | no | no | yes | yes | no |
| Progress finding | owner | owner | owner | no | no | owner | no | no |
| Close finding | no | independent | no | no | no | no | independent | no |
| Verify activity chain | yes | yes | no | no | no | no | yes | no |

Admin is intentionally not an independent reviewer. Ownership checks still apply to submission and evidence uploads. No user-management screen or privilege delegation API is implemented. All demo identities are provisioned explicitly by the seed command.

## Production release gates (not satisfied)

SSO/MFA, formal authorization review, deployment TLS, secure cookie enforcement, centralized rate limits, secrets manager/KMS, key rotation, malware scanning, independent security test, audited PostgreSQL concurrency, disaster recovery drill, accessibility audit, load testing, per-domain normalization, backup encryption, external audit anchors and approved regulatory scope. The feature set is for portfolio demonstration until those gates are met.
