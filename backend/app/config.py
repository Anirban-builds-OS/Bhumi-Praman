"""
config.py
----------
Single source of truth for runtime configuration. Everything here is
overridable via environment variables (see .env.example at the repo root)
-- nothing sensitive is hard-coded, per the project's security requirements.
"""
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(REPO_ROOT / ".env"), extra="ignore")

    APP_NAME: str = "Bhumi Praman"
    ENV: str = "development"

    # Database. Defaults to a local SQLite file so the project runs with zero
    # external services during development. Point DATABASE_URL at a
    # postgresql+psycopg://... URL for a real deployment -- every query in
    # this backend goes through SQLAlchemy, so that's a config change only.
    DATABASE_URL: str = f"sqlite:///{BACKEND_DIR / 'bhumi_praman.db'}"

    # Auth
    SECRET_KEY: str = "dev-only-secret-change-me-3f8a9c2e1b7d4f6a"  # noqa: S105 -- overridden via .env in any real run
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ACCESS_TOKEN_EXPIRE_MINUTES_EXTENDED: int = 480  # "stay signed in" option on the login screen
    JWT_ALGORITHM: str = "HS256"

    # AI / OCR
    TESSERACT_CMD: str | None = None  # set only if tesseract isn't on PATH (see ai/ocr_engine.py)
    OCR_LANGUAGES: str = "en"  # comma-separated subset of en,hi,as
    CONFIDENCE_HIGH_THRESHOLD: float = 0.85  # kept identical to the tuned prototype default
    CONFIDENCE_LOW_THRESHOLD: float = 0.60

    # Storage
    STORAGE_PATH: str = str(REPO_ROOT / "storage")
    MAX_UPLOAD_SIZE_MB: int = 50

    # CORS -- the Vite dev server's default origin, override in .env for prod
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Optional: only used if you wire a real tile/geocoding provider later.
    # The GIS explorer works with OpenStreetMap tiles (no key required) by
    # default -- see frontend/src/pages/GisExplorer.tsx.
    MAP_API_KEY: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def ocr_languages_list(self) -> list[str]:
        return [lang.strip() for lang in self.OCR_LANGUAGES.split(",") if lang.strip()]


settings = Settings()

# Propagate to the AI layer, which reads TESSERACT_CMD directly from the
# environment (ai/ocr_engine.py has no FastAPI/pydantic dependency by design
# -- it stays a plain, framework-agnostic module).
if settings.TESSERACT_CMD:
    os.environ["TESSERACT_CMD"] = settings.TESSERACT_CMD

for _sub in ("uploads", "processed", "verified", "reports"):
    Path(settings.STORAGE_PATH, _sub).mkdir(parents=True, exist_ok=True)
