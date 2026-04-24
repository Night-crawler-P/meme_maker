# API (FastAPI)

This service renders memes by compositing a detected face from an input image onto a template using template anchors.

## Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Quick start (Docker)

```bash
docker compose up --build
```

The API will be available at <http://localhost:8000>.

## Endpoints

| Method | Path      | Description                                      |
|--------|-----------|--------------------------------------------------|
| GET    | /healthz  | Liveness check                                   |
| POST   | /render   | Render a meme (multipart: `template_id`, `photo`) |

`POST /render` returns PNG bytes or:
- `400` — unsupported image type  
- `404` — unknown `template_id`  
- `422` — no face detected in the uploaded photo

## AI pipeline

### Face detection — insightface (RetinaFace via ONNX)

[insightface](https://github.com/deepinsight/insightface) is used for accurate face detection with 5-point landmarks (eyes, nose, mouth corners).  
Model weights (`buffalo_sc`, ~50 MB) are **downloaded automatically on the first request** from the insightface CDN.

**Cache location** (writable inside Docker): `/tmp/insightface_cache`  
Override with the `INSIGHTFACE_HOME` environment variable:

```bash
# docker-compose.yml or CLI
INSIGHTFACE_HOME=/path/to/cache uvicorn app.main:app ...
```

### Face mask generation — MediaPipe FaceMesh

[MediaPipe](https://google.github.io/mediapipe/) FaceMesh produces 468 face landmarks.  
The 36-point face-oval contour is filled into a polygon mask, expanded slightly to cover the hairline, and feathered with a Gaussian blur for smooth blending.  
**MediaPipe models are bundled with the Python package — no separate download required.**

### Fallback behaviour

If the primary detector fails to find a face the API returns HTTP **422**.  
If the mask generator fails (mediapipe unavailable), a feathered ellipse is used as a graceful fallback so the rest of the pipeline still runs.

## Pre-downloading model weights (optional, for air-gapped environments)

Run this once before starting the container (internet access required):

```bash
python - <<'EOF'
import os, insightface
from insightface.app import FaceAnalysis
cache = os.environ.get("INSIGHTFACE_HOME", "/tmp/insightface_cache")
app = FaceAnalysis(name="buffalo_sc", root=cache, providers=["CPUExecutionProvider"])
app.prepare(ctx_id=-1, det_size=(640, 640))
print("Models downloaded to", cache)
EOF
```

Then mount the cache directory into the container:

```yaml
# docker-compose.yml
services:
  api:
    volumes:
      - /tmp/insightface_cache:/tmp/insightface_cache
```

