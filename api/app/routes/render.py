from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response

from ..templates import load_template
from ..pipeline.runner import run_pipeline

router = APIRouter()

@router.post("/render")
async def render(
    template_id: str = Form(...),
    photo: UploadFile = File(...),
):
    if photo.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=400, detail="Unsupported image type")

    template = load_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Unknown template_id")

    img_bytes = await photo.read()
    out_png = run_pipeline(template=template, photo_bytes=img_bytes)

    return Response(content=out_png, media_type="image/png")
