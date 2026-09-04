No migration tool is wired in yet — the prototype uses
`Base.metadata.create_all()` on startup against SQLite, which is fine for
a from-scratch dev database but doesn't handle schema changes to existing
data. Before a real deployment (especially once on PostgreSQL), introduce
Alembic here: `pip install alembic`, `alembic init database/migrations`,
point `sqlalchemy.url` at `DATABASE_URL`, and `alembic revision
--autogenerate` off the models in `backend/app/models/`.
