import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.auth import get_current_user, require_verifier
from app.models.land_record import LandRecord
from app.models.user import User
from app.schemas.land_record import (
    FieldEditRequest, LandRecordOut, LandRecordSummary, PaginatedRecords,
    RecordRejectRequest, RecordVerifyRequest,
)
from app.services import pipeline_service, record_service
from app.services.audit_service import log_action

router = APIRouter(prefix="/api/records", tags=["records"])


def _summary(r: LandRecord) -> LandRecordSummary:
    return LandRecordSummary(
        id=r.id, record_code=r.record_code, status=r.status,
        owner_name=r.owner_name, survey_number=r.survey_number, khasra_number=r.khasra_number,
        khata_number=r.khata_number, village=r.village, tehsil=r.tehsil, district=r.district,
        record_confidence=r.record_confidence,
        has_validation_issues=bool(json.loads(r.validation_issues_json or "[]")),
        has_duplicates=bool(json.loads(r.duplicate_of_json or "[]")),
        has_conflicts=bool(json.loads(r.conflicts_json or "[]")),
        updated_at=r.updated_at,
    )


def _detail(r: LandRecord) -> LandRecordOut:
    return LandRecordOut(
        id=r.id, record_code=r.record_code, document_page_id=r.document_page_id,
        document_id=r.document_page.document_id if r.document_page_id and r.document_page else None,
        extraction_id=r.extraction_id,
        page_image_width=r.document_page.image_width if r.document_page_id and r.document_page else None,
        page_image_height=r.document_page.image_height if r.document_page_id and r.document_page else None,
        status=r.status, owner_name=r.owner_name, father_name=r.father_name, survey_number=r.survey_number,
        khasra_number=r.khasra_number, khata_number=r.khata_number, plot_area=r.plot_area, village=r.village,
        tehsil=r.tehsil, district=r.district, land_classification=r.land_classification,
        mutation_number=r.mutation_number, registration_number=r.registration_number,
        latitude=r.latitude, longitude=r.longitude,
        fields=json.loads(r.fields_json or "{}"),
        validation_issues=json.loads(r.validation_issues_json or "[]"),
        duplicate_of=json.loads(r.duplicate_of_json or "[]"),
        conflicts=json.loads(r.conflicts_json or "[]"),
        record_confidence=r.record_confidence, verification_hash=r.verification_hash,
        rejection_reason=r.rejection_reason, created_by_id=r.created_by_id, verified_by_id=r.verified_by_id,
        verified_by_name=r.verified_by.full_name if r.verified_by_id and r.verified_by else None,
        verified_at=r.verified_at, created_at=r.created_at, updated_at=r.updated_at,
    )


@router.get("", response_model=PaginatedRecords)
def list_records(
    query: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    district: str | None = None,
    tehsil: str | None = None,
    village: str | None = None,
    needs_review_only: bool = False,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(LandRecord)
    if status_filter:
        q = q.filter(LandRecord.status == status_filter)
    if district:
        q = q.filter(LandRecord.district.ilike(f"%{district}%"))
    if tehsil:
        q = q.filter(LandRecord.tehsil.ilike(f"%{tehsil}%"))
    if village:
        q = q.filter(LandRecord.village.ilike(f"%{village}%"))
    if needs_review_only:
        q = q.filter(LandRecord.status == "pending_review")
    if query:
        like = f"%{query}%"
        q = q.filter(or_(
            LandRecord.record_code.ilike(like), LandRecord.owner_name.ilike(like),
            LandRecord.survey_number.ilike(like), LandRecord.khasra_number.ilike(like),
            LandRecord.khata_number.ilike(like), LandRecord.village.ilike(like),
        ))

    total = q.count()
    items = (
        q.order_by(LandRecord.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedRecords(items=[_summary(r) for r in items], total=total, page=page, page_size=page_size)


@router.get("/{record_id}", response_model=LandRecordOut)
def get_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.get(LandRecord, record_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record not found")
    return _detail(record)


@router.post("/{record_id}/fields", response_model=LandRecordOut)
def edit_field(record_id: int, payload: FieldEditRequest, db: Session = Depends(get_db), current_user: User = Depends(require_verifier)):
    record = db.get(LandRecord, record_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record not found")
    if record.status == "verified":
        raise HTTPException(status.HTTP_409_CONFLICT, "Record is already verified and locked. Reopen is not supported in this prototype.")
    try:
        record = record_service.edit_field(db, record, payload.field, payload.value, payload.action, current_user)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    return _detail(record)


@router.post("/{record_id}/validate", response_model=LandRecordOut)
def revalidate_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_verifier)):
    record = db.get(LandRecord, record_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record not found")
    fields = json.loads(record.fields_json)
    record.validation_issues_json = json.dumps(pipeline_service.validate_fields(fields))
    record_service.refresh_duplicates_and_conflicts(db, record)
    db.commit()
    db.refresh(record)
    return _detail(record)


@router.post("/{record_id}/verify", response_model=LandRecordOut)
def verify_record(record_id: int, payload: RecordVerifyRequest, db: Session = Depends(get_db), current_user: User = Depends(require_verifier)):
    record = db.get(LandRecord, record_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record not found")
    if record.status == "verified":
        raise HTTPException(status.HTTP_409_CONFLICT, "Already verified")

    issues = json.loads(record.validation_issues_json or "[]")
    fields = json.loads(record.fields_json or "{}")
    still_needs_review = [name for name, f in fields.items() if f.get("needs_human_review")]
    if issues or still_needs_review:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Cannot verify: {len(issues)} validation issue(s), {len(still_needs_review)} field(s) still need review.",
        )

    record = record_service.verify_record(db, record, current_user, notes=payload.notes)
    return _detail(record)


@router.post("/{record_id}/reject", response_model=LandRecordOut)
def reject_record(record_id: int, payload: RecordRejectRequest, db: Session = Depends(get_db), current_user: User = Depends(require_verifier)):
    record = db.get(LandRecord, record_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record not found")
    record = record_service.reject_record(db, record, current_user, payload.reason)
    return _detail(record)
