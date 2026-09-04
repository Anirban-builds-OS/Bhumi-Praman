from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.auth import get_current_user, require_verifier
from app.models.document import Document, DocumentPage
from app.models.land_record import LandRecord
from app.models.user import User
from app.schemas.document import DocumentOut, ProcessDocumentResponse, ExtractionOut
from app.services import document_service
from app.services.audit_service import log_action

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_verifier),
):
    try:
        document = document_service.save_upload(db, file, current_user)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    return document


@router.get("", response_model=list[DocumentOut])
def list_documents(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Document).order_by(Document.uploaded_at.desc())
    if status_filter:
        q = q.filter(Document.status == status_filter)
    return q.limit(200).all()


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return document


@router.post("/{document_id}/process", response_model=ProcessDocumentResponse)
def process_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_verifier)):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    if document.status == "processing":
        raise HTTPException(status.HTTP_409_CONFLICT, "Document is already being processed")

    document = document_service.process_document(db, document, current_user)
    if document.status == "failed":
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Processing failed: {document.error_message}")

    extractions = []
    record_ids = []
    for page in document.pages:
        if page.extractions:
            latest = page.extractions[-1]
            extractions.append(_extraction_out(latest))
            record = db.query(LandRecord).filter(LandRecord.extraction_id == latest.id).first()
            if record:
                record_ids.append(record.id)

    return ProcessDocumentResponse(document=document, extractions=extractions, land_record_ids=record_ids)


@router.get("/{document_id}/pages/{page_id}/image")
def get_page_image(document_id: int, page_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    page = db.get(DocumentPage, page_id)
    if page is None or page.document_id != document_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Page not found")
    return FileResponse(page.image_path)


def _extraction_out(extraction) -> ExtractionOut:
    import json
    fields = json.loads(extraction.fields_json)
    return ExtractionOut(
        id=extraction.id,
        document_page_id=extraction.document_page_id,
        ocr_full_text=extraction.ocr_full_text,
        ocr_mean_word_confidence=extraction.ocr_mean_word_confidence,
        deskew_angle_deg=extraction.deskew_angle_deg,
        record_confidence=extraction.record_confidence,
        auto_approvable=extraction.auto_approvable,
        fields=fields,
        ocr_words=json.loads(extraction.ocr_words_json),
        validation_issues=json.loads(extraction.validation_issues_json),
        created_at=extraction.created_at,
    )
