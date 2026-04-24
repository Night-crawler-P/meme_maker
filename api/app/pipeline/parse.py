from __future__ import annotations

import logging
from typing import Tuple
import io

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Ordered face-oval landmark indices (clockwise from top-centre).
# Derived from mediapipe FACEMESH_FACE_OVAL connection set.
_FACE_OVAL_INDICES = [
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
    397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
    172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109,
]

_mp_face_mesh_module = None


def _get_mp_face_mesh():
    """Lazily import mediapipe (models are bundled — no download needed)."""
    global _mp_face_mesh_module
    if _mp_face_mesh_module is None:
        import mediapipe as mp  # type: ignore[import]
        _mp_face_mesh_module = mp.solutions.face_mesh
    return _mp_face_mesh_module


def _ellipse_fallback(h: int, w: int, bbox_xywh: Tuple[int, int, int, int]) -> np.ndarray:
    """Fallback: soft ellipse inside the detected bbox."""
    x, y, bw, bh = bbox_xywh
    mask = np.zeros((h, w), dtype=np.float32)
    cy = y + bh * 0.52
    cx = x + bw * 0.50
    ry = bh * 0.48
    rx = bw * 0.42
    yy, xx = np.mgrid[0:h, 0:w]
    ell = (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2) <= 1.0
    mask[ell] = 1.0
    # Light feathering even for the fallback
    k = max(1, (min(bw, bh) // 20) * 2 + 1)
    mask = cv2.GaussianBlur(mask, (k, k), 0)
    return mask


def parse_face_mask(photo_bytes: bytes, bbox_xywh: Tuple[int, int, int, int]) -> np.ndarray:
    """Generate a soft face alpha mask using MediaPipe FaceMesh landmarks.

    Builds a polygon from the 36 face-oval landmarks, optionally expands it
    upward to include the hairline, then applies a Gaussian blur for smooth
    blending edges.

    Falls back to a feathered ellipse mask if landmark detection fails.

    Returns:
        float32 ndarray of shape (H, W) with values in [0, 1].
    """
    img = Image.open(io.BytesIO(photo_bytes)).convert("RGB")
    w, h = img.size
    rgb_np = np.array(img)

    x, y, bw, bh = bbox_xywh

    try:
        mp_face_mesh = _get_mp_face_mesh()
        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.3,
        ) as face_mesh:
            results = face_mesh.process(rgb_np)
    except Exception as exc:
        logger.warning("MediaPipe FaceMesh failed, using ellipse fallback: %s", exc)
        return _ellipse_fallback(h, w, bbox_xywh)

    if not results.multi_face_landmarks:
        logger.debug("No face landmarks from MediaPipe, using ellipse fallback")
        return _ellipse_fallback(h, w, bbox_xywh)

    landmarks = results.multi_face_landmarks[0].landmark

    # Build ordered polygon from face-oval landmarks
    points = np.array(
        [[int(landmarks[i].x * w), int(landmarks[i].y * h)] for i in _FACE_OVAL_INDICES],
        dtype=np.int32,
    )

    # Expand upper points upward to include the hairline (~15% of bbox height)
    hair_expand = max(1, int(bh * 0.15))
    cy_oval = float(points[:, 1].mean())
    for pt in points:
        if pt[1] < cy_oval:
            pt[1] = max(0, pt[1] - hair_expand)

    # Rasterise polygon
    mask = np.zeros((h, w), dtype=np.float32)
    cv2.fillPoly(mask, [points], 1.0)

    # Gaussian feathering proportional to face size
    blur_k = max(1, (min(bw, bh) // 20) * 2 + 1)
    mask = cv2.GaussianBlur(mask, (blur_k, blur_k), 0)

    return mask
