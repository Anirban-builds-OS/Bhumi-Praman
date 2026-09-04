"""
seed.py
--------
Creates the demo users and runs the three real Crystal sample documents
through the actual pipeline (not fabricated output) so the app has
realistic data to demo immediately after setup.

Run from backend/, with the backend venv active:
    python3 ../database/seed/seed.py
"""
import json
import shutil
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
REPO_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings
from app.database.session import Base, SessionLocal, engine
from app.models.document import Document, DocumentPage
from app.models.user import User, UserRole
from app.services import document_service
from app.services.auth_service import hash_password

DEMO_USERS = [
    {"employee_code": "ADM-0001", "full_name": "Priya Bordoloi", "password": "Admin@123",
     "role": UserRole.ADMINISTRATOR, "jurisdiction": "Kamrup Metro"},
    {"employee_code": "OFC-KAM-1102", "full_name": "Rupam Bora", "password": "Officer@123",
     "role": UserRole.VERIFICATION_OFFICER, "jurisdiction": "Kamrup"},
    {"employee_code": "REC-0007", "full_name": "Anup Deka", "password": "Record@123",
     "role": UserRole.RECORD_OFFICER, "jurisdiction": "Kamrup"},
]

SAMPLE_DOCS_DIR = REPO_ROOT / "data" / "sample_documents"


class _UploadFileLike:
    """Minimal stand-in for FastAPI's UploadFile so document_service.save_upload
    can be reused unchanged by this offline script."""
    def __init__(self, path: Path, content_type: str):
        self.filename = path.name
        self.content_type = content_type
        self.file = open(path, "rb")


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print(f"Using database: {settings.DATABASE_URL}")

        users_by_code = {}
        for u in DEMO_USERS:
            existing = db.query(User).filter(User.employee_code == u["employee_code"]).first()
            if existing:
                users_by_code[u["employee_code"]] = existing
                continue
            user = User(
                employee_code=u["employee_code"], full_name=u["full_name"],
                hashed_password=hash_password(u["password"]), role=u["role"],
                jurisdiction=u["jurisdiction"],
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            users_by_code[u["employee_code"]] = user
            print(f"  created user {u['employee_code']} ({u['role'].value})")

        officer = users_by_code["OFC-KAM-1102"]

        if db.query(Document).count() > 0:
            print("Documents already exist -- skipping sample document processing (seed is idempotent).")
        else:
            sample_files = sorted(SAMPLE_DOCS_DIR.glob("*.png"))
            if not sample_files:
                print(f"WARNING: no sample documents found in {SAMPLE_DOCS_DIR}")
            for path in sample_files:
                upload = _UploadFileLike(path, "image/png")
                document = document_service.save_upload(db, upload, officer, batch_label="SEED-DEMO-BATCH")
                upload.file.close()
                print(f"  uploaded {path.name} -> document #{document.id}")
                document = document_service.process_document(db, document, officer)
                print(f"    processed -> status={document.status}")

        print("\nDemo credentials:")
        for u in DEMO_USERS:
            print(f"  {u['role'].value:<22} employee_code={u['employee_code']:<14} password={u['password']}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
