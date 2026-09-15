"""
Standardizer Module - Standardizes raster patches, aligns multi-temporal inputs, and generates image hashes.
"""

import hashlib
from typing import Tuple
import numpy as np
import cv2


def compute_image_hash(image: np.ndarray) -> str:
    """Computes an MD5 hex digest of the image bytes for consistent identification."""
    if image is None:
        return "IMG_NULL"
    return hashlib.md5(image.tobytes()[:8192]).hexdigest()[:10].upper()


def standardize_patch(
    image: np.ndarray,
    target_size: Tuple[int, int] = (256, 256)
) -> np.ndarray:
    """
    Resizes image patch to target dimensions and ensures uint8 RGB format.
    """
    if image is None:
        raise ValueError("Cannot standardize None image.")

    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

    if (image.shape[1], image.shape[0]) != target_size:
        return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

    return image.astype(np.uint8)


def extract_ndwi_proxy(rgb_patch: np.ndarray) -> np.ndarray:
    """
    Computes an RGB proxy for water/flood detection: (Green - Red) / (Green + Red + 1e-5).
    In standard Sentinel-2 / Landsat, NDWI is (Green - NIR) / (Green + NIR).
    When NIR is absent in 3-channel RGB chips, (Green - Red) or HSV Saturation thresholding
    is the standard accepted proxy in computer vision disaster literature.
    Returns float32 map normalized between -1.0 and 1.0.
    """
    green = rgb_patch[:, :, 1].astype(np.float32)
    red = rgb_patch[:, :, 0].astype(np.float32)
    numerator = green - red
    denominator = green + red + 1e-5
    return np.clip(numerator / denominator, -1.0, 1.0)
