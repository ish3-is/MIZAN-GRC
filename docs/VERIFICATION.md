# Executed verification record

## Local login address correction

Corrected the local Origin allowlist for localhost/127.0.0.1 on explicit development ports; configured deployment origins still override it. Unauthorized origins now receive a structured error. Strict Vite port and existing-service detection prevent accidental duplicate startup. Executed backend suite: **12 passed**, one upstream deprecation warning. Actual Chromium login at `http://127.0.0.1:5173/` passed. Both startup commands correctly detected existing services.

## MaDar dark appearance update — 18 October 2026

Added default dark appearance, saved light/dark selection, pre-paint theme initialization, and the user-supplied unmodified MaDar Academy logo with bilingual attribution on sign-in, sidebar and footer. Executed production build and frontend unit suite: passed (2 tests). An actual Chromium check verified dark default, light preference after reload, original logo decoding, authenticated desktop/mobile rendering, no horizontal page overflow at 390px, and no captured page errors. Screenshots: `login-madar-dark.png`, `dashboard-madar-dark.png`, `dashboard-madar-light.png`, `mobile-madar-dark.png`. Inspected the login and dashboard images visually. This appearance update does not change regulatory or backend workflows.

Date: 18 October 2026. Host: Windows, Python 3.12.1, Node 24.13.1. Native FastAPI + Vite with SQLite. These are executed observations, not a certification or penetration-test report.

| Check | Observed result | Scope |
|---|---|---|
| `python -m pytest backend/tests -q` | **10 passed**, one upstream TestClient deprecation warning | Full assessment/evidence/risk/finding/retest/report chain; RBAC, sessions, CSRF/Origin rejection, version conflicts, evidence signature/freshness, N/A exclusion, self-approval denial, audit/evidence tampering, rate limiting, audit-pack hashes, ownership and risk-acceptance denial |
| `npm test` | **2 passed** | API helper includes CSRF/same-origin settings and surfaces server errors |
| `npm run build` | **Passed** | TypeScript build and production Vite bundle; manual vendor/chart chunks remove earlier size warning |
| `npm run test:e2e` | **1 passed**, final run 5.7 seconds total | Actual Chromium: Arabic RTL, English LTR, assessment create/save, encrypted upload, submission, reload persistence, separate auditor approval, mobile width and no captured browser page errors |
| `python scripts/verify-register.py` | **7 source records passed** | Required fields, publisher hosts, allowed states, unique framework IDs; does not validate legal interpretation |
| `ruff check backend scripts/verify-register.py --select F` | **Passed** | Undefined/unused Python name checks |
| `ruff format --check backend` | **Passed** before final main-module format; final main module formatted | Python format check; no functional claim |
| `alembic current` | **0001 (head)** | Native SQLite migrated schema |
| `alembic check` | **No new upgrade operations detected** | SQLAlchemy metadata matches migrated native schema |
| `pip check` | **No broken requirements found** | Installed Python compatibility |
| `pip-audit -r backend/requirements.txt` | **No known vulnerabilities found** | Resolved Python dependencies at audit time; JSON saved |
| `npm audit` | **0 vulnerabilities reported** | All installed frontend dependencies at audit time; JSON saved |
| `docker compose config --quiet` | **Passed** | Compose interpolation/configuration only |
| Docker engine / Compose runtime | **Unavailable / not run** | Docker 29.5.3 CLI installed; engine pipe unavailable even after launching Docker Desktop |
| Sample audit ZIP verification | **Passed**, 2 synthetic evidence documents at generation | Recomputed SHA-256 matches manifest; management/source provenance included |
| Visual review | **Performed** | Arabic dashboard, English dashboard, mobile screenshot inspected; RTL chart direction and mobile table readability corrected |

Captured screenshots are real local application states. Repeated browser tests add an approved assessment; screenshots therefore differ from the clean seed's five-assessment baseline. They are not fictitious dashboard values. The heatmap and chart use persisted risk records. Test runs use synthetic-only file content.

## Test-driven corrections during implementation

The first frontend unit run attempted to collect the Playwright suite; a dedicated Vitest include pattern corrected test separation. TypeScript caught an unknown JSON payload used as a React conditional; it was explicitly converted to boolean. Initial dependency pins had known advisories and were updated before final scans. Windows temporary SQLite cleanup required disposing the engine. Refactoring route domains exposed intentional side-effect imports to lint; explicit exports corrected the check. Final test/build results above refer to corrected versions.

## Not verified

PostgreSQL runtime, concurrent transaction behavior, Docker image startup, container permissions, Linux CI execution, deployment HTTPS, multi-tenant isolation (not implemented), backup recovery drill, malware detection, formal WCAG compliance, screen-reader audit, full Arabic content translation, large-file/load/performance testing, independent penetration testing, source currency beyond the recorded checks, legal applicability and specialist Arabic interpretation.

The security controls are demonstrator implementations with documented residual risks. Zero dependency advisories is a point-in-time package scan, not evidence that the application has no vulnerabilities. A chained activity log needs external head anchoring to detect administrative rewrite or truncation. No claim of official compliance, certification, regulatory approval or legal advice is made.
