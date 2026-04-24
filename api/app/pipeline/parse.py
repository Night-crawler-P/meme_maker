from __future__ import annotations

from typing import Tuple
import io

import numpy as np
from PIL import Image


def parse_face_mask(photo_bytes: bytes, bbox_xywh: Tuple[int, int, int, int]) -> np.ndarray:
    """STUB face parsing.

    Replace with a face parsing model (e.g., BiSeNet-based) to get clean skin/hair boundaries.

    Returns a float mask in [0..1] with shape (H, W).
    """
    img = Image.open(io.BytesIO(photo_bytes)).convert("RGB")
    w, h = img.size

    x, y, bw, bh = bbox_xywh
    mask = np.zeros((h, w), dtype=np.float32)

    # simple ellipse inside bbox
    cy = y + bh * 0.52
    cx = x + bw * 0.50
    ry = bh * 0.48
    rx = bw * 0.42

    yy, xx = np.mgrid[0:h, 0:w]
    ell = (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2) <= 1.0
    mask[ell] = 1.0

    return mask
