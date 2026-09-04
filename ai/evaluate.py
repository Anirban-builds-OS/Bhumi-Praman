"""
evaluate.py
------------
Implements PS requirement around measurable accuracy: runs the full
pipeline over every document in sample_data/ (each with known ground
truth), and reports:

  1. Character Error Rate (CER) of the raw OCR layer, per document and
     averaged -- the standard OCR-quality metric used throughout the
     literature cited in the accompanying report.
  2. Field-level Precision / Recall / F1 for every structured field --
     the metric that actually matters to a land-records office, since a
     perfect CER on the page does not guarantee the khasra number ended
     up in the khasra_number slot.
  3. A confidence-calibration check: does the confidence score the system
     assigns actually correlate with whether the field was extracted
     correctly? (this is what justifies trusting the confidence score to
     drive the human-in-the-loop routing decision in production)

Outputs:
  output/evaluation_report.json   -- full numeric results
  output/field_f1_chart.png       -- bar chart of per-field F1
  output/evaluation_summary.csv   -- flat table, easy to paste into slides
"""
import json
import os

import jiwer
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import pipeline

BASE_DIR = os.path.dirname(__file__)
# PORTABILITY FIX (found via integration testing): the original prototype
# kept sample_data/ as a sibling of this file. The web app's repo layout
# separates code (ai/) from data (top-level data/) per the architecture in
# the engineering brief, so these are now overridable via environment
# variables -- defaulting to the original layout so `python3 evaluate.py`
# still works standalone, unchanged, exactly as before if run from ai/
# with a local sample_data/ present.
SAMPLE_DIR = os.environ.get("CRYSTAL_SAMPLE_DIR", os.path.join(BASE_DIR, "sample_data"))
GROUND_TRUTH_PATH = os.environ.get("CRYSTAL_GROUND_TRUTH_PATH", os.path.join(SAMPLE_DIR, "ground_truth.json"))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def normalize(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.lower().split())


def ground_truth_text(record: dict) -> str:
    """Flattens a ground-truth record into the same 'Label : Value' text
    shape the synthetic document was rendered from, so CER can be computed
    against what the page actually says."""
    label_map = {
        "owner_name": "Owner Name",
        "father_name": "Father's / Guardian's Name",
        "survey_number": "Survey Number",
        "khasra_number": "Khasra Number",
        "khata_number": "Khata Number",
        "plot_area": "Plot Area",
        "village": "Village",
        "tehsil": "Tehsil",
        "district": "District",
        "land_classification": "Land Classification",
        "mutation_number": "Mutation Number",
        "registration_number": "Registration Number",
    }
    lines = ["RECORD OF RIGHTS (KHATAUNI)",
              f"Revenue Circle Office | Doc Ref: {record['doc_id']}"]
    lines += [f"{label} : {record[key]}" for key, label in label_map.items()]
    lines += ["Certified to be a true extract from the Register of Rights",
              "maintained under the Land Revenue Code."]
    return "\n".join(lines)


def main():
    with open(GROUND_TRUTH_PATH) as f:
        ground_truth = {r["doc_id"]: r for r in json.load(f)}

    field_names = [k for k in ground_truth[next(iter(ground_truth))].keys()
                   if k not in ("doc_id", "scan_quality")]

    per_field_counts = {f: {"tp": 0, "fp": 0, "fn": 0} for f in field_names}
    calibration_rows = []  # (confidence_bucket, was_correct)
    cer_scores = []
    per_doc_rows = []

    for doc_id, gt in ground_truth.items():
        image_path = os.path.join(SAMPLE_DIR, f"{doc_id}.png")
        result = pipeline.process_document(image_path)

        # --- CER of the raw OCR layer for this document ---
        pre = pipeline.preprocessing.preprocess(image_path)
        ocr_result = pipeline.ocr_engine.run_ocr(pre["final"], languages=["en"])
        ref_text = ground_truth_text(gt)
        cer = jiwer.cer(ref_text, ocr_result["full_text"])
        cer_scores.append(cer)

        correct_fields = 0
        for field in field_names:
            extracted = result["fields"][field]
            extracted_value = normalize(extracted["value"])
            true_value = normalize(gt[field])
            is_correct = extracted_value == true_value

            if extracted["value"] is None:
                if true_value:
                    per_field_counts[field]["fn"] += 1
            else:
                if is_correct:
                    per_field_counts[field]["tp"] += 1
                    correct_fields += 1
                else:
                    per_field_counts[field]["fp"] += 1
                    per_field_counts[field]["fn"] += 1  # the true value was never surfaced

            calibration_rows.append((extracted["confidence_bucket"], is_correct))

        per_doc_rows.append({
            "doc_id": doc_id,
            "scan_quality": gt["scan_quality"],
            "deskew_angle_deg": result["deskew_angle_deg"],
            "ocr_mean_word_confidence": result["ocr_mean_word_confidence"],
            "cer": round(cer, 4),
            "fields_correct": correct_fields,
            "fields_total": len(field_names),
            "record_confidence": result["record_confidence"],
            "auto_approvable": result["auto_approvable"],
        })

    # --- Field-level precision / recall / F1 ---
    field_metrics = {}
    for field, counts in per_field_counts.items():
        tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        field_metrics[field] = {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
            "support": tp + fn,
        }

    macro_f1 = sum(m["f1"] for m in field_metrics.values()) / len(field_metrics)

    # --- Confidence calibration: accuracy within each confidence bucket ---
    calibration = {}
    for bucket in ("high", "medium", "low", "missing"):
        rows = [correct for b, correct in calibration_rows if b == bucket]
        if rows:
            calibration[bucket] = {
                "count": len(rows),
                "accuracy_when_bucket_used": round(sum(rows) / len(rows), 3),
            }

    report = {
        "documents_evaluated": len(ground_truth),
        "mean_cer": round(sum(cer_scores) / len(cer_scores), 4),
        "macro_average_f1": round(macro_f1, 3),
        "field_metrics": field_metrics,
        "confidence_calibration": calibration,
        "per_document": per_doc_rows,
    }

    with open(os.path.join(OUTPUT_DIR, "evaluation_report.json"), "w") as f:
        json.dump(report, f, indent=2)

    # CSV summary (handy for slides)
    df = pd.DataFrame(field_metrics).T
    df.index.name = "field"
    df.to_csv(os.path.join(OUTPUT_DIR, "evaluation_summary.csv"))

    # Chart: per-field F1
    fig, ax = plt.subplots(figsize=(9, 5))
    fields_sorted = sorted(field_metrics.items(), key=lambda kv: kv[1]["f1"])
    labels = [f for f, _ in fields_sorted]
    values = [m["f1"] for _, m in fields_sorted]
    colors = ["#d9534f" if v < 0.7 else "#f0ad4e" if v < 0.9 else "#5cb85c" for v in values]
    ax.barh(labels, values, color=colors)
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("F1 score")
    ax.set_title(f"Crystal prototype -- per-field extraction F1 (macro avg = {macro_f1:.2f})")
    for i, v in enumerate(values):
        ax.text(v + 0.01, i, f"{v:.2f}", va="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "field_f1_chart.png"), dpi=150)
    plt.close(fig)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
