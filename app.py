from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import os

app = FastAPI(title="Video Generator API")

FILES_DIR = "files"

# Garante que a pasta existe (importante no deploy)
os.makedirs(FILES_DIR, exist_ok=True)


class VideoRequest(BaseModel):
    title: str
    script: str


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Video Generator API running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/generate-video")
def generate_video(data: VideoRequest):
    """
    Endpoint inicial (stub).
    No futuro:
    - gerar roteiro
    - gerar áudio
    - gerar imagens
    - montar vídeo
    """

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"{FILES_DIR}/video_{timestamp}.txt"

    # Simula geração de conteúdo
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Título: {data.title}\n\n")
        f.write(f"Roteiro:\n{data.script}\n")

    return {
        "status": "success",
        "message": "Video generation started",
        "file": filename
    }
