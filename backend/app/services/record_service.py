import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.document import DocumentPage, Extraction
from app.models.land_record import FIELD_NAMES, LandRecord
from app.models.user import User
from app.services import gis_service, pipeline_service
from app.services.audit_service import log_action


def _sync_flat_columns(record: LandRecord, fields: dict) -> None:
    for name in FIELD_NAMES:
        setattr(record, name, (fields.get(name) or {}).get("value"))
    record.fields_json = json.dumps(fields)
    confidences = [f["confidence"] for f in fields.values()] if fields else []
    record.record_confidence = round(sum(confidences) / len(confidences), 3) if confidences else 0.0


def _record_code(district: str | None, record_id: int) -> str:
    year = datetime.now(timezone.utc).year
    district_code = "".join(ch for ch in (district or "XXX") if ch.isalpha())[:3].upper() or "XXX"
    return f"REC-AS-{district_code}-{year}-{record_id:04d}"


def create_from_extraction(db: Session, page: DocumentPage, extraction: Extraction, actor: User) -> LandRecord:
    fields = json.loads(extraction.fields_json)
    record = LandRecord(
        record_code="PENDING",  # replaced below once we have a real id
        document_page_id=page.id,
        extraction_id=extraction.id,
        status="pending_review",
        validation_issues_json=extraction.validation_issues_json,
        created_by_id=actor.id if actor else None,
    )
    _sync_flat_columns(record, fields)
    db.add(record)
    db.commit()
    db.refresh(record)

    record.record_code = _record_code(record.district, record.id)
    record.latitude, record.longitude = gis_service.assign_coordinates(record.village, record.district, record.record_code)
    refresh_duplicates_and_conflicts(db, record)
    db.commit()
    db.refresh(record)

    log_action(db, actor, "record.created", "land_record", record.id, notes=f"Created from extraction {extraction.id}")
    return record


def refresh_duplicates_and_conflicts(db: Session, record: LandRecord) -> None:
    """Recomputes duplicate/conflict flags across every active record, not
    just this one, and writes the result back to every row that changed.
    (Fixed during integration testing: a single-record view goes stale the
    moment a *new* record collides with an *older* one -- e.g. record B is
    clean when created, then record C arrives sharing its khasra number;
    without this, B never learns it now has a conflict.)"""
    active = (
        db.query(LandRecord)
        .filter(LandRecord.status != "rejected", LandRecord.id != record.id)
        .all()
    )
    by_code: dict[str, LandRecord] = {r.record_code: r for r in active}
    by_code[record.record_code] = record  # in-memory record may not be queryable yet on first creation

    all_fields = {code: json.loads(r.fields_json) for code, r in by_code.items()}
    dupes, conflicts = pipeline_service.compute_batch_duplicates_and_conflicts(all_fields)

    for code, r in by_code.items():
        new_dupes = json.dumps(dupes.get(code, []))
        new_conflicts = json.dumps(conflicts.get(code, []))
        if r.duplicate_of_json != new_dupes:
            r.duplicate_of_json = new_dupes
            db.add(r)
        if r.conflicts_json != new_conflicts:
            r.conflicts_json = new_conflicts
            db.add(r)


def edit_field(db: Session, record: LandRecord, field: str, value: str | None, action: str, actor: User) -> LandRecord:
    if field not in FIELD_NAMES:
        raise ValueError(f"Unknown field: {field}")

    fields = json.loads(record.fields_json)
    current = fields.get(field, {"value": None, "confidence": 0.0, "confidence_bucket": "missing",
                                  "needs_human_review": True, "source": "ai", "field_verified": False,
                                  "pattern_confidence": 0.0, "ocr_confidence": 0.0, "location": None})
    old_value = current.get("value")

    if action == "edit":
        current["value"] = value
        current["source"] = "officer"
        current["field_verified"] = True
        current["needs_human_review"] = False
        current["confidence"] = 1.0
        current["confidence_bucket"] = "high"
        # The old highlight box located the AI's original value on the page.
        # A hand-typed replacement value may not be at that position (or on
        # the page at all), so the stale box would mislead rather than
        # help -- clear it rather than show a highlight that no longer
        # matches what's displayed.
        current["location"] = None
    elif action == "accept":
        current["field_verified"] = True
        current["needs_human_review"] = False
    elif action == "reject":
        current["value"] = None
        current["field_verified"] = False
        current["needs_human_review"] = True
        current["location"] = None
        current["confidence"] = 0.0
        current["confidence_bucket"] = "missing"
        current["source"] = "officer"
    else:
        raise ValueError(f"Unknown action: {action}")

    fields[field] = current
    _sync_flat_columns(record, fields)

    if field == "village":
        record.latitude, record.longitude = gis_service.assign_coordinates(record.village, record.district, record.record_code)

    record.validation_issues_json = json.dumps(pipeline_service.validate_fields(fields))
    refresh_duplicates_and_conflicts(db, record)

    db.commit()
    db.refresh(record)

    log_action(
        db, actor, f"record.field_{action}", "land_record", record.id,
        field_name=field, old_value=str(old_value) if old_value is not None else None,
        new_value=str(current.get("value")) if current.get("value") is not None else None,
    )
    return record


def verify_record(db: Session, record: LandRecord, actor: User, notes: str | None = None) -> LandRecord:
    fields = json.loads(record.fields_json)
    canonical = json.dumps(
        {name: (fields.get(name) or {}).get("value") for name in FIELD_NAMES}, sort_keys=True
    )
    digest = hashlib.sha256(f"{record.record_code}|{canonical}|{actor.id}".encode("utf-8")).hexdigest()

    record.status = "verified"
    record.verified_by_id = actor.id
    record.verified_at = datetime.now(timezone.utc)
    record.verification_hash = digest
    db.commit()
    db.refresh(record)

    log_action(db, actor, "record.verified", "land_record", record.id, notes=notes)
    return record


def reject_record(db: Session, record: LandRecord, actor: User, reason: str) -> LandRecord:
    record.status = "rejected"
    record.rejection_reason = reason
    db.commit()
    db.refresh(record)

    log_action(db, actor, "record.rejected", "land_record", record.id, notes=reason)
    return record
