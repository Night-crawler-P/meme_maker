from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import io

import numpy as np
from PIL import Image


@dataclass
class DetectedFace:
    # Pixel coords in source image
    left_eye: Tuple[float, float]
    right_eye: Tuple[float, float]
    bbox: Tuple[int, int, int, int]  # x,y,w,h
    score: float


def _pil_to_rgb_np(img_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(img)


def detect_primary_face(photo_bytes: bytes) -> DetectedFace:
    """STUB detector.

    Replace with RetinaFace/YOLO-face.

    For now, we assume the face is near center and estimate eye points from the bbox.
    This keeps the end-to-end pipeline working.
    """
    rgb = _pil_to_rgb_np(photo_bytes)
    h, w = rgb.shape[:2]

    # center-ish box
    bw = int(w * 0.45)
    bh = int(h * 0.45)
    x = (w - bw) // 2
    y = (h - bh) // 3

    left_eye = (x + bw * 0.33, y + bh * 0.40)
    right_eye = (x + bw * 0.67, y + bh * 0.40)

    return DetectedFace(
        left_eye=left_eye,
        right_eye=right_eye,
        bbox=(x, y, bw, bh),
        score=0.5,
    )
