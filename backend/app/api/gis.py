from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.auth import get_current_user
from app.models.land_record import LandRecord
from app.models.user import User
from app.schemas.audit import GisRecord

router = APIRouter(prefix="/api/gis", tags=["gis"])


@router.get("/records", response_model=list[GisRecord])
def gis_records(
    district: str | None = None,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(LandRecord).filter(LandRecord.latitude.isnot(None), LandRecord.longitude.isnot(None))
    if district:
        q = q.filter(LandRecord.district.ilike(f"%{district}%"))
    if status_filter:
        q = q.filter(LandRecord.status == status_filter)

    return [
        GisRecord(
            id=r.id, record_code=r.record_code, status=r.status, owner_name=r.owner_name,
            khasra_number=r.khasra_number, survey_number=r.survey_number, village=r.village,
            tehsil=r.tehsil, district=r.district, plot_area=r.plot_area,
            latitude=r.latitude, longitude=r.longitude,
        )
        for r in q.limit(500).all()
    ]
