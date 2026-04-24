# meme_maker

AI meme maker: upload a friend's photo, pick a meme template, and generate a meme with their face.

## Monorepo layout
- `web/` Next.js website (UI + template anchoring)
- `api/` Python FastAPI renderer (detection + parsing + compositing)

## Quickstart (local)

### 1) API
```bash
cd api
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2) Web
```bash
cd web
npm install
npm run dev
```

Open http://localhost:3000

## Templates
Place template images in `web/public/templates/` and define anchors in `web/src/templates/index.json`.

## Notes
The API currently uses a **stub** face detector + mask generator so the pipeline works end-to-end.
Replace the stubs in `api/app/pipeline/*` with RetinaFace + face parsing models when you’re ready.
