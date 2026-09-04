from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base

FIELD_NAMES = [
    "owner_name", "father_name", "survey_number", "khasra_number", "khata_number",
    "plot_area", "village", "tehsil", "district", "land_classification",
    "mutation_number", "registration_number",
]


class LandRecord(Base):
    """The structured, current-state record an officer verifies against.
    Flat columns below are denormalised copies of fields_json (kept in sync
    on every edit) purely so search/filter/sort/GIS/reports can use plain
    SQL instead of parsing JSON on every request. fields_json is the
    authoritative per-field state (value + confidence + who last touched
    it) that the verification workspace reads and writes."""
    __tablename__ = "land_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    record_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    document_page_id: Mapped[int | None] = mapped_column(ForeignKey("document_pages.id"), nullable=True)
    extraction_id: Mapped[int | None] = mapped_column(ForeignKey("extractions.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending_review", index=True)  # pending_review|verified|rejected

    owner_name: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    father_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    survey_number: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    khasra_number: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    khata_number: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    plot_area: Mapped[str | None] = mapped_column(String(64), nullable=True)
    village: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    tehsil: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    district: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    land_classification: Mapped[str | None] = mapped_column(String(128), nullable=True)
    mutation_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    registration_number: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Prototype-labelled demo coordinates for the GIS explorer (section 28 of
    # the spec is explicit: never fabricate real cadastral boundaries -- see
    # backend/app/services/gis_service.py for how these get assigned).
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    fields_json: Mapped[str] = mapped_column(Text, default="{}")
    validation_issues_json: Mapped[str] = mapped_column(Text, default="[]")
    duplicate_of_json: Mapped[str] = mapped_column(Text, default="[]")
    conflicts_json: Mapped[str] = mapped_column(Text, default="[]")
    record_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    verification_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    verified_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    document_page: Mapped["DocumentPage"] = relationship()  # noqa: F821
    extraction: Mapped["Extraction"] = relationship()  # noqa: F821
    created_by: Mapped["User"] = relationship(foreign_keys=[created_by_id])  # noqa: F821
    verified_by: Mapped["User"] = relationship(foreign_keys=[verified_by_id])  # noqa: F821
