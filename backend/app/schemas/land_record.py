from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.document import FieldState


class LandRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    record_code: str
    document_page_id: int | None = None
    document_id: int | None = None
    extraction_id: int | None = None
    status: str
    page_image_width: int | None = None
    page_image_height: int | None = None

    owner_name: str | None = None
    father_name: str | None = None
    survey_number: str | None = None
    khasra_number: str | None = None
    khata_number: str | None = None
    plot_area: str | None = None
    village: str | None = None
    tehsil: str | None = None
    district: str | None = None
    land_classification: str | None = None
    mutation_number: str | None = None
    registration_number: str | None = None

    latitude: float | None = None
    longitude: float | None = None

    fields: dict[str, FieldState]
    validation_issues: list[str]
    duplicate_of: list[str]
    conflicts: list[dict]
    record_confidence: float
    verification_hash: str | None = None
    rejection_reason: str | None = None

    created_by_id: int | None = None
    verified_by_id: int | None = None
    verified_by_name: str | None = None
    verified_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class LandRecordSummary(BaseModel):
    """Lighter shape for list/search views."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    record_code: str
    status: str
    owner_name: str | None = None
    survey_number: str | None = None
    khasra_number: str | None = None
    khata_number: str | None = None
    village: str | None = None
    tehsil: str | None = None
    district: str | None = None
    record_confidence: float
    has_validation_issues: bool
    has_duplicates: bool
    has_conflicts: bool
    updated_at: datetime


class FieldEditRequest(BaseModel):
    field: str
    value: str | None
    action: str = "edit"  # edit|accept|reject


class RecordVerifyRequest(BaseModel):
    notes: str | None = None


class RecordRejectRequest(BaseModel):
    reason: str


class RecordSearchParams(BaseModel):
    query: str | None = None
    status: str | None = None
    district: str | None = None
    tehsil: str | None = None
    village: str | None = None
    needs_review_only: bool = False
    page: int = 1
    page_size: int = 20


class PaginatedRecords(BaseModel):
    items: list[LandRecordSummary]
    total: int
    page: int
    page_size: int
