"""
preprocessing.py
-----------------
Classical (non-deep-learning) preprocessing stage of the Crystal pipeline.

This is deliberately built on OpenCV rather than a learned restoration model
so it runs anywhere with no GPU and no model download -- in production this
stage would sit in front of whichever OCR/VLM engine is selected (see
ocr_engine.py) and its output quality directly drives downstream accuracy.

Steps implemented:
 1. Grayscale normalisation
 2. Deskew (rotation correction) using the minAreaRect of thresholded ink
 3. Denoising (fastNlMeansDenoising)
 4. Adaptive binarisation (Otsu + adaptive threshold fallback)
 5. Contrast normalisation (CLAHE) for uneven illumination
"""
# import cv2
# import numpy as np


# def to_grayscale(img: np.ndarray) -> np.ndarray:
#     if len(img.shape) == 3:
#         return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     return img


# def deskew(gray: np.ndarray) -> tuple[np.ndarray, float]:
#     """Estimate and correct page rotation using the minimum-area bounding
#     rectangle of the dark (ink) pixels. Returns (corrected_image, angle_deg)."""
#     inv = cv2.bitwise_not(gray)
#     thresh = cv2.threshold(inv, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
#     coords = np.column_stack(np.where(thresh > 0))
#     if len(coords) < 50:
#         return gray, 0.0

#     angle = cv2.minAreaRect(coords)[-1]
#     if angle < -45:
#         angle = -(90 + angle)
#     else:
#         angle = -angle

#     # Guard against wild angle estimates on sparse/near-blank inputs
#     if abs(angle) > 20:
#         return gray, 0.0

#     (h, w) = gray.shape[:2]
#     center = (w // 2, h // 2)
#     M = cv2.getRotationMatrix2D(center, angle, 1.0)
#     rotated = cv2.warpAffine(
#         gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
#     )
#     return rotated, angle


# def denoise(gray: np.ndarray) -> np.ndarray:
#     return cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)


# def normalize_illumination(gray: np.ndarray) -> np.ndarray:
#     clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
#     return clahe.apply(gray)


# def binarize(gray: np.ndarray) -> np.ndarray:
#     return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


# def preprocess(image_path: str, save_debug_path: str | None = None) -> dict:
#     """Runs the full preprocessing chain and returns intermediate + final
#     arrays plus metadata (useful both for OCR input and for showing a human
#     reviewer what the system 'saw')."""
#     raw = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
#     if raw is None:
#         raise FileNotFoundError(image_path)

#     gray = to_grayscale(raw)
#     deskewed, angle = deskew(gray)
#     denoised = denoise(deskewed)
#     illum_norm = normalize_illumination(denoised)
#     final = binarize(illum_norm)

#     if save_debug_path:
#         cv2.imwrite(save_debug_path, final)

#     return {
#         "raw": raw,
#         "final": final,
#         "deskew_angle_deg": round(float(angle), 2),
#         "shape": final.shape,
#     }

import cv2
import numpy as np


def to_grayscale(img):
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def deskew(gray):
    """
    Conservative deskew.
    Old documents can have torn edges, so don't aggressively rotate them.
    """
    try:
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        _, thresh = cv2.threshold(
            blur,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        coords = np.column_stack(np.where(thresh > 0))

        if len(coords) < 100:
            return gray, 0.0

        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        if abs(angle) > 10:
            return gray, 0.0

        h, w = gray.shape[:2]
        center = (w // 2, h // 2)

        matrix = cv2.getRotationMatrix2D(
            center,
            angle,
            1.0
        )

        rotated = cv2.warpAffine(
            gray,
            matrix,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )

        return rotated, float(angle)

    except Exception:
        return gray, 0.0


def normalize_contrast(gray):
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    return clahe.apply(gray)


def denoise(gray):
    return cv2.fastNlMeansDenoising(
        gray,
        None,
        h=7,
        templateWindowSize=7,
        searchWindowSize=21
    )


def make_adaptive(gray):
    return cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )


def make_otsu(gray):
    return cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]


def preprocess(image_path, save_debug_path=None):
    raw = cv2.imread(
        image_path,
        cv2.IMREAD_COLOR
    )

    if raw is None:
        raise FileNotFoundError(image_path)

    gray = to_grayscale(raw)

    deskewed, angle = deskew(gray)

    denoised = denoise(deskewed)

    enhanced = normalize_contrast(denoised)

    otsu = make_otsu(enhanced)

    adaptive = make_adaptive(enhanced)

    # IMPORTANT:
    # Keep several versions instead of forcing OCR to use only one.
    variants = {
        "gray": deskewed,
        "enhanced": enhanced,
        "otsu": otsu,
        "adaptive": adaptive,
    }

    if save_debug_path:
        cv2.imwrite(save_debug_path, enhanced)

    return {
        "raw": raw,
        "final": enhanced,
        "variants": variants,
        "deskew_angle_deg": round(angle, 2),
        "shape": enhanced.shape,
    }
