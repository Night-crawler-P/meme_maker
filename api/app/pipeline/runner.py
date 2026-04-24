from __future__ import annotations

from ..templates import MemeTemplate
from .detect import detect_primary_face
from .parse import parse_face_mask
from .align_blend import (
    estimate_affine_from_eyes,
    warp_overlay,
    feather_blend,
    seamless_clone,
    load_template_bgr,
    photo_bytes_to_bgr,
    to_png_bytes,
)


def run_pipeline(template: MemeTemplate, photo_bytes: bytes) -> bytes:
    base = load_template_bgr(template.template_path)
    src = photo_bytes_to_bgr(photo_bytes)

    det = detect_primary_face(photo_bytes)
    mask = parse_face_mask(photo_bytes, det.bbox)

    out_h, out_w = base.shape[:2]

    M = estimate_affine_from_eyes(
        src_left_eye=det.left_eye,
        src_right_eye=det.right_eye,
        dst_left_eye=(template.target.left_eye["x"], template.target.left_eye["y"]),
        dst_right_eye=(template.target.right_eye["x"], template.target.right_eye["y"]),
    )

    overlay, overlay_mask = warp_overlay(
        src_bgr=src,
        src_mask=mask,
        M=M,
        out_size_wh=(out_w, out_h),
    )

    if template.target.blend_mode == "seamlessClone":
        out = seamless_clone(base, overlay, overlay_mask)
    else:
        out = feather_blend(base, overlay, overlay_mask, feather_px=template.target.feather_px)

    return to_png_bytes(out)
