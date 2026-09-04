"""
generate_samples.py
--------------------
Synthesizes mock Record-of-Rights (RoR) / Khatauni style land-record documents
as images, together with machine-readable ground truth, so the extraction
pipeline can be demonstrated and evaluated end-to-end without needing access
to real (sensitive, access-restricted) government land records.

Each generated document is rendered first as a "clean" printed page and then
put through a degradation step (rotation, gaussian noise, blur, JPEG-style
compression artefacts) to approximate a real scanned/photographed document,
which is the realistic input the production system must handle.
"""
import json
import os
import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2

random.seed(7)
np.random.seed(7)

OUT_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(OUT_DIR, exist_ok=True)

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def get_font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# A small pool of synthetic-but-plausible records. Names/villages are
# invented placeholders, not real people or places.
RECORDS = [
    {
        "owner_name": "Ram Bahadur Thapa",
        "father_name": "Late Deben Thapa",
        "survey_number": "SY-1042/B",
        "khasra_number": "412",
        "khata_number": "87",
        "plot_area": "2.35 acres",
        "village": "Rangapara",
        "tehsil": "Sonapur",
        "district": "Kamrup",
        "land_classification": "Agricultural - Irrigated",
        "mutation_number": "MUT-2291",
        "registration_number": "REG/2024/00456",
    },
    {
        "owner_name": "Anjali Devi Sharma",
        "father_name": "Nabin Sharma",
        "survey_number": "SY-0876/A",
        "khasra_number": "129",
        "khata_number": "34",
        "plot_area": "0.75 hectare",
        "village": "Beltola",
        "tehsil": "Guwahati",
        "district": "Kamrup Metro",
        "land_classification": "Homestead",
        "mutation_number": "MUT-1187",
        "registration_number": "REG/2023/09981",
    },
    {
        "owner_name": "Mohammad Iqbal Hussain",
        "father_name": "Abdul Hussain",
        "survey_number": "SY-2210/C",
        "khasra_number": "765",
        "khata_number": "156",
        "plot_area": "1.10 acres",
        "village": "Chandrapur",
        "tehsil": "Rangia",
        "district": "Kamrup",
        "land_classification": "Agricultural - Unirrigated",
        "mutation_number": "MUT-3062",
        "registration_number": "REG/2022/04471",
    },
]


def render_clean_document(record: dict, doc_id: str) -> Image.Image:
    W, H = 1240, 1600  # ~150dpi A4 portrait
    img = Image.new("L", (W, H), color=255)
    draw = ImageDraw.Draw(img)

    title_font = get_font(34)
    header_font = get_font(22)
    body_font = get_font(24)
    small_font = get_font(18)

    y = 60
    draw.text((W // 2 - 260, y), "RECORD OF RIGHTS (KHATAUNI)", font=title_font, fill=0)
    y += 50
    draw.text((W // 2 - 200, y), f"Revenue Circle Office | Doc Ref: {doc_id}", font=small_font, fill=0)
    y += 60
    draw.line([(60, y), (W - 60, y)], fill=0, width=2)
    y += 30

    rows = [
        ("Owner Name", record["owner_name"]),
        ("Father's / Guardian's Name", record["father_name"]),
        ("Survey Number", record["survey_number"]),
        ("Khasra Number", record["khasra_number"]),
        ("Khata Number", record["khata_number"]),
        ("Plot Area", record["plot_area"]),
        ("Village", record["village"]),
        ("Tehsil", record["tehsil"]),
        ("District", record["district"]),
        ("Land Classification", record["land_classification"]),
        ("Mutation Number", record["mutation_number"]),
        ("Registration Number", record["registration_number"]),
    ]

    label_x = 80
    value_x = 480
    for label, value in rows:
        draw.text((label_x, y), f"{label}", font=header_font, fill=0)
        draw.text((value_x, y), f": {value}", font=body_font, fill=0)
        y += 56

    y += 20
    draw.line([(60, y), (W - 60, y)], fill=0, width=1)
    y += 30
    draw.text((80, y), "Certified to be a true extract from the Register of Rights", font=small_font, fill=0)
    y += 34
    draw.text((80, y), "maintained under the Land Revenue Code.", font=small_font, fill=0)

    return img


def degrade(img: Image.Image, level: str) -> Image.Image:
    arr = np.array(img)

    if level == "clean":
        return img

    # Rotation to simulate a skewed scan/photograph
    angle = random.uniform(-3.5, 3.5) if level == "medium" else random.uniform(-7, 7)
    h, w = arr.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    arr = cv2.warpAffine(arr, M, (w, h), borderValue=255)

    # Gaussian noise to simulate low-quality scan/camera sensor noise
    noise_sigma = 6 if level == "medium" else 14
    noise = np.random.normal(0, noise_sigma, arr.shape)
    arr = np.clip(arr.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    # Slight blur to simulate camera focus / photocopy generation loss
    ksize = 3 if level == "medium" else 5
    arr = cv2.GaussianBlur(arr, (ksize, ksize), 0)

    # Uneven illumination (common in phone-photographed documents)
    if level == "heavy":
        gradient = np.tile(np.linspace(-20, 20, arr.shape[1]), (arr.shape[0], 1))
        arr = np.clip(arr.astype(np.float32) + gradient, 0, 255).astype(np.uint8)

    return Image.fromarray(arr)


def main():
    manifest = []
    quality_levels = ["clean", "medium", "heavy"]
    for i, record in enumerate(RECORDS):
        doc_id = f"DOC{i+1:03d}"
        clean_img = render_clean_document(record, doc_id)
        level = quality_levels[i % len(quality_levels)]
        final_img = degrade(clean_img, level)

        fname = f"{doc_id}.png"
        final_img.save(os.path.join(OUT_DIR, fname))

        gt = dict(record)
        gt["doc_id"] = doc_id
        gt["scan_quality"] = level
        manifest.append(gt)

    with open(os.path.join(OUT_DIR, "ground_truth.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated {len(manifest)} synthetic land-record documents in {OUT_DIR}")


if __name__ == "__main__":
    main()
