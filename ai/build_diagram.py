import graphviz

g = graphviz.Digraph("crystal_architecture", format="png")
g.attr(rankdir="TB", bgcolor="white", fontname="Helvetica", nodesep="0.35", ranksep="0.55", splines="ortho")
g.attr("node", fontname="Helvetica", fontsize="12", shape="box", style="rounded,filled", color="#33475b", fontcolor="#1a1a1a")
g.attr("edge", fontname="Helvetica", fontsize="10", color="#33475b")

NAVY = "#dbe9f7"
GREEN = "#dcf1e2"
AMBER = "#fdf1d6"
RED = "#fbe2e0"
PURPLE = "#ece3f6"
GREY = "#eeeeee"

# ---- Input sources ----
with g.subgraph(name="cluster_inputs") as c:
    c.attr(label="INPUT SOURCES", style="rounded", color="#888888", fontsize="12", fontname="Helvetica-Bold")
    c.node("scans", "Scanned Registers\n& Legacy PDFs", fillcolor=NAVY)
    c.node("maps", "Cadastral Maps /\nFMBs / Tippans", fillcolor=NAVY)
    c.node("mobile", "Mobile Capture\n(field agents / CSCs)", fillcolor=NAVY)

g.node("intake", "Document Intake API\n(batch upload + mobile + tehsil scanners)", fillcolor=GREY)

g.node("preprocess", "Preprocessing\nDeskew | Denoise | Binarize | Language-ID", fillcolor=NAVY)

g.node("classify_doc", "Document & Script\nType Classifier", fillcolor=NAVY)

with g.subgraph(name="cluster_ocr") as c:
    c.attr(label="MULTI-ENGINE OCR / DOCUMENT-AI LAYER", style="rounded", color="#888888", fontsize="12", fontname="Helvetica-Bold")
    c.node("ocr_print", "Printed-text OCR\n(PaddleOCR-VL / Tesseract)", fillcolor=GREEN)
    c.node("ocr_hand", "Handwriting OCR\n(fine-tuned TrOCR / Donut)", fillcolor=GREEN)
    c.node("layout", "Layout & Table Parser\n(LayoutLMv3-style)", fillcolor=GREEN)

g.node("fusion", "OCR Fusion & Text Normalization\n(transliteration to Schedule-VIII scripts via Bhashini)", fillcolor=GREY)

g.node("nlp", "Field Classification\nRule engine + trained NER (khasra, khata, survey no.,\nowner, village/tehsil/district, area, classification...)", fillcolor=PURPLE)

g.node("confidence", "Multi-Signal Confidence Scoring\n(OCR confidence x pattern/model confidence)", fillcolor=AMBER)

g.node("validate", "Business-Rule Validation &\nDuplicate/Fraud Detection\n(cross-check vs DILRMP / NGDRS / ULPIN master data)", fillcolor=AMBER)

g.node("decision", "Confidence >= threshold\n& rules pass?", shape="diamond", fillcolor="#fff3b0", fontsize="11")

g.node("hitl", "Human-in-the-Loop\nReview Console\n(low/uncertain fields highlighted)", fillcolor=RED)

g.node("store", "Structured Land Record Store\n(versioned DB + GIS parcel layer + audit trail)", fillcolor=GREEN, fontsize="12")

g.node("retrain", "Active-Learning Dataset\n& Periodic Retraining", fillcolor=PURPLE)

with g.subgraph(name="cluster_out") as c:
    c.attr(label="INTEGRATION & CONSUMPTION", style="rounded", color="#888888", fontsize="12", fontname="Helvetica-Bold")
    c.node("api", "Integration APIs\n(LRMS / DILRMP / NGDRS / GIS-Bhuvan)", fillcolor=NAVY)
    c.node("dash", "Role-based Dashboards\n& State/District Analytics", fillcolor=NAVY)
    c.node("citizen", "Citizen Self-Service\n(status, certified copy request)", fillcolor=NAVY)

# Edges
g.edge("scans", "intake")
g.edge("maps", "intake")
g.edge("mobile", "intake")
g.edge("intake", "preprocess")
g.edge("preprocess", "classify_doc")
g.edge("classify_doc", "ocr_print")
g.edge("classify_doc", "ocr_hand")
g.edge("classify_doc", "layout")
g.edge("ocr_print", "fusion")
g.edge("ocr_hand", "fusion")
g.edge("layout", "fusion")
g.edge("fusion", "nlp")
g.edge("nlp", "confidence")
g.edge("confidence", "validate")
g.edge("validate", "decision")
g.edge("decision", "store", label="  yes", fontcolor="#1a7a33")
g.edge("decision", "hitl", label="  no", fontcolor="#a13c33")
g.edge("hitl", "store", label="  corrected")
g.edge("hitl", "retrain", style="dashed")
g.edge("retrain", "ocr_hand", style="dashed", label="  model update", constraint="false")
g.edge("retrain", "nlp", style="dashed", constraint="false")
g.edge("store", "api")
g.edge("store", "dash")
g.edge("store", "citizen")

g.render("output/crystal_architecture", cleanup=True)
print("diagram written to output/crystal_architecture.png")
