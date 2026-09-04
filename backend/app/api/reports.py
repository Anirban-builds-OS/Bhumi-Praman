from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.auth import require_verifier
from app.models.land_record import LandRecord
from app.models.user import User
from app.services import report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/{record_id}")
def generate_report(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_verifier)):
    record = db.get(LandRecord, record_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record not found")

    report = report_service.generate_record_pdf(db, record, current_user)
    return FileResponse(report.file_path, media_type="application/pdf", filename=f"{record.record_code}.pdf")
