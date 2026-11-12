# MIZAN architecture and critical decisions

Status: operating-system simulation v0.2, 12 November 2026. This is a single-organization portfolio demonstrator, not an enterprise production release.

## Critical architecture plan

1. Regulatory provenance is separate from legal applicability. Record access, exact-reference inspection and specialist interpretation as distinct states. Never infer statutory deadlines from generic task due dates.
2. Build the assessment-to-remediation workflow first, then add a shared operational-record kernel for governance, policy, privacy, supplier, incident, continuity, training and audit domains. A domain is presented as writable only when its transitions and authorization rules exist.
3. Serve React and FastAPI on one browser origin. Use opaque server-side sessions, HttpOnly cookies and a required custom mutation header. Do not store tokens in browser storage.
4. Run one API worker in the initial single-organization deployment. PostgreSQL serializes activity-chain writes using an advisory transaction lock; affected workflow rows use row locks. SQLite is the local verification fallback, not the production concurrency target.
5. Persist core assessment/evidence relationships with foreign keys. Versioned work items normalize ownership, review, approval, due date, lifecycle and history while retaining domain-specific fields in JSON. Explicit relationship edges record cross-domain rationale and review. Further normalization is still required for large production deployments.
6. Encrypt evidence before filesystem writes; use opaque names, authenticated encryption and plaintext SHA-256 integrity verification. Keep the encryption key outside Git. Database and evidence backup consistency matters.
7. Reserve legal interpretation, applicability approval, mapping equivalence and final decisions for authorized humans. No AI API dependency.

## Component diagram

```mermaid
flowchart LR
  A[Arabic / English browser] -->|same origin session| N[Nginx / local Vite proxy]
  N --> R[React + TanStack Query + Router]
  N --> F[FastAPI / OpenAPI]
  F --> I[Identity and authorization]
  F --> C[Assessments and independent review]
  F --> M[Risk and remediation]
  F --> E[Encrypted evidence]
  F --> L[Hash-chained activity]
  F --> O[Operational domain workflows]
  F --> P[Reporting and registries]
  C --> D[(PostgreSQL)]
  M --> D
  I --> D
  L --> D
  P --> D
  O --> D
  E --> S[(Encrypted filesystem volume)]
```

## Current ERD

```mermaid
erDiagram
  USER ||--o{ SESSION : authenticates
  USER ||--o{ ASSESSMENT : owns
  USER ||--o{ ASSESSMENT : reviews
  RECORD ||--o{ ASSESSMENT : control
  RECORD ||--o{ ASSESSMENT : asset
  ASSESSMENT ||--o{ EVIDENCE : supported_by
  ASSESSMENT ||--o{ FINDING : exposes
  RECORD ||--o{ FINDING : risk
  USER ||--o{ FINDING : accountable
  USER ||--o{ EVIDENCE : uploads
  USER ||--o{ WORK_ITEM : owns
  WORK_ITEM ||--o{ APPROVAL : records
  WORK_ITEM ||--o{ POLICY_ACKNOWLEDGEMENT : receives
  RECORD {
    int id PK
    string kind
    string title
    string department
    json payload
    int version
  }
  ASSESSMENT {
    int id PK
    int control_id FK
    int asset_id FK
    int owner_id FK
    int reviewer_id FK
    string status
    string stage
    string rationale
    string period
    int version
  }
  EVIDENCE {
    int id PK
    int assessment_id FK
    string sha256
    string storage_key
    string review_due
  }
  FINDING {
    int id PK
    int assessment_id FK
    int risk_id FK
    int owner_id FK
    string state
    string due
  }
  ACTIVITY {
    int id PK
    string actor
    string action
    string target
    json details
    string previous_hash
    string digest
  }
  WORK_ITEM {
    int id PK
    string uid UK
    string domain
    string record_type
    string status
    int owner_id FK
    int reviewer_id FK
    int approver_id FK
    json payload
    int version
  }
  RELATIONSHIP {
    int id PK
    string source_type
    int source_id
    string target_type
    int target_id
    string relation
    string rationale
  }
  APPROVAL {
    int id PK
    int work_item_id FK
    int actor_id FK
    string decision
    string rationale
  }
```

## Extended target model

Organization → department / process / asset / vendor; framework → source revision → requirement; requirement ↔ control through reviewed mappings; control ↔ asset/process; assessment → immutable assessment revision → evidence version → reviewer signoff; finding → risk → treatment → approval; privacy inventory → processing activity → PIA / rights / breach / transfer case. Reports snapshot scope and source revisions. Every cross-framework mapping stores intent overlap, exclusions, reviewer and review date. Similar titles alone never establish equivalence.

The current app has one deployment per organization. It has no tenant identifier and must not be marketed or used as multi-tenant software. The database credential is an application service identity; end-user authorization lives in FastAPI. PostgreSQL row-level security is not implemented.

## Data-flow and trust boundaries

```mermaid
sequenceDiagram
  actor Owner
  actor Auditor
  participant Browser
  participant API
  participant DB
  participant Vault as Evidence volume
  Owner->>Browser: Enter rating and rationale
  Browser->>API: Session + CSRF header + expected version
  API->>DB: Validate role, owner and workflow state
  API->>DB: Save rating and hash-chained activity
  Owner->>API: Upload synthetic evidence
  API->>Vault: Authenticated ciphertext under opaque name
  API->>DB: Evidence digest and review date
  Owner->>API: Submit
  Auditor->>API: Download and inspect evidence
  API->>Vault: Decrypt and verify digest
  Auditor->>API: Independent approval with rationale
  API->>DB: Reject self-approval; persist reviewer and event
  API->>Browser: Scoped report with source references
```

## Operational decisions

No Redis or background scheduler in v0.2. Overdue findings, remediation and evidence freshness are calculated at request time; no emails or notification delivery is claimed. No paid AI or automatic legal conclusions. No separate requirement table yet: selected starter control provenance is embedded in control documents. No standards text is redistributed. External Google Fonts are optional presentation dependencies; system fallbacks work offline. Self-host fonts before restricted-network use.

Frontend uses plain CSS tokens rather than Tailwind. FastAPI route modules separate identities, compliance, risk, remediation, evidence, operational domains, audit, reporting and registries; shared authentication and audit primitives live in `core.py`. Governance and privacy use the versioned operational kernel. The React workspace is still a single component module; domain component extraction and dedicated service/repository layers are required before production scale. These choices prioritize an inspectable, tested release while explicitly limiting architectural claims.
