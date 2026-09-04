from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OcrWord(BaseModel):
    text: str
    conf: float
    left: int
    top: int
    width: int
    height: int
    line_num: int
    block_num: int


class FieldLocation(BaseModel):
    left: int
    top: int
    width: int
    height: int
    match_score: float


class FieldState(BaseModel):
    """One extracted field's full state -- matches the shape stored in
    LandRecord.fields_json and Extraction.fields_json."""
    value: str | None = None
    pattern_confidence: float = 0.0
    ocr_confidence: float = 0.0
    confidence: float = 0.0
    confidence_bucket: str = "missing"  # high|medium|low|missing
    needs_human_review: bool = True
    source: str = "ai"  # ai|officer
    field_verified: bool = False
    location: FieldLocation | None = None


class DocumentPageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    page_number: int
    image_path: str
    image_width: int | None = None
    image_height: int | None = None
    status: str
    error_message: str | None = None


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    content_type: str
    file_size_bytes: int
    page_count: int
    status: str
    error_message: str | None = None
    batch_label: str | None = None
    uploaded_at: datetime
    pages: list[DocumentPageOut] = []


class ExtractionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_page_id: int
    ocr_full_text: str
    ocr_mean_word_confidence: float
    deskew_angle_deg: float
    record_confidence: float
    auto_approvable: bool
    fields: dict[str, FieldState]
    ocr_words: list[OcrWord]
    validation_issues: list[str]
    created_at: datetime


class ProcessDocumentResponse(BaseModel):
    document: DocumentOut
    extractions: list[ExtractionOut]
    land_record_ids: list[int]
