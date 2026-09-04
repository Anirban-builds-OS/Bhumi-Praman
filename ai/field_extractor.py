# """
# field_extractor.py
# --------------------
# Classifies raw OCR text into the structured land-record fields called out in
# Problem Statement 26018: landowner details, survey number, khasra number,
# khata number, plot area, village, tehsil, district, land classification,
# mutation number, registration number.

# This prototype uses regex/keyword rules tuned to the common
# "Label : Value" layout found on Records of Rights (RoR) / Khatauni extracts.
# This is intentionally the same tier of approach a first hackathon prototype
# would ship (fast, transparent, zero training data required) -- the
# "Tech Stack" section of the report explains how this layer would be upgraded
# to a trained sequence-labelling / LayoutLM-style model once real, labelled
# land-record data is available, and why keeping a rule-based fallback
# alongside the learned model is still good practice for auditability.

# Each pattern also carries a "pattern_confidence" weight reflecting how
# specific/unambiguous that pattern is, which the confidence scorer combines
# with OCR confidence.
# """
# import re

# FIELD_PATTERNS = {
#     "owner_name": [
#         (r"owner\s*name\s*[:\-\.]?\s*([A-Za-z][A-Za-z\. ]{2,60})", 0.95),
#     ],
#     "father_name": [
#         (r"father.{0,15}guardian.{0,10}name\s*[:\-\.]?\s*([A-Za-z][A-Za-z\. ]{2,60})", 0.9),
#         (r"(?:s/o|d/o|w/o)\s*[:\-\.]?\s*([A-Za-z][A-Za-z\. ]{2,60})", 0.7),
#     ],
#     "survey_number": [
#         (r"survey\s*number\s*[:\-\.]?\s*([A-Za-z0-9\-\/]{2,20})", 0.95),
#     ],
#     "khasra_number": [
#         (r"khasra\s*number\s*[:\-\.]?\s*([A-Za-z0-9\-\/]{1,20})", 0.95),
#     ],
#     "khata_number": [
#         (r"khata\s*number\s*[:\-\.]?\s*([A-Za-z0-9\-\/]{1,20})", 0.95),
#     ],
#     "plot_area": [
#         (r"plot\s*area\s*[:\-\.]?\s*([0-9]+\.?[0-9]*\s*(?:acres?|hectares?|sq\.?\s?m|bigha|katha))", 0.9),
#     ],
#     "village": [
#         (r"village\s*[:\-\.]?\s*([A-Za-z][A-Za-z ]{2,40})", 0.9),
#     ],
#     "tehsil": [
#         (r"tehsil\s*[:\-\.]?\s*([A-Za-z][A-Za-z ]{2,40})", 0.9),
#     ],
#     "district": [
#         (r"district\s*[:\-\.]?\s*([A-Za-z][A-Za-z ]{2,40})", 0.9),
#     ],
#     "land_classification": [
#         (r"land\s*classification\s*[:\-\.]?\s*([A-Za-z][A-Za-z\- ]{2,40})", 0.9),
#     ],
#     "mutation_number": [
#         (r"mutation\s*number\s*[:\-\.]?\s*([A-Za-z0-9\-\/]{2,20})", 0.95),
#     ],
#     "registration_number": [
#         (r"registration\s*number\s*[:\-\.]?\s*([A-Za-z0-9\-\/]{2,20})", 0.95),
#     ],
# }

# # Fields that should be validated as "known vocabulary" / cross-checked
# # against a reference list in a real deployment (district/tehsil/village
# # master data from the state LRMS). Kept here so validator.py and the
# # report can point at the same source of truth.
# GEO_FIELDS = {"village", "tehsil", "district"}
# NUMERIC_ID_FIELDS = {"survey_number", "khasra_number", "khata_number", "mutation_number", "registration_number"}


# def _clean_value(raw_value: str) -> str:
#     value = raw_value.strip()
#     value = re.sub(r"\s+", " ", value)
#     value = value.rstrip(".,:;")
#     return value


# def extract_fields(ocr_text: str) -> dict:
#     """Runs every field's regex family against the OCR text and returns, for
#     each field, the best match plus the pattern_confidence that produced it.
#     A field with no match is returned with value=None and confidence=0.0 so
#     it is unambiguously flagged for human review downstream."""
#     text = ocr_text
#     results = {}

#     for field, patterns in FIELD_PATTERNS.items():
#         best = {"value": None, "pattern_confidence": 0.0}
#         for pattern, weight in patterns:
#             match = re.search(pattern, text, flags=re.IGNORECASE)
#             if match:
#                 value = _clean_value(match.group(1))
#                 if value and weight > best["pattern_confidence"]:
#                     best = {"value": value, "pattern_confidence": weight}
#         results[field] = best

#     return results

"""
field_extractor.py
------------------
OCR-tolerant field extraction for Bhumi Praman.

The OCR engine can make small mistakes in labels and separators, for example:

    Khasra Number  -> Khasra. Number
    Plot Area      -> Plt Area
    Owner Name :   -> Owner Name +
    Village :      -> Village - 1
    Father's ...   -> Fathen's /Guandian's Name

This extractor tolerates those errors while keeping the same output format
expected by the existing confidence scorer and backend.

IMPORTANT:
This module does NOT invent values. If OCR produces "SF" for a field that
visually looks like "87", this module will return "SF". That should remain
a low-confidence/manual-review case rather than silently changing the value.
"""

# import re


# # ---------------------------------------------------------------------------
# # PUBLIC FIELD PATTERNS
# # ---------------------------------------------------------------------------
# # pipeline_service.py imports FIELD_PATTERNS, so keep this constant.

# FIELD_PATTERNS = {
#     "owner_name": [
#         (r"owner\s*name", 0.95),
#     ],

#     "father_name": [
#         (r"father.*guardian.*name", 0.90),
#         (r"father\s*name", 0.85),
#     ],

#     "survey_number": [
#         (r"survey\s*(?:number|no\.?)", 0.95),
#     ],

#     "khasra_number": [
#         (r"khasra\s*(?:number|no\.?)", 0.95),
#     ],

#     "khata_number": [
#         (r"khata\s*(?:number|no\.?)", 0.95),
#     ],

#     "plot_area": [
#         (r"plot\s*area", 0.90),
#     ],

#     "village": [
#         (r"village", 0.90),
#     ],

#     "tehsil": [
#         (r"tehsil", 0.90),
#     ],

#     "district": [
#         (r"district", 0.90),
#     ],

#     "land_classification": [
#         (r"land\s*classification", 0.90),
#     ],

#     "mutation_number": [
#         (r"mutation\s*(?:number|no\.?)", 0.95),
#     ],

#     "registration_number": [
#         (r"registration\s*(?:number|no\.?)", 0.95),
#     ],
# }


# GEO_FIELDS = {
#     "village",
#     "tehsil",
#     "district",
# }


# NUMERIC_ID_FIELDS = {
#     "survey_number",
#     "khasra_number",
#     "khata_number",
#     "mutation_number",
#     "registration_number",
# }


# # ---------------------------------------------------------------------------
# # COMMON OCR ERRORS IN FIELD LABELS
# # ---------------------------------------------------------------------------
# # These corrections are intentionally limited to LABELS.
# # We do NOT globally correct values because that could create false data.

# LABEL_CORRECTIONS = [

#     # Father's / Guardian's Name
#     (r"\bfathen['’]?s\b", "father's"),
#     (r"\bfathen\b", "father"),
#     (r"\bguandian['’]?s\b", "guardian's"),
#     (r"\bguandian\b", "guardian"),

#     # Plot Area
#     (r"\bplt\b", "plot"),
#     (r"\barca\b", "area"),

#     # Khasra / Khata labels
#     (r"\bkhasra\s*[.\-]\s*number\b", "khasra number"),
#     (r"\bkhata\s*[.\-]\s*number\b", "khata number"),

#     # Tehsil
#     (r"\bteb?sil\b", "tehsil"),

#     # Land classification
#     (r"\bhand\s+classification\b", "land classification"),
#     (r"\bland\s+class(?:fication|ification)\b", "land classification"),

#     # Registration
#     (r"\bregishation\b", "registration"),
# ]


# # OCR commonly changes ":" into "-", "+", ">", ".", etc.
# SEPARATOR_RE = r"\s*[:;=+>\-–—.]\s*"


# # ---------------------------------------------------------------------------
# # CLEANING
# # ---------------------------------------------------------------------------

# def _clean_value(value: str) -> str:
#     """Clean an extracted value without changing its meaning."""

#     value = value.replace("’", "'")

#     # Collapse repeated whitespace.
#     value = re.sub(r"\s+", " ", value).strip()

#     # Remove punctuation accidentally attached to the beginning/end.
#     value = value.strip(" .,:;=+>–—-")

#     # Common OCR artefact:
#     #     Village - 1 Rangapara
#     # should become:
#     #     Rangapara
#     value = re.sub(
#         r"^[0-9Il|]{1,2}\s+(?=[A-Za-z])",
#         "",
#         value,
#     )

#     # Normalise spaces around identifier separators.
#     value = re.sub(
#         r"\s*([/\-])\s*",
#         r"\1",
#         value,
#     )

#     return value.strip(" .,:;=+>–—-")


# def _normalise_label_text(line: str) -> str:
#     """
#     Correct only known OCR errors in field labels.

#     We deliberately do NOT correct words inside extracted values.
#     """

#     result = line.replace("’", "'")

#     for pattern, replacement in LABEL_CORRECTIONS:
#         result = re.sub(
#             pattern,
#             replacement,
#             result,
#             flags=re.IGNORECASE,
#         )

#     return result


# # ---------------------------------------------------------------------------
# # FIELD-SPECIFIC EXTRACTION
# # ---------------------------------------------------------------------------

# def _extract_with_pattern(
#     field: str,
#     line: str,
# ) -> tuple[str | None, float]:
#     """
#     Extract a value from one OCR line.

#     Returns:
#         (value, pattern_confidence)
#     """

#     # Fix only known label OCR errors first.
#     line = _normalise_label_text(line)

#     patterns = {

#         "owner_name":
#             rf"\bowner\s+name\b{SEPARATOR_RE}(.+)$",

#         "father_name":
#             rf"\bfather(?:'s)?\s*/?\s*guardian(?:'s)?\s+name\b"
#             rf"{SEPARATOR_RE}(.+)$",

#         "survey_number":
#             rf"\bsurvey\s+(?:number|no\.?)\b"
#             rf"{SEPARATOR_RE}(.+)$",

#         "khasra_number":
#             rf"\bkhasra\s+(?:number|no\.?)\b"
#             rf"{SEPARATOR_RE}(.+)$",

#         "khata_number":
#             rf"\bkhata\s+(?:number|no\.?)\b"
#             rf"{SEPARATOR_RE}(.+)$",

#         "plot_area":
#             rf"\bplot\s+area\b"
#             rf"{SEPARATOR_RE}(.+)$",

#         "village":
#             rf"\bvillage\b"
#             rf"{SEPARATOR_RE}(.+)$",

#         "tehsil":
#             rf"\btehsil\b"
#             rf"{SEPARATOR_RE}(.+)$",

#         "district":
#             rf"\bdistrict\b"
#             rf"{SEPARATOR_RE}(.+)$",

#         "land_classification":
#             rf"\bland\s+classification\b"
#             rf"{SEPARATOR_RE}(.+)$",

#         "mutation_number":
#             rf"\bmutation\s+(?:number|no\.?)\b"
#             rf"{SEPARATOR_RE}(.+)$",

#         "registration_number":
#             rf"\bregistration\s+(?:number|no\.?)\b"
#             rf"{SEPARATOR_RE}(.+)$",
#     }

#     # ---------------------------------------------------------------
#     # First attempt: corrected/exact label
#     # ---------------------------------------------------------------

#     match = re.search(
#         patterns[field],
#         line,
#         flags=re.IGNORECASE,
#     )

#     if match:

#         value = _clean_value(match.group(1))

#         if value:
#             return value, 0.95

#     # ---------------------------------------------------------------
#     # Second attempt: tolerant OCR fallback
#     # ---------------------------------------------------------------

#     fallback_patterns = {

#         "owner_name":
#             r"owner\s+name",

#         "father_name":
#             r"father.*?guardian.*?name|father\s+name|guardian\s+name",

#         "survey_number":
#             r"survey\s+(?:number|no)|surveynumber",

#         "khasra_number":
#             r"khasra\s+(?:number|no)|khasra",

#         "khata_number":
#             r"khata\s+(?:number|no)|khata",

#         "plot_area":
#             r"plot\s+area|plt\s+area|plot\s+arca",

#         "village":
#             r"village",

#         "tehsil":
#             r"tehsil|tehsi",

#         "district":
#             r"district|distric",

#         "land_classification":
#             r"land\s+classification|hand\s+classification",

#         "mutation_number":
#             r"mutation\s+(?:number|no)|mutation",

#         "registration_number":
#             r"registration\s+(?:number|no)|regishation",
#     }

#     match = re.search(
#         rf"(?:{fallback_patterns[field]})"
#         rf"\s*{SEPARATOR_RE}"
#         rf"(.+)$",
#         line,
#         flags=re.IGNORECASE,
#     )

#     if match:

#         value = _clean_value(match.group(1))

#         if value:
#             return value, 0.85

#     return None, 0.0


# # ---------------------------------------------------------------------------
# # VALUE ON NEXT LINE
# # ---------------------------------------------------------------------------

# def _value_on_next_line(
#     field: str,
#     lines: list[str],
#     index: int,
# ) -> str | None:
#     """
#     Handle OCR where the label and value appear on separate lines.
#     """

#     for j in range(
#         index + 1,
#         min(index + 3, len(lines)),
#     ):

#         candidate = lines[j].strip()

#         if not candidate:
#             continue

#         normalised = _normalise_label_text(candidate)

#         # Don't accidentally use another field's label as this field's value.
#         if re.search(
#             r"\b(?:"
#             r"owner\s+name|"
#             r"father(?:'s)?|"
#             r"guardian|"
#             r"survey\s+(?:number|no)|"
#             r"khasra|"
#             r"khata|"
#             r"plot\s+area|"
#             r"village|"
#             r"tehsil|"
#             r"district|"
#             r"land\s+classification|"
#             r"mutation|"
#             r"registration"
#             r")\b",
#             normalised,
#             flags=re.IGNORECASE,
#         ):
#             return None

#         cleaned = _clean_value(candidate)

#         if cleaned:
#             return cleaned

#     return None


# # ---------------------------------------------------------------------------
# # MAIN EXTRACTION FUNCTION
# # ---------------------------------------------------------------------------

# def extract_fields(ocr_text: str) -> dict:
#     """
#     Extract all supported land-record fields.

#     Output format remains:

#         {
#             "owner_name": {
#                 "value": "...",
#                 "pattern_confidence": 0.95
#             },
#             ...
#         }

#     This is compatible with confidence_scorer.py and the existing backend.
#     """

#     fields = list(FIELD_PATTERNS.keys())

#     # Empty OCR result.
#     if not ocr_text or not ocr_text.strip():

#         return {
#             field: {
#                 "value": None,
#                 "pattern_confidence": 0.0,
#             }
#             for field in fields
#         }

#     # Preserve OCR line structure.
#     lines = [
#         re.sub(r"\s+", " ", line).strip()
#         for line in ocr_text.splitlines()
#     ]

#     results = {
#         field: {
#             "value": None,
#             "pattern_confidence": 0.0,
#         }
#         for field in fields
#     }

#     # ---------------------------------------------------------------
#     # Extract every field.
#     # ---------------------------------------------------------------

#     for field in fields:

#         best_value = None
#         best_confidence = 0.0

#         for index, line in enumerate(lines):

#             if not line:
#                 continue

#             # -------------------------------------------------------
#             # Try same-line extraction.
#             # -------------------------------------------------------

#             value, confidence = _extract_with_pattern(
#                 field,
#                 line,
#             )

#             if value and confidence > best_confidence:

#                 best_value = value
#                 best_confidence = confidence

#                 continue

#             # -------------------------------------------------------
#             # Try the following line if label/value are separated.
#             # -------------------------------------------------------

#             normalised = _normalise_label_text(line)

#             label_patterns = {

#                 "owner_name":
#                     r"owner\s+name",

#                 "father_name":
#                     r"father|guardian",

#                 "survey_number":
#                     r"survey",

#                 "khasra_number":
#                     r"khasra",

#                 "khata_number":
#                     r"khata",

#                 "plot_area":
#                     r"plot\s+area|plt\s+area",

#                 "village":
#                     r"village",

#                 "tehsil":
#                     r"tehsil|tehsi",

#                 "district":
#                     r"district",

#                 "land_classification":
#                     r"land\s+classification|hand\s+classification",

#                 "mutation_number":
#                     r"mutation",

#                 "registration_number":
#                     r"registration|regishation",
#             }

#             label_present = bool(
#                 re.search(
#                     label_patterns[field],
#                     normalised,
#                     flags=re.IGNORECASE,
#                 )
#             )

#             if label_present:

#                 next_value = _value_on_next_line(
#                     field,
#                     lines,
#                     index,
#                 )

#                 if next_value and 0.84 > best_confidence:

#                     best_value = next_value
#                     best_confidence = 0.84

#         results[field] = {
#             "value": best_value,
#             "pattern_confidence": round(
#                 best_confidence,
#                 2,
#             ),
#         }

#     return results

"""
field_extractor.py
------------------

Multilingual OCR-tolerant field extractor for Bhumi Praman.

Supports:
- English
- Bengali
- Hindi
- Assamese

Handles:
- Label : Value
- Label - Value
- Label = Value
- Label
  Value

The extractor never changes the actual extracted value.
"""

import re


# ---------------------------------------------------------------------------
# PUBLIC FIELD PATTERNS
# ---------------------------------------------------------------------------

FIELD_PATTERNS = {
    "owner_name": [
        (r"owner\s*name", 0.95),
        (r"মালিকের\s*নাম", 0.95),
        (r"মালিক\s*নাম", 0.90),
        (r"मालिक\s*का\s*नाम", 0.95),
        (r"मालिक\s*नाम", 0.90),
        (r"মালিক", 0.80),
    ],

    "father_name": [
        (r"father(?:'s)?\s*(?:/|\s)?\s*guardian(?:'s)?\s*name", 0.95),
        (r"father\s*name", 0.90),
        (r"guardian\s*name", 0.90),

        # Bengali
        (r"পিতা\s*/?\s*অভিভাবকের\s*নাম", 0.95),
        (r"পিতা\s*/?\s*অভিভাবক", 0.90),
        (r"পিতার\s*নাম", 0.95),
        (r"পিতা\s*নাম", 0.90),

        # Hindi
        (r"पिता\s*/?\s*अभिभावक\s*का\s*नाम", 0.95),
        (r"पिता\s*का\s*नाम", 0.95),
        (r"अभिभावक\s*का\s*नाम", 0.90),
    ],

    "survey_number": [
        (r"survey\s*(?:number|no\.?)", 0.95),
        (r"জরিপ\s*(?:নং|নম্বর|নম্বর)?", 0.95),
        (r"জরীপ\s*(?:নং|নম্বর)?", 0.90),
        (r"सर्वे\s*(?:नंबर|नं\.?)", 0.95),
        (r"सर्वे", 0.80),
    ],

    "khasra_number": [
        (r"khasra\s*(?:number|no\.?)", 0.95),
        (r"খাসরা\s*(?:নং|নম্বর)?", 0.95),
        (r"खसरा\s*(?:नंबर|नं\.?)", 0.95),
        (r"খসড়া\s*(?:নং|নম্বর)?", 0.90),
    ],

    "khata_number": [
        (r"khata\s*(?:number|no\.?)", 0.95),
        (r"খতিয়ান\s*(?:নং|নম্বর)?", 0.95),
        (r"খতিয়ান\s*(?:নং|নম্বর)?", 0.95),
        (r"खाता\s*(?:नंबर|नं\.?)", 0.95),
        (r"खतियान\s*(?:नंबर|नं\.?)", 0.95),
    ],

    "plot_area": [
        (r"plot\s*area", 0.90),
        (r"land\s*area", 0.90),
        (r"জমির\s*পরিমাণ", 0.95),
        (r"জমির\s*আয়তন", 0.90),
        (r"জমির\s*আয়তন", 0.90),
        (r"भूमि\s*(?:का\s*)?क्षेत्रफल", 0.95),
        (r"प्लॉट\s*(?:का\s*)?क्षेत्रफल", 0.90),
    ],

    "village": [
        (r"village", 0.90),
        (r"গ্রাম", 0.95),
        (r"গ্রামের\s*নাম", 0.95),
        (r"गांव", 0.95),
        (r"गाँव", 0.95),
        (r"ग्राम", 0.95),
    ],

    "tehsil": [
        (r"tehsil", 0.90),
        (r"তহশিল", 0.95),
        (r"তহশীল", 0.95),
        (r"মৌজা", 0.85),
        (r"থানা", 0.80),
        (r"तहसील", 0.95),
        (r"तहसील", 0.95),
        (r"मौजा", 0.85),
        (r"थाना", 0.80),
    ],

    "district": [
        (r"district", 0.90),
        (r"জেলা", 0.95),
        (r"জেলার\s*নাম", 0.95),
        (r"जिला", 0.95),
        (r"जिले\s*का\s*नाम", 0.95),
    ],

    "land_classification": [
        (r"land\s*classification", 0.90),
        (r"land\s*class", 0.85),
        (r"জমির\s*শ্রেণি", 0.95),
        (r"জমির\s*শ্রেণী", 0.95),
        (r"ভূমির\s*শ্রেণি", 0.95),
        (r"भूमि\s*वर्गीकरण", 0.95),
        (r"भूमि\s*की\s*श्रेणी", 0.95),
    ],

    "mutation_number": [
        (r"mutation\s*(?:number|no\.?)", 0.95),
        (r"মিউটেশন\s*(?:নং|নম্বর)?", 0.95),
        (r"নামজারি\s*(?:নং|নম্বর)?", 0.90),
        (r"म्यूटेशन\s*(?:नंबर|नं\.?)", 0.95),
        (r"नामांतरण\s*(?:नंबर|नं\.?)", 0.90),
    ],

    "registration_number": [
        (r"registration\s*(?:number|no\.?)", 0.95),
        (r"রেজিস্ট্রেশন\s*(?:নং|নম্বর)?", 0.95),
        (r"নিবন্ধন\s*(?:নং|নম্বর)?", 0.90),
        (r"पंजीकरण\s*(?:नंबर|नं\.?)", 0.95),
        (r"रजिस्ट्रेशन\s*(?:नंबर|नं\.?)", 0.95),
    ],
}


GEO_FIELDS = {
    "village",
    "tehsil",
    "district",
}


NUMERIC_ID_FIELDS = {
    "survey_number",
    "khasra_number",
    "khata_number",
    "mutation_number",
    "registration_number",
}


# ---------------------------------------------------------------------------
# LABEL CORRECTIONS
# ---------------------------------------------------------------------------

LABEL_CORRECTIONS = [
    # English OCR errors
    (r"\bfathen['’]?s\b", "father's"),
    (r"\bfathen\b", "father"),
    (r"\bguandian['’]?s\b", "guardian's"),
    (r"\bguandian\b", "guardian"),
    (r"\bplt\b", "plot"),
    (r"\barca\b", "area"),
    (r"\bkhasra\s*[.\-]\s*number\b", "khasra number"),
    (r"\bkhata\s*[.\-]\s*number\b", "khata number"),
    (r"\bteb?sil\b", "tehsil"),
    (r"\bhand\s+classification\b", "land classification"),
    (r"\bregishation\b", "registration"),
]


# Separators commonly produced by OCR.
SEPARATOR_RE = r"\s*[:;=+>\-–—.]\s*"


# ---------------------------------------------------------------------------
# CLEANING
# ---------------------------------------------------------------------------

def _clean_value(value: str) -> str:
    if not value:
        return ""

    value = value.replace("’", "'")
    value = re.sub(r"\s+", " ", value).strip()

    value = value.strip(" .,:;=+>–—-")

    # Remove accidental OCR numbering before English values.
    value = re.sub(
        r"^[0-9Il|]{1,2}\s+(?=[A-Za-z])",
        "",
        value,
    )

    value = re.sub(
        r"\s*([/\-])\s*",
        r"\1",
        value,
    )

    return value.strip(" .,:;=+>–—-")


def _normalise_label_text(line: str) -> str:
    result = line.replace("’", "'")

    for pattern, replacement in LABEL_CORRECTIONS:
        result = re.sub(
            pattern,
            replacement,
            result,
            flags=re.IGNORECASE,
        )

    return result


# ---------------------------------------------------------------------------
# LABEL DETECTION
# ---------------------------------------------------------------------------

def _label_match(field: str, line: str):
    """
    Return the matching label regex + confidence.
    Works with Unicode labels such as Bengali/Hindi.
    """

    line = _normalise_label_text(line)

    best = None

    for pattern, confidence in FIELD_PATTERNS[field]:
        match = re.search(pattern, line, flags=re.IGNORECASE)

        if match:
            if best is None or confidence > best[1]:
                best = (match, confidence)

    return best


def _contains_any_field_label(line: str) -> bool:
    """
    Prevent one field from stealing another field's label as its value.
    """

    for field in FIELD_PATTERNS:
        if _label_match(field, line):
            return True

    return False


# ---------------------------------------------------------------------------
# SAME-LINE EXTRACTION
# ---------------------------------------------------------------------------

def _extract_with_pattern(field: str, line: str):
    """
    Extract:
        Owner Name : Rahul
        মালিকের নাম : রাহুল
        खाता नं : 123

    Also handles:
        Owner Name - Rahul
        মালিকের নাম - রাহুল
    """

    line = _normalise_label_text(line)

    for pattern, confidence in FIELD_PATTERNS[field]:

        # Label followed by separator and value.
        regex = rf"(?:{pattern}){SEPARATOR_RE}(.+)$"

        match = re.search(
            regex,
            line,
            flags=re.IGNORECASE,
        )

        if match:
            value = _clean_value(match.group(1))

            if value:
                return value, confidence

        # OCR sometimes removes the separator completely.
        # Only use this when there is clearly text after the label.
        match = re.search(
            rf"(?:{pattern})\s+(.+)$",
            line,
            flags=re.IGNORECASE,
        )

        if match:
            value = _clean_value(match.group(1))

            if value and not _contains_any_field_label(value):
                return value, max(confidence - 0.05, 0.70)

    return None, 0.0


# ---------------------------------------------------------------------------
# NEXT-LINE EXTRACTION
# ---------------------------------------------------------------------------

def _value_on_next_line(
    field: str,
    lines: list[str],
    index: int,
):
    """
    Handles:

        মালিকের নাম
        মধুমিতা পাল

        খতিয়ান নং
        672
    """

    # Search only a couple of lines ahead.
    for j in range(
        index + 1,
        min(index + 3, len(lines)),
    ):

        candidate = lines[j].strip()

        if not candidate:
            continue

        # If next line is another known field label,
        # don't steal it.
        if _contains_any_field_label(candidate):
            return None

        cleaned = _clean_value(candidate)

        if cleaned:
            return cleaned

    return None


# ---------------------------------------------------------------------------
# MAIN EXTRACTION
# ---------------------------------------------------------------------------

def extract_fields(ocr_text: str) -> dict:
    """
    Extract all supported land-record fields.

    Output remains compatible with the existing confidence scorer:

        {
            "owner_name": {
                "value": "...",
                "pattern_confidence": 0.95
            },
            ...
        }
    """

    fields = list(FIELD_PATTERNS.keys())

    # Empty OCR.
    if not ocr_text or not ocr_text.strip():
        return {
            field: {
                "value": None,
                "pattern_confidence": 0.0,
            }
            for field in fields
        }

    # Preserve line structure.
    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in ocr_text.splitlines()
    ]

    results = {
        field: {
            "value": None,
            "pattern_confidence": 0.0,
        }
        for field in fields
    }

    # ---------------------------------------------------------------
    # Try every field against every OCR line.
    # ---------------------------------------------------------------

    for field in fields:

        best_value = None
        best_confidence = 0.0

        for index, line in enumerate(lines):

            if not line:
                continue

            # -------------------------------------------------------
            # 1. Same-line extraction
            # -------------------------------------------------------

            value, confidence = _extract_with_pattern(
                field,
                line,
            )

            if value and confidence > best_confidence:
                best_value = value
                best_confidence = confidence

            # -------------------------------------------------------
            # 2. Label on one line, value on next line
            # -------------------------------------------------------

            if _label_match(field, line):

                next_value = _value_on_next_line(
                    field,
                    lines,
                    index,
                )

                if next_value and 0.90 > best_confidence:
                    best_value = next_value
                    best_confidence = 0.90

        results[field] = {
            "value": best_value,
            "pattern_confidence": round(
                best_confidence,
                2,
            ),
        }

    return results
