import json

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.auth import get_current_user, require_administrator
from app.models.audit import AuditLog
from app.models.document import Document, DocumentPage
from app.models.land_record import LandRecord
from app.models.user import User
from app.schemas.audit import AuditLogOut, DashboardStats, EvaluationReport
from app.services import pipeline_service

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/dashboard/statistics", response_model=DashboardStats)
def dashboard_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_documents = db.query(func.count(Document.id)).scalar() or 0
    total_pages_processed = db.query(func.count(DocumentPage.id)).filter(DocumentPage.status == "processed").scalar() or 0

    total_records = db.query(func.count(LandRecord.id)).scalar() or 0
    verified = db.query(func.count(LandRecord.id)).filter(LandRecord.status == "verified").scalar() or 0
    pending = db.query(func.count(LandRecord.id)).filter(LandRecord.status == "pending_review").scalar() or 0
    rejected = db.query(func.count(LandRecord.id)).filter(LandRecord.status == "rejected").scalar() or 0
    low_conf = db.query(func.count(LandRecord.id)).filter(LandRecord.record_confidence < 0.60, LandRecord.status != "rejected").scalar() or 0

    all_active = db.query(LandRecord).filter(LandRecord.status != "rejected").all()
    conflict_count = sum(1 for r in all_active if json.loads(r.conflicts_json or "[]"))
    duplicate_count = sum(1 for r in all_active if json.loads(r.duplicate_of_json or "[]"))

    pipeline_flow = {
        "uploaded": total_documents,
        "ai_parsed": total_pages_processed,
        "reviewing": pending,
        "verified": verified,
        "rejected": rejected,
    }

    district_rows = (
        db.query(LandRecord.district, func.count(LandRecord.id))
        .filter(LandRecord.district.isnot(None))
        .group_by(LandRecord.district)
        .all()
    )
    district_coverage = []
    for district, total in district_rows:
        verified_in_district = (
            db.query(func.count(LandRecord.id))
            .filter(LandRecord.district == district, LandRecord.status == "verified")
            .scalar() or 0
        )
        pct = round((verified_in_district / total) * 100, 1) if total else 0.0
        district_coverage.append({"district": district, "total": total, "verified": verified_in_district, "pct": pct})

    recent = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(15).all()

    return DashboardStats(
        total_documents=total_documents,
        total_pages_processed=total_pages_processed,
        total_records=total_records,
        verified_records=verified,
        pending_review_records=pending,
        rejected_records=rejected,
        low_confidence_records=low_conf,
        validation_conflicts=conflict_count,
        duplicate_flags=duplicate_count,
        pipeline_flow=pipeline_flow,
        district_coverage=district_coverage,
        recent_activity=[AuditLogOut.model_validate(a) for a in recent],
    )


@router.post("/evaluation/run", response_model=EvaluationReport)
def run_evaluation(admin: User = Depends(require_administrator)):
    """Reruns the real ai/evaluate.py against the sample set and ground
    truth and returns whatever it actually measures -- see spec section 53,
    this is never a hard-coded figure."""
    report = pipeline_service.rerun_full_evaluation()
    return EvaluationReport(**report)
