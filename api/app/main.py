from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import health, render

app = FastAPI(title="meme_maker API", version="0.1.0")

# Dev-friendly CORS (tighten for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)

app.include_router(health.router)
app.include_router(render.router)
