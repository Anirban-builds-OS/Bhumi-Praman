from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_name_snapshot: str
    action: str
    entity_type: str
    entity_id: int | None = None
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    notes: str | None = None
    created_at: datetime


class DashboardStats(BaseModel):
    total_documents: int
    total_pages_processed: int
    total_records: int
    verified_records: int
    pending_review_records: int
    rejected_records: int
    low_confidence_records: int
    validation_conflicts: int
    duplicate_flags: int
    pipeline_flow: dict[str, int]  # uploaded / ai_parsed / reviewing / verified / rejected
    district_coverage: list[dict]  # [{district, total, verified, pct}]
    recent_activity: list[AuditLogOut]


class GisRecord(BaseModel):
    id: int
    record_code: str
    status: str
    owner_name: str | None = None
    khasra_number: str | None = None
    survey_number: str | None = None
    village: str | None = None
    tehsil: str | None = None
    district: str | None = None
    plot_area: str | None = None
    latitude: float
    longitude: float


class EvaluationReport(BaseModel):
    """Mirrors ai/evaluate.py's real output exactly -- never a fabricated
    number, see spec section 53."""
    documents_evaluated: int
    mean_cer: float
    macro_average_f1: float
    field_metrics: dict[str, dict]
    confidence_calibration: dict[str, dict]
    per_document: list[dict]
