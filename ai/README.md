# Crystal AI Pipeline

The OCR/extraction engine originally built as a standalone prototype for
**Smart India Hackathon 2026 — Problem Statement 26018: Intelligent Land
Record Digitization and Validation System**, now wrapped by the Bhumi
Praman web application. Everything below still runs standalone from this
directory exactly as it did originally; the FastAPI backend additionally
calls into it through a thin adapter
(`backend/app/services/pipeline_service.py`) so none of this code needs to
know it's being called from a web request.

## What this is

1. **Preprocesses** a scanned land-record image (deskew, denoise, illumination
   normalization, binarization) — `preprocessing.py`
2. Runs **multilingual OCR** (English / Hindi / Assamese) with per-word confidence
   *and bounding boxes* — `ocr_engine.py`
3. **Classifies** the recognized text into the twelve land-record fields the problem
   statement names — `field_extractor.py`
4. **Scores confidence** per field from two independent signals (OCR confidence and
   pattern-match confidence) — `confidence_scorer.py`
5. **Locates** each extracted value back to its bounding box on the page, for the
   verification workspace's real source-highlighting — `field_locator.py` *(added
   during web integration; not part of the original standalone submission)*
6. **Validates** the record against business rules, checks for duplicates across a
   batch, and flags possible ownership conflicts — `validator.py` (conflict
   detection added during integration, alongside the original duplicate detection)
7. Ties it all together end to end — `pipeline.py`
8. **Evaluates** the whole thing against a small labelled synthetic test set, producing
   the CER / precision / recall / F1 / confidence-calibration numbers — `evaluate.py`

`generate_samples.py` synthesizes the test documents themselves (mock Record-of-Rights
extracts, rendered then artificially degraded with rotation/noise/blur) since real land
records are sensitive, access-restricted government data that cannot be used for a public
hackathon demo.

## Quick start (standalone, no web app needed)

```bash
# System dependency (Ubuntu/Debian): Tesseract OCR with English, Hindi and Assamese data
sudo apt-get install -y tesseract-ocr tesseract-ocr-hin tesseract-ocr-asm
# Windows: see the root README's Prerequisites section

# Python dependencies
pip install -r requirements.txt

# Run the full pipeline on one document (uses the sample docs already in ../data/)
python3 pipeline.py ../data/sample_documents/DOC001.png

# Run the full evaluation across all sample documents
python3 evaluate.py
```

`evaluate.py` writes to `output/`: `evaluation_report.json` (full numeric results),
`evaluation_summary.csv` (flat per-field metrics table), `field_f1_chart.png` (bar
chart of per-field F1). The web app's admin-only **Run Evaluation** button calls this
same code and shows the same numbers live — never a hard-coded figure.

`build_diagram.py` regenerates the system architecture diagram
(`output/crystal_architecture.png`) via Graphviz.

To regenerate the sample documents themselves (they're already committed under
`../data/`, so this is only needed if you want a different synthetic set):
`python3 generate_samples.py` writes into a local `sample_data/` here — copy the
output into `../data/sample_documents/` and `../data/ground_truth/ground_truth.json`
to use it with the web app, or point `CRYSTAL_SAMPLE_DIR` /
`CRYSTAL_GROUND_TRUTH_PATH` at it directly (see `evaluate.py`).

## Honest scope of this prototype

This proves the architecture end to end; it is not a production system:

| Component | Here | For a real submission / production |
|---|---|---|
| OCR engine | Tesseract (offline, no model download, genuinely multilingual, printed text only) | PaddleOCR-VL or a fine-tuned TrOCR/Donut model for handwriting |
| Field classification | Regex/rule-based | A trained NER/sequence-labelling model once real labelled data exists, rule-based layer kept as an auditable fallback |
| Test documents | Synthetic printed-text RoR extracts with known ground truth | Real, properly authorized/consented/anonymized scanned registers, including handwritten ones |
| Measured accuracy | Macro F1 = 0.042, mean CER = 62% on the 3-doc synthetic set (heavily degraded scans are genuinely hard for off-the-shelf OCR) | Improves directly with a trained model and a larger, real evaluation set |
| Storage & integration | Called from a FastAPI + SQLite/PostgreSQL web app | DILRMP/NGDRS/GIS integration adapters (architecture is integration-ready, not integrated) |

## File map

```
ai/
  generate_samples.py     - synthetic test document generator
  preprocessing.py        - deskew / denoise / binarize
  ocr_engine.py            - multilingual OCR wrapper (env-configurable tesseract path)
  field_extractor.py       - rule-based field classification
  confidence_scorer.py     - multi-signal confidence scoring
  field_locator.py         - links extracted values back to page coordinates [added]
  validator.py              - business rules, duplicate detection, conflict detection
  pipeline.py               - end-to-end orchestration (run this on one file)
  evaluate.py                - batch evaluation harness (paths env-configurable)
  build_diagram.py           - regenerates the architecture diagram
  requirements.txt
  tests/                      - pytest smoke tests for this package
  output/                     - evaluation results + diagram (after running evaluate.py / build_diagram.py)
```

Sample data lives at the repo's top-level `../data/` (shared with the web app's seed
script), not in a local `sample_data/` folder as in the original standalone version.
