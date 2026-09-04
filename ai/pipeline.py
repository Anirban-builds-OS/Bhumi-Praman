"""
pipeline.py
------------
Orchestrates the full Crystal extraction pipeline for a single document:

    scanned image
        -> preprocessing (deskew / denoise / binarize)
        -> OCR (multilingual, word-level confidence)
        -> field extraction (rule-based classification into RoR fields)
        -> confidence scoring (multi-signal, per field)
        -> business-rule validation

Run directly on one file for a quick manual check:
    python3 pipeline.py sample_data/DOC001.png
"""
import json
import sys
import cv2

import preprocessing
import ocr_engine
import field_extractor
import confidence_scorer
import validator


def process_document(image_path: str, languages: list[str] | None = None) -> dict:
    languages = languages or ["en"]

    pre = preprocessing.preprocess(image_path)
    ocr_result = ocr_engine.run_ocr(pre, languages=languages)
    raw_fields = field_extractor.extract_fields(ocr_result["full_text"])
    scored_fields = confidence_scorer.score_fields(raw_fields, ocr_result)
    issues = validator.validate_record(scored_fields)

    fields_needing_review = [f for f, v in scored_fields.items() if v["needs_human_review"]]
    record_confidence = (
        round(sum(v["confidence"] for v in scored_fields.values()) / len(scored_fields), 3)
        if scored_fields
        else 0.0
    )

    return {
        "image_path": image_path,
        "deskew_angle_deg": pre["deskew_angle_deg"],
        "ocr_mean_word_confidence": ocr_result["mean_word_confidence"],
        "fields": scored_fields,
        "validation_issues": issues,
        "fields_needing_human_review": fields_needing_review,
        "record_confidence": record_confidence,
        "auto_approvable": record_confidence >= confidence_scorer.HIGH_THRESHOLD and not issues,
    }


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_data/DOC001.png"
    result = process_document(path)
    print(json.dumps(result, indent=2))
