"""
Image Loader Module - Safely retrieves and decodes visual imagery from local paths, URLs, and Base64.
"""

import os
import base64
import logging
from typing import Tuple, Optional
import numpy as np
import cv2

logger = logging.getLogger("drishtisetu.cv.loader")


class ImageLoadError(Exception):
    """Raised when an image cannot be retrieved or decoded."""
    pass


def load_image(image_source: str, max_dimension: int = 1024) -> Tuple[np.ndarray, str]:
    """
    Loads an image from a local path, URL, or base64 string, returning (image_rgb, source_type).
    Image returned is an RGB uint8 NumPy array of shape (H, W, 3).
    """
    if not image_source or not isinstance(image_source, str) or not image_source.strip():
        raise ImageLoadError("Empty or invalid image source provided.")

    source = image_source.strip()

    # 1. Base64 Data URI
    if source.startswith("data:image/") or ";base64," in source:
        try:
            _, b64data = source.split(";base64,", 1)
            raw_bytes = base64.b64decode(b64data)
            nparr = np.frombuffer(raw_bytes, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img_bgr is None:
                raise ImageLoadError("Failed to decode base64 image data.")
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            return _resize_if_needed(img_rgb, max_dimension), "base64"
        except Exception as e:
            raise ImageLoadError(f"Error decoding base64 image: {str(e)}")

    # 2. HTTP/HTTPS URL
    if source.startswith("http://") or source.startswith("https://"):
        try:
            import urllib.request
            req = urllib.request.Request(
                source,
                headers={"User-Agent": "DrishtiSetu-CV/2.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                raw_bytes = response.read()
            nparr = np.frombuffer(raw_bytes, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img_bgr is None:
                raise ImageLoadError(f"Failed to decode image from URL: {source}")
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            return _resize_if_needed(img_rgb, max_dimension), "url"
        except Exception as e:
            logger.warning(f"Could not download remote image '{source}': {e}. Falling back to virtual patch.")
            raise ImageLoadError(f"Failed to fetch image from URL: {source} ({e})")

    # 3. Local filesystem path
    # Check current directory and common project relative paths
    search_paths = [
        source,
        os.path.join(os.getcwd(), source),
        os.path.join(os.path.dirname(__file__), "..", source),
        os.path.join(os.path.dirname(__file__), "..", "demo_assets", os.path.basename(source))
    ]

    for path in search_paths:
        if os.path.isfile(path):
            img_bgr = cv2.imread(path, cv2.IMREAD_COLOR)
            if img_bgr is not None:
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                return _resize_if_needed(img_rgb, max_dimension), "local_file"

    # If file not found
    raise ImageLoadError(f"Local image file not found or could not be decoded: {source}")


def _resize_if_needed(img: np.ndarray, max_dim: int) -> np.ndarray:
    """Restricts max dimension to preserve memory and latency."""
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return img
