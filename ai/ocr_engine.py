"""
ocr_engine.py
--------------
Thin OCR abstraction so the rest of the pipeline never talks to a specific
engine directly. Swapping the engine (e.g. to a hosted PaddleOCR-VL / TrOCR /
Donut endpoint for handwriting) means editing only this file.

The prototype ships a Tesseract-based implementation because it runs fully
offline with no model download, and Tesseract's Hindi + Assamese trained data
is installed, giving genuine multilingual OCR for printed text out of the
box. Tesseract still returns per-word confidence, which the confidence
scorer downstream needs regardless of which engine ultimately backs this
function in production.

PRODUCTION NOTE: for the handwritten and highly degraded registers that
Problem Statement 26018 centres on, Tesseract is not the recommended
production engine -- see the "Tech Stack" and "Existing Solutions" sections
of the accompanying report for why TrOCR / PaddleOCR-VL / a fine-tuned
Donut model is the recommended production path, and why it isn't wired in
here (those require model downloads this sandbox cannot reach).
"""
# import os
# import pytesseract
# from pytesseract import Output
# import numpy as np

# # PORTABILITY FIX (was hard-coded to a Windows-only path, which broke this
# # module on Linux/macOS/deployment): only override pytesseract's binary
# # location if TESSERACT_CMD is explicitly set. Otherwise pytesseract falls
# # back to whatever `tesseract` resolves to on PATH, which is the correct
# # behaviour on Linux/macOS and on any Windows machine where the installer
# # added Tesseract to PATH. See backend/.env.example for the Windows default
# # path to set TESSERACT_CMD to if it is not on PATH.
# _tesseract_cmd = os.environ.get("TESSERACT_CMD")
# if _tesseract_cmd:
#     pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd


# LANG_MAP = {
#     "en": "eng",
#     "hi": "hin",
#     "as": "asm",
# }


# def run_ocr(image: np.ndarray, languages: list[str] | None = None) -> dict:
#     """Runs OCR on a preprocessed (binarized) image array.

#     Returns full text plus a list of word-level detections, each carrying a
#     confidence score in [0, 100], which downstream confidence scoring
#     combines with pattern-match strength.
#     """
#     languages = languages or ["en"]
#     tess_langs = "+".join(LANG_MAP.get(lang, "eng") for lang in languages)

#     config = "--oem 3 --psm 6"  # assume a single uniform block of text
#     data = pytesseract.image_to_data(
#         image, lang=tess_langs, config=config, output_type=Output.DICT
#     )

#     words = []
#     for i, text in enumerate(data["text"]):
#         text = text.strip()
#         if not text:
#             continue
#         conf = float(data["conf"][i])
#         if conf < 0:  # tesseract uses -1 for non-text regions
#             continue
#         words.append(
#             {
#                 "text": text,
#                 "conf": conf,
#                 "left": data["left"][i],
#                 "top": data["top"][i],
#                 "width": data["width"][i],
#                 "height": data["height"][i],
#                 "line_num": data["line_num"][i],
#                 "block_num": data["block_num"][i],
#             }
#         )

#     # Reconstruct line-grouped text (preserves layout better than the raw
#     # top-to-bottom word stream for downstream regex extraction)
#     lines = {}
#     for w in words:
#         key = (w["block_num"], w["line_num"])
#         lines.setdefault(key, []).append(w)

#     line_texts = []
#     for key in sorted(lines.keys()):
#         line_words = sorted(lines[key], key=lambda w: w["left"])
#         line_texts.append(" ".join(w["text"] for w in line_words))

#     full_text = "\n".join(line_texts)
#     mean_conf = float(np.mean([w["conf"] for w in words])) if words else 0.0

#     return {
#         "full_text": full_text,
#         "words": words,
#         "mean_word_confidence": round(mean_conf, 2),
#     }

import os
import subprocess
import pytesseract
from pytesseract import Output
import numpy as np



_tesseract_cmd = os.environ.get("TESSERACT_CMD")

if _tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd


LANG_MAP = {
    # "en": "eng",
    # "hi": "hin",
    # "as": "asm",
    # "ben": "ben",

    "en": "eng",
    "hi": "hin",
    "as": "asm",
    "bn": "ben",
    "gu": "guj",
    "mr": "mar",
    "kn": "kan",
    "ml": "mal",
    "or": "ori",
    "pa": "pan",
    "ta": "tam",
    "te": "tel",
    
}

def get_installed_languages():
    """Return Tesseract language packs installed on this machine."""
    try:
        result = subprocess.run(
            ["tesseract", "--list-langs"],
            capture_output=True,
            text=True,
            check=True,
        )

        languages = set()

        for line in result.stdout.splitlines():
            line = line.strip()

            if line and not line.lower().startswith("list of available"):
                languages.add(line)

        return languages

    except Exception:
        return {"eng"}


def resolve_language(language: str) -> str:
    """
    Resolve an application language code to a Tesseract language code.

    If 'auto' is requested, use all supported language packs that are
    actually installed on the current machine.
    """
    installed = get_installed_languages()

    if language == "auto":
        preferred = [
            "eng",
            "hin",
            "asm",
            "ben",
            "guj",
            "mar",
            "kan",
            "mal",
            "ori",
            "pan",
            "tam",
            "tel",
        ]

        available = [
            lang
            for lang in preferred
            if lang in installed
        ]

        return "+".join(available) if available else "eng"

    requested = LANG_MAP.get(language, language)

    if requested in installed:
        return requested

    return "eng"

def detect_script(text: str) -> str:
    """
    Detect the dominant script in OCR text.

    Returns an application language code.
    """
    counts = {
        "hi": 0,   # Devanagari
        "bn": 0,   # Bengali
        "as": 0,   # Assamese (shares Bengali script)
        "gu": 0,   # Gujarati
        "pa": 0,   # Gurmukhi
        "ta": 0,   # Tamil
        "te": 0,   # Telugu
        "kn": 0,   # Kannada
        "ml": 0,   # Malayalam
        "or": 0,   # Odia
        "ur": 0,   # Urdu/Arabic
        "en": 0,
    }

    for char in text:
        code = ord(char)

        # Devanagari
        if 0x0900 <= code <= 0x097F:
            counts["hi"] += 1

        # Bengali / Assamese
        elif 0x0980 <= code <= 0x09FF:
            counts["bn"] += 1

        # Gujarati
        elif 0x0A80 <= code <= 0x0AFF:
            counts["gu"] += 1

        # Gurmukhi
        elif 0x0A00 <= code <= 0x0A7F:
            counts["pa"] += 1

        # Odia
        elif 0x0B00 <= code <= 0x0B7F:
            counts["or"] += 1

        # Tamil
        elif 0x0B80 <= code <= 0x0BFF:
            counts["ta"] += 1

        # Telugu
        elif 0x0C00 <= code <= 0x0C7F:
            counts["te"] += 1

        # Kannada
        elif 0x0C80 <= code <= 0x0CFF:
            counts["kn"] += 1

        # Malayalam
        elif 0x0D00 <= code <= 0x0D7F:
            counts["ml"] += 1

        # Arabic script
        elif 0x0600 <= code <= 0x06FF:
            counts["ur"] += 1

        # Basic Latin
        elif (
            0x0041 <= code <= 0x005A
            or 0x0061 <= code <= 0x007A
        ):
            counts["en"] += 1

    if not counts:
        return "en"

    return max(counts, key=lambda language: counts[language])

def get_language_candidates():
    """
    Return the Tesseract languages we can safely test for
    automatic language detection.
    """
    installed = get_installed_languages()

    candidates = [
        ("eng", "en"),
        ("hin", "hi"),
        ("ben", "bn"),
        ("asm", "as"),
        ("guj", "gu"),
        ("mar", "mr"),
        ("pan", "pa"),
        ("ori", "or"),
        ("tam", "ta"),
        ("tel", "te"),
        ("kan", "kn"),
        ("mal", "ml"),
        ("urd", "ur"),
    ]

    return [
        (tess_lang, app_lang)
        for tess_lang, app_lang in candidates
        if tess_lang in installed
    ]

def detect_language_from_image(image):
    """
    Quickly test installed language models and choose the one
    producing the strongest OCR confidence.
    """

    candidates = get_language_candidates()

    if not candidates:
        return "eng"

    best_language = "eng"
    best_confidence = -1.0

    for tess_lang, app_lang in candidates:

        try:
            data = pytesseract.image_to_data(
                image,
                lang=tess_lang,
                config="--oem 3 --psm 11",
                output_type=Output.DICT,
            )

            confidences = []
            text_count = 0

            for i, text in enumerate(data["text"]):

                text = text.strip()

                if not text:
                    continue

                try:
                    conf = float(data["conf"][i])
                except (ValueError, TypeError):
                    continue

                if conf >= 0:
                    confidences.append(conf)
                    text_count += 1

            if not confidences:
                continue

            mean_confidence = float(
                np.mean(confidences)
            )

            # Small bonus for actually finding text.
            score = (
                mean_confidence
                + min(text_count, 50) * 0.10
            )

            if score > best_confidence:
                best_confidence = score
                best_language = tess_lang

        except Exception as exc:
            print(
                f"Language detection failed for "
                f"{tess_lang}: {exc}"
            )

    return best_language


def _run_single(image, tess_lang, psm):
    config = f"--oem 3 --psm {psm}"

    data = pytesseract.image_to_data(
        image,
        lang=tess_lang,
        config=config,
        output_type=Output.DICT
    )

    words = []

    for i, text in enumerate(data["text"]):

        text = text.strip()

        if not text:
            continue

        try:
            conf = float(data["conf"][i])
        except Exception:
            conf = 0.0

        if conf < 0:
            continue

        words.append({
            "text": text,
            "conf": conf,
            "left": int(data["left"][i]),
            "top": int(data["top"][i]),
            "width": int(data["width"][i]),
            "height": int(data["height"][i]),
            "line_num": int(data["line_num"][i]),
            "block_num": int(data["block_num"][i]),
        })

    return words


def _build_lines(words):
    lines = {}

    for word in words:
        key = (
            word["block_num"],
            word["line_num"]
        )

        lines.setdefault(key, []).append(word)

    result = []

    for key in sorted(lines.keys()):

        line_words = sorted(
            lines[key],
            key=lambda x: x["left"]
        )

        result.append({
            "text": " ".join(
                w["text"] for w in line_words
            ),
            "words": line_words,
        })

    return result


# def run_ocr(image, languages=None):
#     """
#     Multi-pass OCR.

#     PSM 6  = structured page
#     PSM 11 = sparse text
#     PSM 12 = sparse text with more layout tolerance
#     """

#     languages = languages or ["en"]

#     tess_langs = "+".join(
#         LANG_MAP.get(
#             lang,
#             "eng"
#         )
#         for lang in languages
#     )

#     all_results = []

def run_ocr(image, languages=None):
    """
    Multi-pass OCR.

    PSM 6  = structured page
    PSM 11 = sparse text
    PSM 12 = sparse text with more layout tolerance
    """

    # languages = languages or ["auto"]

    # if languages == ["auto"]:
    #     tess_langs = resolve_language("auto")
    # else:
    #     tess_langs = "+".join(
    #         resolve_language(language)
    #         for language in languages
    #     )

    languages = languages or ["auto"]

    detected_language = None

    if languages == ["auto"]:
        # Get an image suitable for quick language detection.
        if isinstance(image, dict):
            variants = image.get("variants", {})
            if "original" in variants:
                detection_image = variants["original"]
            elif variants:
                detection_image = next(iter(variants.values()))
            else:
                detection_image = None
        else:
            detection_image = image

        if detection_image is not None:
            detected_language = detect_language_from_image(detection_image)
            tess_langs = detected_language
        else:
            tess_langs = "eng"
    else:
        tess_langs = "+".join(
            resolve_language(language)
            for language in languages
        )
        detected_language = tess_langs

    all_results = []

    # If preprocessing supplied variants, use them.
    if isinstance(image, dict):
        variants = image.get("variants", {})
    else:
        variants = {"input": image}

    for variant_name, variant_image in variants.items():
        for psm in (6, 11, 12):
            try:
                words = _run_single(variant_image, tess_langs, psm)
                if words:
                    all_results.append({
                        "variant": variant_name,
                        "psm": psm,
                        "words": words,
                    })
            except Exception as exc:
                print(f"OCR failed: {variant_name}, PSM {psm}: {exc}")

    if not all_results:
        return {
            "full_text": "",
            "words": [],
            "mean_word_confidence": 0.0,
        }

    def result_score(result):
        words = result["words"]
        if not words:
            return 0
        confidence = np.mean([w["conf"] for w in words])
        return confidence + min(len(words), 100) * 0.05

    best = max(all_results, key=result_score)
    words = best["words"]
    lines = _build_lines(words)
    full_text = "\n".join(line["text"] for line in lines)
    mean_conf = float(np.mean([w["conf"] for w in words])) if words else 0.0

    # return {
    #     "full_text": full_text,
    #     "words": words,
    #     "mean_word_confidence": round(mean_conf, 2),
    #     "ocr_variant": best["variant"],
    #     "ocr_psm": best["psm"],
    # }

    return {
    "full_text": full_text,
    "words": words,
    "mean_word_confidence": round(
        mean_conf,
        2
    ),
    "ocr_variant": best["variant"],
    "ocr_psm": best["psm"],
    "detected_language": detected_language,
    "tesseract_language": tess_langs,
}
