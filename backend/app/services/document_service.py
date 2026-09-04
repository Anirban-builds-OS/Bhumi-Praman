import json
import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.models.document import Document, DocumentPage, Extraction
from app.models.user import User
from app.services import pipeline_service, record_service
from app.services.audit_service import log_action

ALLOWED_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
}


def save_upload(db: Session, file: UploadFile, actor: User, batch_label: str | None = None) -> Document:
    suffix = ALLOWED_CONTENT_TYPES.get(file.content_type)
    if suffix is None:
        raise ValueError(f"Unsupported file type: {file.content_type}. Allowed: PDF, JPG, PNG.")

    uploads_dir = Path(settings.STORAGE_PATH) / "uploads"
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    stored_path = uploads_dir / stored_name

    with stored_path.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    size_bytes = stored_path.stat().st_size

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        stored_path.unlink(missing_ok=True)
        raise ValueError(f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit.")

    document = Document(
        original_filename=file.filename or stored_name,
        stored_path=str(stored_path),
        content_type=file.content_type,
        file_size_bytes=size_bytes,
        status="uploaded",
        batch_label=batch_label,
        uploaded_by_id=actor.id if actor else None,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    _materialize_pages(db, document)

    log_action(db, actor, "document.uploaded", "document", document.id, notes=document.original_filename)
    return document


def _materialize_pages(db: Session, document: Document) -> None:
    """Splits the upload into one or more page images. A PDF becomes N
    pages (one image each); a JPG/PNG is already a single page."""
    processed_dir = Path(settings.STORAGE_PATH) / "processed"
    if document.content_type == "application/pdf":
        base_name = Path(document.stored_path).stem
        page_paths = pipeline_service.pdf_to_page_images(document.stored_path, processed_dir, base_name)
    else:
        page_paths = [Path(document.stored_path)]

    for i, path in enumerate(page_paths, start=1):
        db.add(DocumentPage(document_id=document.id, page_number=i, image_path=str(path), status="pending"))
    document.page_count = len(page_paths)
    db.commit()


def process_document(db: Session, document: Document, actor: User) -> Document:
    document.status = "processing"
    db.commit()

    try:
        for page in document.pages:
            _process_page(db, page, actor)
        document.status = "processed"
        document.error_message = None
    except Exception as exc:  # noqa: BLE001 -- surfaced as a controlled error, never a raw stack trace to the client
        document.status = "failed"
        document.error_message = str(exc)
        log_action(db, actor, "document.processing_failed", "document", document.id, notes=str(exc))
    db.commit()
    db.refresh(document)
    return document


def _process_page(db: Session, page: DocumentPage, actor: User) -> None:
    from app.config import settings as cfg

    page.status = "processing"
    db.commit()

    result = pipeline_service.process_page_image(page.image_path, languages=cfg.ocr_languages_list)

    page.image_width = result["image_width"]
    page.image_height = result["image_height"]
    page.status = "processed"

    extraction = Extraction(
        document_page_id=page.id,
        ocr_full_text=result["ocr_full_text"],
        ocr_mean_word_confidence=result["ocr_mean_word_confidence"],
        deskew_angle_deg=result["deskew_angle_deg"],
        ocr_words_json=json.dumps(result["ocr_words"]),
        fields_json=json.dumps(result["fields"]),
        field_locations_json=json.dumps({k: v.get("location") for k, v in result["fields"].items()}),
        validation_issues_json=json.dumps(result["validation_issues"]),
        record_confidence=result["record_confidence"],
        auto_approvable=result["auto_approvable"],
    )
    db.add(extraction)
    db.commit()
    db.refresh(extraction)

    record_service.create_from_extraction(db, page, extraction, actor)
    log_action(db, actor, "document.page_processed", "document_page", page.id,
               notes=f"record_confidence={result['record_confidence']}")
