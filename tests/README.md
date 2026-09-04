Automated tests live next to the code they test:
- `ai/tests/` — unit/smoke tests for the OCR/extraction pipeline
- `backend/tests/` — API integration tests (FastAPI TestClient)

This top-level folder is kept for true cross-stack end-to-end tests (e.g.
Playwright driving the real browser against both servers) — not yet
written; see the README's Future Scope section.
