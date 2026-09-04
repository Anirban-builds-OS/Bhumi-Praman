"""
Smoke tests for the AI pipeline as integrated into Bhumi Praman.
Run with: pytest ai/tests/test_pipeline_smoke.py -v
(from the backend venv, with the ai/ dir on PYTHONPATH -- see backend/app/services/pipeline_service.py for how the real API does this)
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pipeline
import validator
import field_locator

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_documents")
GT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "ground_truth", "ground_truth.json")


def test_pipeline_runs_on_all_sample_docs():
    with open(GT_PATH) as f:
        ground_truth = json.load(f)
    for rec in ground_truth:
        doc_id = rec["doc_id"]
        image_path = os.path.join(SAMPLE_DIR, f"{doc_id}.png")
        result = pipeline.process_document(image_path)
        assert "fields" in result
        assert len(result["fields"]) == 12
        assert 0.0 <= result["record_confidence"] <= 1.0
        assert isinstance(result["validation_issues"], list)


def test_field_locator_finds_boxes_for_present_values():
    result = pipeline.process_document(os.path.join(SAMPLE_DIR, "DOC001.png"))
    pre = pipeline.preprocessing.preprocess(os.path.join(SAMPLE_DIR, "DOC001.png"))
    ocr_result = pipeline.ocr_engine.run_ocr(pre["final"], languages=["en"])
    locations = field_locator.locate_fields(result["fields"], ocr_result["words"])
    # At least the fields extraction did find a value for should mostly locate
    found_values = [f for f, v in result["fields"].items() if v["value"]]
    located = [f for f in found_values if locations.get(f) is not None]
    assert len(located) >= 1, "expected at least one extracted field to be located back on the page"
    for box in locations.values():
        if box is not None:
            assert box["width"] > 0 and box["height"] > 0


def test_find_duplicates_flags_identical_parcels():
    fields_a = {
        "village": {"value": "Beltola"},
        "khasra_number": {"value": "129"},
        "khata_number": {"value": "34"},
    }
    fields_b = dict(fields_a)  # exact same parcel identifiers
    fields_c = {
        "village": {"value": "Chandrapur"},
        "khasra_number": {"value": "765"},
        "khata_number": {"value": "156"},
    }
    dupes = validator.find_duplicates({"A": fields_a, "B": fields_b, "C": fields_c})
    assert dupes.get("A") == ["B"]
    assert dupes.get("B") == ["A"]
    assert "C" not in dupes


def test_find_duplicates_ignores_records_with_no_identifying_fields():
    # Two records that both failed extraction entirely on the key fields --
    # this must NOT be flagged as a duplicate; it's a data-quality problem,
    # not a "same parcel entered twice" problem.
    blank_a = {"village": {"value": None}, "khasra_number": {"value": None}, "khata_number": {"value": None}}
    blank_b = {"village": {"value": ""}, "khasra_number": {"value": None}, "khata_number": {"value": None}}
    dupes = validator.find_duplicates({"A": blank_a, "B": blank_b})
    assert dupes == {}


def test_find_conflicts_flags_same_survey_different_owner():
    fields_a = {"owner_name": {"value": "Ramesh Kumar"}, "survey_number": {"value": "127/3"}, "khasra_number": {"value": None}}
    fields_b = {"owner_name": {"value": "Suresh Kumar"}, "survey_number": {"value": "127/3"}, "khasra_number": {"value": None}}
    conflicts = validator.find_conflicts({"A": fields_a, "B": fields_b})
    assert "A" in conflicts and "B" in conflicts
    assert conflicts["A"][0]["shared_field"] == "survey_number"


def test_find_conflicts_ignores_same_owner():
    fields_a = {"owner_name": {"value": "Ramesh Kumar"}, "survey_number": {"value": "127/3"}, "khasra_number": {"value": None}}
    fields_b = {"owner_name": {"value": "Ramesh Kumar"}, "survey_number": {"value": "127/3"}, "khasra_number": {"value": None}}
    conflicts = validator.find_conflicts({"A": fields_a, "B": fields_b})
    assert conflicts == {}
