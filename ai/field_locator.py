"""
field_locator.py
------------------
NEW module (not part of the original Crystal prototype) that closes a real
gap identified during integration: ocr_engine.run_ocr() already returns
word-level bounding boxes, but field_extractor.py discards word position
when it matches against the joined full_text string, so extracted field
values had no link back to *where* they came from on the page.

This module re-establishes that link after the fact: given an extracted
field's value and the OCR engine's word list, it searches for the
contiguous run of OCR words whose text best matches the value and returns
the bounding box enclosing that run. This is what backs real "source
highlighting" in the verification workspace (click a field, see the
matching region on the document) -- as opposed to a fabricated/decorative
box, every highlight returned here is a genuine re-match against the
words Tesseract actually detected, and a field simply gets no highlight
if no confident match is found rather than guessing.
"""
import re


def _normalize_token(token: str) -> str:
    return re.sub(r"[^\w]", "", token).lower()


def locate_value(value: str | None, ocr_words: list[dict]) -> dict | None:
    """Returns {"left","top","width","height","match_score"} in the same
    pixel space as the OCR words (i.e. the preprocessed image), or None if
    no sufficiently confident contiguous match is found.
    """
    if not value or not ocr_words:
        return None

    value_tokens = [_normalize_token(t) for t in value.split() if _normalize_token(t)]
    if not value_tokens:
        return None

    # Reading order: top-to-bottom blocks/lines, left-to-right within a line
    # -- matches how ocr_engine.py reconstructs line_texts, so window search
    # below walks the words in the same order the field text was built from.
    ordered = sorted(ocr_words, key=lambda w: (w["block_num"], w["line_num"], w["left"]))
    n = len(value_tokens)

    best = None
    for window_len in (n, n + 1, max(n - 1, 1)):
        if window_len <= 0 or window_len > len(ordered):
            continue
        for start in range(0, len(ordered) - window_len + 1):
            window = ordered[start:start + window_len]
            window_tokens = [_normalize_token(w["text"]) for w in window]
            matches = sum(1 for t in window_tokens if t in value_tokens)
            score = matches / max(len(value_tokens), len(window_tokens))
            if best is None or score > best[0]:
                best = (score, window)

    if best is None or best[0] < 0.5:
        return None

    score, window = best
    left = min(w["left"] for w in window)
    top = min(w["top"] for w in window)
    right = max(w["left"] + w["width"] for w in window)
    bottom = max(w["top"] + w["height"] for w in window)
    return {
        "left": left,
        "top": top,
        "width": right - left,
        "height": bottom - top,
        "match_score": round(score, 3),
    }


def locate_fields(scored_fields: dict, ocr_words: list[dict]) -> dict:
    """Runs locate_value for every field in a pipeline.process_document()
    result's 'fields' dict. Returns {field_name: bbox_dict_or_None}."""
    return {
        field: locate_value(info.get("value"), ocr_words)
        for field, info in scored_fields.items()
    }
