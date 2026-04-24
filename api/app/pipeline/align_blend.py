from __future__ import annotations

from typing import Tuple
import io

import cv2
import numpy as np
from PIL import Image


def _pil_to_bgr(img: Image.Image) -> np.ndarray:
    rgb = np.array(img.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def _bgr_to_png_bytes(bgr: np.ndarray) -> bytes:
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def estimate_affine_from_eyes(
    src_left_eye: Tuple[float, float],
    src_right_eye: Tuple[float, float],
    dst_left_eye: Tuple[float, float],
    dst_right_eye: Tuple[float, float],
):
    src = np.array([src_left_eye, src_right_eye], dtype=np.float32)
    dst = np.array([dst_left_eye, dst_right_eye], dtype=np.float32)

    # Need 3 points for full affine. Create a synthetic third point using perpendicular direction.
    def third_point(a, b):
        v = b - a
        perp = np.array([-v[1], v[0]], dtype=np.float32)
        return a + perp

    src3 = np.vstack([src, third_point(src[0], src[1])])
    dst3 = np.vstack([dst, third_point(dst[0], dst[1])])

    M = cv2.getAffineTransform(src3, dst3)
    return M


def warp_overlay(
    src_bgr: np.ndarray,
    src_mask: np.ndarray,
    M: np.ndarray,
    out_size_wh: Tuple[int, int],
):
    out_w, out_h = out_size_wh
    warped = cv2.warpAffine(src_bgr, M, (out_w, out_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)
    warped_mask = cv2.warpAffine(src_mask, M, (out_w, out_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    warped_mask = np.clip(warped_mask, 0.0, 1.0)
    return warped, warped_mask


def feather_blend(base_bgr: np.ndarray, overlay_bgr: np.ndarray, overlay_mask: np.ndarray, feather_px: int = 14):
    m = (overlay_mask * 255).astype(np.uint8)
    if feather_px > 0:
        k = max(1, feather_px // 2 * 2 + 1)
        m = cv2.GaussianBlur(m, (k, k), 0)
    alpha = (m.astype(np.float32) / 255.0)[..., None]

    out = (overlay_bgr.astype(np.float32) * alpha + base_bgr.astype(np.float32) * (1.0 - alpha)).astype(np.uint8)
    return out


def seamless_clone(base_bgr: np.ndarray, overlay_bgr: np.ndarray, overlay_mask: np.ndarray):
    mask_u8 = (np.clip(overlay_mask, 0.0, 1.0) * 255).astype(np.uint8)
    if mask_u8.max() == 0:
        return base_bgr

    ys, xs = np.where(mask_u8 > 0)
    center = (int(xs.mean()), int(ys.mean()))
    return cv2.seamlessClone(overlay_bgr, base_bgr, mask_u8, center, cv2.NORMAL_CLONE)


def load_template_bgr(template_path: str) -> np.ndarray:
    img = Image.open(template_path).convert("RGB")
    return _pil_to_bgr(img)


def photo_bytes_to_bgr(photo_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(photo_bytes)).convert("RGB")
    return _pil_to_bgr(img)


def to_png_bytes(bgr: np.ndarray) -> bytes:
    return _bgr_to_png_bytes(bgr)
