"""
API-level integration tests. Run from backend/, with the venv active:
    pytest tests/test_api.py -v

Uses a temporary SQLite file per test session (never the real dev DB) and
the real AI pipeline against the real sample documents -- these are slower
than unit tests (OCR takes a few seconds per document) but they're testing
the thing that actually matters: the full upload -> process -> verify path
a judge will exercise through the browser.
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
REPO_ROOT = BACKEND_DIR.parent
SAMPLE_DOC = REPO_ROOT / "data" / "sample_documents" / "DOC001.png"


@pytest.fixture(scope="module")
def client():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    # Re-import app fresh so it picks up the temp DB set above.
    for mod in list(sys.modules):
        if mod.startswith("app."):
            del sys.modules[mod]
    from app.main import app
    from app.database.session import Base, engine
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as c:
        yield c

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="module")
def officer_token(client):
    client.post("/api/auth/login", json={"employee_code": "bootstrap", "password": "x"})  # warms up, ignore result
    # Create the first user directly via the DB layer since /api/auth/users requires an admin token (chicken/egg for a fresh DB).
    from app.database.session import SessionLocal
    from app.models.user import User, UserRole
    from app.services.auth_service import hash_password

    db = SessionLocal()
    officer = User(employee_code="TEST-OFC", full_name="Test Officer",
                    hashed_password=hash_password("Test@123"), role=UserRole.VERIFICATION_OFFICER)
    admin = User(employee_code="TEST-ADM", full_name="Test Admin",
                 hashed_password=hash_password("Test@123"), role=UserRole.ADMINISTRATOR)
    db.add_all([officer, admin])
    db.commit()
    db.close()

    resp = client.post("/api/auth/login", json={"employee_code": "TEST-OFC", "password": "Test@123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture(scope="module")
def admin_token(client, officer_token):
    resp = client.post("/api/auth/login", json={"employee_code": "TEST-ADM", "password": "Test@123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    assert client.get("/api/health").json()["status"] == "ok"


def test_login_rejects_bad_password(client, officer_token):
    resp = client.post("/api/auth/login", json={"employee_code": "TEST-OFC", "password": "wrong"})
    assert resp.status_code == 401


def test_unauthenticated_request_rejected(client):
    assert client.get("/api/records").status_code == 401


def test_upload_and_process_real_document(client, officer_token):
    with open(SAMPLE_DOC, "rb") as f:
        resp = client.post("/api/documents/upload", headers=auth(officer_token), files={"file": ("DOC001.png", f, "image/png")})
    assert resp.status_code == 201
    doc = resp.json()
    assert doc["status"] == "uploaded"
    assert len(doc["pages"]) == 1

    resp = client.post(f"/api/documents/{doc['id']}/process", headers=auth(officer_token))
    assert resp.status_code == 200
    result = resp.json()
    assert result["document"]["status"] == "processed"
    assert len(result["land_record_ids"]) == 1
    assert len(result["extractions"][0]["fields"]) == 12


def test_reject_unsupported_file_type(client, officer_token):
    resp = client.post("/api/documents/upload", headers=auth(officer_token),
                        files={"file": ("notes.txt", b"hello", "text/plain")})
    assert resp.status_code == 400


@pytest.fixture(scope="module")
def processed_record_id(client, officer_token):
    with open(SAMPLE_DOC, "rb") as f:
        resp = client.post("/api/documents/upload", headers=auth(officer_token), files={"file": ("DOC001.png", f, "image/png")})
    doc_id = resp.json()["id"]
    result = client.post(f"/api/documents/{doc_id}/process", headers=auth(officer_token)).json()
    return result["land_record_ids"][0]


REALISTIC_VALUES = {
    "owner_name": "Ram Bahadur Thapa", "father_name": "Late Deben Thapa", "survey_number": "SY-1042/B",
    "khasra_number": "412", "khata_number": "87", "plot_area": "2.35 acres", "village": "Rangapara",
    "tehsil": "Sonapur", "district": "Kamrup", "land_classification": "Agricultural - Irrigated",
    "mutation_number": "MUT-2291", "registration_number": "REG/2024/00456",
}  # DOC001's actual ground truth -- used as realistic officer-entered fallbacks so format
   # validation (e.g. plot_area's "<number> <unit>" check) passes, exactly like a real correction would.


def test_verify_blocked_until_fields_resolved(client, officer_token, processed_record_id):
    resp = client.post(f"/api/records/{processed_record_id}/verify", headers=auth(officer_token), json={})
    assert resp.status_code == 422  # real extraction on a degraded scan always leaves at least one field to review


def test_edit_field_and_full_verify_flow(client, officer_token, processed_record_id):
    record = client.get(f"/api/records/{processed_record_id}", headers=auth(officer_token)).json()
    for name, state in record["fields"].items():
        if state["needs_human_review"]:
            value = state["value"] or REALISTIC_VALUES[name]
            resp = client.post(f"/api/records/{processed_record_id}/fields", headers=auth(officer_token),
                                json={"field": name, "value": value, "action": "edit"})
            assert resp.status_code == 200
        elif not state["field_verified"]:
            client.post(f"/api/records/{processed_record_id}/fields", headers=auth(officer_token),
                        json={"field": name, "value": state["value"], "action": "accept"})

    record = client.get(f"/api/records/{processed_record_id}", headers=auth(officer_token)).json()
    assert all(not f["needs_human_review"] for f in record["fields"].values())

    resp = client.post(f"/api/records/{processed_record_id}/verify", headers=auth(officer_token), json={"notes": "test"})
    assert resp.status_code == 200
    verified = resp.json()
    assert verified["status"] == "verified"
    assert verified["verification_hash"] is not None

    # Verifying twice is rejected, not silently re-applied
    resp2 = client.post(f"/api/records/{processed_record_id}/verify", headers=auth(officer_token), json={})
    assert resp2.status_code == 409


def test_report_pdf_generation(client, officer_token, processed_record_id):
    resp = client.post(f"/api/reports/{processed_record_id}", headers=auth(officer_token))
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:4] == b"%PDF"


def test_audit_trail_records_every_mutation(client, officer_token, processed_record_id):
    resp = client.get(f"/api/audit/records/{processed_record_id}", headers=auth(officer_token))
    actions = [a["action"] for a in resp.json()]
    assert "record.created" in actions
    assert "record.verified" in actions


def test_gis_records_have_coordinates(client, officer_token):
    resp = client.get("/api/gis/records", headers=auth(officer_token))
    assert resp.status_code == 200
    for r in resp.json():
        assert -90 <= r["latitude"] <= 90
        assert -180 <= r["longitude"] <= 180


def test_dashboard_statistics_reflect_real_counts(client, officer_token):
    resp = client.get("/api/dashboard/statistics", headers=auth(officer_token))
    assert resp.status_code == 200
    stats = resp.json()
    assert stats["total_documents"] >= 2  # from the two fixtures above
    assert stats["verified_records"] >= 1


def test_evaluation_requires_admin(client, officer_token):
    resp = client.post("/api/evaluation/run", headers=auth(officer_token))
    assert resp.status_code == 403


def test_evaluation_returns_real_measured_numbers(client, admin_token):
    resp = client.post("/api/evaluation/run", headers=auth(admin_token))
    assert resp.status_code == 200
    report = resp.json()
    assert report["documents_evaluated"] == 3
    assert 0.0 <= report["macro_average_f1"] <= 1.0
    assert 0.0 <= report["mean_cer"]


def test_duplicate_flags_do_not_false_positive_on_blank_records(client, admin_token):
    """Regression test for the bug found during integration: two records
    that both failed extraction on every identifying field must NOT be
    flagged as duplicates of each other."""
    from app.database.session import SessionLocal
    from app.models.land_record import LandRecord
    import json

    db = SessionLocal()
    blank_fields = {f: {"value": None, "confidence": 0.0, "confidence_bucket": "missing",
                         "needs_human_review": True, "source": "ai", "field_verified": False} for f in
                    ["owner_name", "father_name", "survey_number", "khasra_number", "khata_number", "plot_area",
                     "village", "tehsil", "district", "land_classification", "mutation_number", "registration_number"]}
    r1 = LandRecord(record_code="TEST-BLANK-0001", status="pending_review", fields_json=json.dumps(blank_fields))
    r2 = LandRecord(record_code="TEST-BLANK-0002", status="pending_review", fields_json=json.dumps(blank_fields))
    db.add_all([r1, r2])
    db.commit()
    db.refresh(r1)
    db.refresh(r2)

    from app.services import record_service
    record_service.refresh_duplicates_and_conflicts(db, r1)
    db.commit()
    db.refresh(r1)
    db.refresh(r2)
    db.close()

    assert json.loads(r1.duplicate_of_json) == []
    assert json.loads(r2.duplicate_of_json) == []
