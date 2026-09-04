The schema is defined as SQLAlchemy models in `backend/app/models/` (the
single source of truth) rather than duplicated here as static SQL — see
that folder, or run the backend once and inspect `bhumi_praman.db`
directly, for the current table definitions.
