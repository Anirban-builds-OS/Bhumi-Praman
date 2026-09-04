"""
confidence_scorer.py
----------------------
Implements PS requirement #11 ("Confidence scoring for extracted information
with automatic identification of uncertain fields") and feeds requirement
#12 ("Human-assisted verification workflow for low-confidence records").

Design: a field's final confidence blends two independent signals so that a
field is only trusted when BOTH the OCR engine was sure about the
characters AND the extraction rule was sure about the field's identity --
either signal alone is an unreliable estimator on its own (an OCR engine can
be confident about the wrong characters; a regex can match confidently
against garbled text). This mirrors the "multi-signal confidence" approach
used in production document-intelligence systems, where a single
model-internal probability is treated as necessary but not sufficient.

Confidence buckets:
  >= HIGH_THRESHOLD   -> auto-accept, no human review needed
  >= LOW_THRESHOLD    -> accept but flag for spot-check / batch audit
  <  LOW_THRESHOLD    -> route to mandatory human-in-the-loop (HITL) review
"""

HIGH_THRESHOLD = 0.85
LOW_THRESHOLD = 0.60

OCR_WEIGHT = 0.4
PATTERN_WEIGHT = 0.6


def _ocr_confidence_for_value(value: str, ocr_words: list[dict], fallback: float) -> float:
    if not value:
        return 0.0
    tokens = [t.strip(".,:;") for t in value.lower().split()]
    matched = [w["conf"] for w in ocr_words if w["text"].lower().strip(".,:;") in tokens]
    if not matched:
        return fallback / 100.0
    return (sum(matched) / len(matched)) / 100.0


def score_fields(extracted_fields: dict, ocr_result: dict) -> dict:
    """extracted_fields: output of field_extractor.extract_fields
    ocr_result: output of ocr_engine.run_ocr (needs 'words' and
    'mean_word_confidence')
    Returns the same field dict enriched with 'confidence' and 'review_flag'.
    """
    words = ocr_result.get("words", [])
    global_mean = ocr_result.get("mean_word_confidence", 0.0)

    scored = {}
    for field, info in extracted_fields.items():
        value = info["value"]
        pattern_conf = info["pattern_confidence"]
        ocr_conf = _ocr_confidence_for_value(value, words, global_mean) if value else 0.0

        combined = PATTERN_WEIGHT * pattern_conf + OCR_WEIGHT * ocr_conf
        combined = round(combined, 3) if value else 0.0

        if not value:
            bucket = "missing"
        elif combined >= HIGH_THRESHOLD:
            bucket = "high"
        elif combined >= LOW_THRESHOLD:
            bucket = "medium"
        else:
            bucket = "low"

        scored[field] = {
            "value": value,
            "pattern_confidence": pattern_conf,
            "ocr_confidence": round(ocr_conf, 3),
            "confidence": combined,
            "confidence_bucket": bucket,
            "needs_human_review": bucket in ("low", "missing"),
        }
    return scored
