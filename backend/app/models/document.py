from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Document(Base):
    """The uploaded file as the user sent it (PDF or image). A PDF may
    contain several pages; each becomes one DocumentPage."""
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(512))
    content_type: Mapped[str] = mapped_column(String(128))
    file_size_bytes: Mapped[int] = mapped_column(Integer)
    page_count: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default="uploaded")  # uploaded|processing|processed|failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    batch_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    uploaded_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    pages: Mapped[list["DocumentPage"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    uploaded_by: Mapped["User"] = relationship()  # noqa: F821


class DocumentPage(Base):
    """One image the AI pipeline actually runs on -- a single-image upload
    produces exactly one of these; a multi-page PDF is rasterised into one
    per page (see backend/app/services/document_service.py)."""
    __tablename__ = "document_pages"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    page_number: Mapped[int] = mapped_column(Integer, default=1)
    image_path: Mapped[str] = mapped_column(String(512))
    image_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending|processing|processed|failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    document: Mapped["Document"] = relationship(back_populates="pages")
    extractions: Mapped[list["Extraction"]] = relationship(back_populates="document_page", cascade="all, delete-orphan")


class Extraction(Base):
    """Immutable snapshot of what the AI pipeline produced for one page at
    one point in time. A page can be re-processed (creating a new row here)
    without losing the original AI output for audit purposes."""
    __tablename__ = "extractions"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_page_id: Mapped[int] = mapped_column(ForeignKey("document_pages.id"))
    ocr_full_text: Mapped[str] = mapped_column(Text, default="")
    ocr_mean_word_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    deskew_angle_deg: Mapped[float] = mapped_column(Float, default=0.0)
    ocr_words_json: Mapped[str] = mapped_column(Text, default="[]")
    fields_json: Mapped[str] = mapped_column(Text, default="{}")
    field_locations_json: Mapped[str] = mapped_column(Text, default="{}")
    validation_issues_json: Mapped[str] = mapped_column(Text, default="[]")
    record_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    auto_approvable: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    document_page: Mapped["DocumentPage"] = relationship(back_populates="extractions")
