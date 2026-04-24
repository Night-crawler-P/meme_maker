# API (FastAPI)

This service renders memes by compositing a detected face from an input image onto a template using template anchors.

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Endpoints
- `GET /healthz`
- `POST /render` multipart form:
  - `template_id`: string
  - `photo`: file

Returns PNG bytes.

## Implementation notes
`app/pipeline/detect.py` and `app/pipeline/parse.py` currently contain **stub implementations** so you can ship the web UI and the full pipeline first.
Swap them with RetinaFace + face parsing later.
