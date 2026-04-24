from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Tuple
import io

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Model weights are auto-downloaded on first run.
# Override via the INSIGHTFACE_HOME environment variable.
_INSIGHTFACE_CACHE = os.environ.get("INSIGHTFACE_HOME", "/tmp/insightface_cache")

_face_app = None
_face_app_init_error: Exception | None = None


def _get_face_app():
    """Lazily initialise insightface FaceAnalysis (downloads model on first call)."""
    global _face_app, _face_app_init_error
    if _face_app is not None:
        return _face_app
    if _face_app_init_error is not None:
        raise _face_app_init_error
    try:
        from insightface.app import FaceAnalysis  # type: ignore[import]

        app = FaceAnalysis(
            name="buffalo_sc",
            root=_INSIGHTFACE_CACHE,
            providers=["CPUExecutionProvider"],
        )
        app.prepare(ctx_id=-1, det_size=(640, 640))
        _face_app = app
        logger.info("insightface FaceAnalysis (buffalo_sc) initialised OK")
        return _face_app
    except Exception as exc:
        _face_app_init_error = exc
        logger.error("Failed to initialise insightface: %s", exc)
        raise


@dataclass
class DetectedFace:
    # Pixel coords in source image (observer's left/right convention)
    left_eye: Tuple[float, float]
    right_eye: Tuple[float, float]
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    score: float


def _pil_to_rgb_np(img_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(img)


def detect_primary_face(photo_bytes: bytes) -> DetectedFace:
    """Detect the primary face using insightface RetinaFace (ONNX, CPU).

    Model weights (~50 MB for buffalo_sc) are downloaded automatically on
    the first call to *INSIGHTFACE_HOME* (default: /tmp/insightface_cache).

    Landmark convention — observer's perspective (matches template anchors):
      kps[0] = left  eye (smaller x in a frontal image)
      kps[1] = right eye (larger  x in a frontal image)

    Returns:
        DetectedFace with accurate eye coordinates, bbox (x,y,w,h), and score.

    Raises:
        ValueError: if no face is found in the image.
    """
    rgb = _pil_to_rgb_np(photo_bytes)
    h, w = rgb.shape[:2]

    app = _get_face_app()
    faces = app.get(rgb)

    if not faces:
        raise ValueError("No face detected in the provided image")

    # Pick the highest-confidence face
    face = max(faces, key=lambda f: float(f.det_score))

    x1, y1, x2, y2 = (int(v) for v in face.bbox)
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    # kps shape: (5, 2) — observer's left/right convention
    # [0]=left eye, [1]=right eye, [2]=nose, [3]=left mouth, [4]=right mouth
    kps = face.kps
    left_eye = (float(kps[0][0]), float(kps[0][1]))
    right_eye = (float(kps[1][0]), float(kps[1][1]))

    return DetectedFace(
        left_eye=left_eye,
        right_eye=right_eye,
        bbox=(x1, y1, x2 - x1, y2 - y1),
        score=float(face.det_score),
    )
