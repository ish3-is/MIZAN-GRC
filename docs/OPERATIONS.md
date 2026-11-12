# Local operations

## Windows with Docker (prepared; runtime not verified in this environment)

Prerequisites: Docker Desktop with Linux containers running; Git; PowerShell. The build uses Node 24 and Python 3.12 images.

```powershell
./scripts/bootstrap.ps1
docker compose config --quiet
docker compose up --build -d
docker compose ps
```

Open http://localhost:8080. Read `DEMO_PASSWORD` from the ignored local `.env`. Accounts: `owner`, `auditor`, `manager`, `risk`, `privacy`, `compliance`, `executive`, `admin`. Every account is nonproduction. Credentials are generated locally rather than published in README. Do not post the `.env`, password or encryption key in issues/screenshots.

The proxy binds to loopback. Database and backend are not published to the host. Use HTTPS, secure cookies and a reviewed deployment configuration before remote exposure. Do not set `SECURE_COOKIES=true` on plain HTTP localhost; the cookie then will not be sent.

## Native fallback (verified locally)

```powershell
python -m venv .venv
./.venv/Scripts/python -m pip install -r backend/requirements.txt
./scripts/bootstrap.ps1
cd frontend
npm ci
cd ..
./scripts/start-local.ps1 backend
```

In a second terminal at the repository root:

```powershell
./scripts/start-local.ps1 frontend
```

Open http://localhost:5173. Native development explicitly allows localhost and 127.0.0.1 on ports 5173/5174 for browser Origin checks. Setting APP_ORIGIN or APP_ORIGINS replaces that fallback with the configured allowlist; arbitrary origins remain rejected. Vite now uses strict port 5173, and startup scripts reuse a running MIZAN service instead of creating a duplicate on another port. API health: http://127.0.0.1:8000/api/health. OpenAPI: http://127.0.0.1:8000/docs and `/openapi.json`. Native fallback uses the ignored root `mizan.db` and ignored `data/evidence`. Database schema is applied with Alembic, not application startup table creation.

## Verification

```powershell
./.venv/Scripts/python -m pytest backend/tests -q
./.venv/Scripts/python scripts/verify-register.py
cd frontend
npm test
npm run build
npm audit
npx playwright install chromium
npm run test:e2e
```

Browser tests need both native services and a clean seeded database. They mutate the demo by adding one independently approved assessment. Backend tests use an isolated temporary SQLite database, never the demo database. `TEST_DATABASE_URL` support for PostgreSQL integration is planned; current tests do not exercise PostgreSQL.

## Seed reset

Seeding is deterministic in identifiers, counts and scenario ratings. Password hashes and uploaded content metadata intentionally vary. Seed is idempotent once a user exists; it does not overwrite work. Do not call a test reset against valuable data.

For a fresh demonstration, stop services and archive the local `mizan.db` and `data/evidence` together, then rerun the native startup. Keep `.env` alongside encrypted backups; never rotate the evidence key without re-encryption. A destructive automated reset button is intentionally not exposed. Docker reset can be done only after backup using `docker compose down --volumes`; this irreversibly deletes database/evidence volumes. The command is guidance, not something run by this delivery.

## Backup and restore guidance (drill pending)

1. Stop writes and retain an externally stored activity-chain head.
2. Export PostgreSQL with `pg_dump` using the database service; do not put secrets in shell arguments or logs. Copy encrypted evidence with the same point-in-time snapshot.
3. Store database dump, evidence volume, image/revision references, source-register revision and audit head. Back up the encryption key separately under controlled access; encrypt the backup.
4. Restore into an isolated environment with matching key, migrate only as documented, inspect row counts and foreign keys, verify evidence digest/decryption and audit chain, then run a smoke assessment.
5. Record restoration time, missing objects and approvals. No RPO/RTO is claimed until a restore drill has been executed.

## Health and limitations

Health checks query the database and report service version. They do not validate every evidence object, verify current legal sources or measure readiness for production. Encryption key validation occurs on backend startup. Forgotten keys cannot be reconstructed. No mail, external notification service, Redis worker, regulatory polling or paid AI is configured.
