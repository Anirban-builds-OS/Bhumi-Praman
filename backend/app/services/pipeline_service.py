"""
pipeline_service.py
---------------------
The "Prototype Adapter" the spec calls for in section 39: the only place in
the backend that imports the ai/ modules directly. Every API route calls
through here, never into ai/ directly, so the AI engine can be swapped
(e.g. Tesseract -> a hosted PaddleOCR-VL/TrOCR endpoint per ai/ocr_engine.py's
own docstring) by editing this one file and ai/ocr_engine.py.
"""
import json
import sys
from pathlib import Path

import pymupdf as fitz  # PyMuPDF (import name still 'fitz' for API compatibility)

REPO_ROOT = Path(__file__).resolve().parents[3]
AI_DIR = REPO_ROOT / "ai"
if str(AI_DIR) not in sys.path:
    sys.path.insert(0, str(AI_DIR))

import confidence_scorer  # noqa: E402
import field_locator  # noqa: E402
import ocr_engine  # noqa: E402
import preprocessing  # noqa: E402
import validator  # noqa: E402
from field_extractor import FIELD_PATTERNS  # noqa: E402

FIELD_NAMES = list(FIELD_PATTERNS.keys())


def pdf_to_page_images(pdf_path: str, out_dir: Path, base_name: str) -> list[Path]:
    """Rasterises every page of a PDF to a PNG at ~200 DPI (matches the
    spec's 'Min. 200 DPI resolution' upload requirement) so the existing
    image-based pipeline can run unchanged on each page."""
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    paths = []
    zoom = 200 / 72  # PDF points are 72/inch
    matrix = fitz.Matrix(zoom, zoom)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=matrix)
        out_path = out_dir / f"{base_name}_p{i + 1}.png"
        pix.save(str(out_path))
        paths.append(out_path)
    doc.close()
    return paths


def process_page_image(image_path: str, languages: list[str] | None = None) -> dict:
    """Runs the real Crystal pipeline on one page image and returns a dict
    shaped for the Extraction/LandRecord models -- fields enriched with
    source-highlighting boxes via field_locator (new, see ai/field_locator.py),
    everything else exactly what pipeline.process_document() itself computed
    (nothing here recomputes or overrides the AI's own numbers)."""
    languages = languages or ["en"]

    pre = preprocessing.preprocess(image_path)
    # ocr_result = ocr_engine.run_ocr(pre["final"], languages=languages)
    ocr_result = ocr_engine.run_ocr(pre, languages=languages)
    raw_fields = _extract_fields(ocr_result["full_text"])
    scored_fields = confidence_scorer.score_fields(raw_fields, ocr_result)
    issues = validator.validate_record(scored_fields)
    locations = field_locator.locate_fields(scored_fields, ocr_result["words"])

    fields_out = {}
    for name, info in scored_fields.items():
        fields_out[name] = {
            **info,
            "source": "ai",
            "field_verified": False,
            "location": locations.get(name),
        }

    record_confidence = (
        round(sum(v["confidence"] for v in scored_fields.values()) / len(scored_fields), 3)
        if scored_fields else 0.0
    )
    auto_approvable = record_confidence >= confidence_scorer.HIGH_THRESHOLD and not issues

    return {
        "ocr_full_text": ocr_result["full_text"],
        "ocr_mean_word_confidence": ocr_result["mean_word_confidence"],
        "deskew_angle_deg": pre["deskew_angle_deg"],
        "ocr_words": ocr_result["words"],
        "fields": fields_out,
        "validation_issues": issues,
        "record_confidence": record_confidence,
        "auto_approvable": auto_approvable,
        "image_width": int(pre["shape"][1]),
        "image_height": int(pre["shape"][0]),
    }


def _extract_fields(ocr_text: str) -> dict:
    import field_extractor
    return field_extractor.extract_fields(ocr_text)


def validate_fields(fields: dict) -> list[str]:
    return validator.validate_record(fields)


def compute_batch_duplicates_and_conflicts(all_records: dict[str, dict]) -> tuple[dict[str, list], dict[str, list]]:
    """Wraps validator.find_duplicates / find_conflicts (the latter added
    during this integration -- see ai/validator.py) across a whole batch at
    once. Returns the full {record_code: [...]} dicts for every record, not
    just one -- duplicate/conflict status is a property of the batch (did a
    *new* record just collide with an *older* one?), so a single-record
    view would go stale the moment a colliding record appears later.
    record_service.refresh_duplicates_and_conflicts applies this across
    every affected row, not just the one being edited."""
    return validator.find_duplicates(all_records), validator.find_conflicts(all_records)


def rerun_full_evaluation() -> dict:
    """Shells out to the real ai/evaluate.py logic (imported, not
    subprocessed) so any 'measured accuracy' the UI shows is always freshly
    computed from the actual sample set and ground truth -- never a
    hard-coded number. See spec section 53."""
    import os
    import evaluate as evaluate_module
    import importlib

    os.environ["CRYSTAL_SAMPLE_DIR"] = str(REPO_ROOT / "data" / "sample_documents")
    os.environ["CRYSTAL_GROUND_TRUTH_PATH"] = str(REPO_ROOT / "data" / "ground_truth" / "ground_truth.json")
    importlib.reload(evaluate_module)  # picks up the env vars set above
    evaluate_module.main()
    report_path = AI_DIR / "output" / "evaluation_report.json"
    with open(report_path) as f:
        return json.load(f)
