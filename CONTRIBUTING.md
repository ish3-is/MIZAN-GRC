# Contributing to MIZAN

MIZAN is a portfolio simulation with strict provenance and no real personal data. Contributions must preserve that boundary.

1. Create a focused branch and describe the business scenario and affected roles.
2. Do not commit `.env`, databases, evidence files, tokens, customer data or proprietary standards text.
3. For a regulatory change, update `regulatory/sources.json`, record the official publisher URL and verification date, distinguish source access from legal interpretation, and run `python scripts/verify-register.py`.
4. Do not mark a requirement verified, applicable or equivalent without evidence and independent review.
5. Add API negative tests for authorization and invalid workflow transitions.
6. Run backend tests, frontend tests, production build and the relevant Playwright flow before opening a review.
7. Update `docs/IMPLEMENTATION_CHECKLIST.md` and state remaining limitations honestly.

Generated demonstration records must include `SIMULATED DATA — NOT REAL ORGANIZATIONAL EVIDENCE`.
