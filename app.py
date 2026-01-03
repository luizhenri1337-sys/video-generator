from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from datetime import datetime
import os

app = FastAPI(title="Video Generator API")

FILES_DIR = "files"
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
    Stub inicial de geração de vídeo.
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"{FILES_DIR}/video_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Título: {data.title}\n\n")
        f.write(f"Roteiro:\n{data.script}\n")

    return {
        "status": "success",
        "file": filename
    }


@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    """
    Endpoint preparado para uploads (n8n, imagens, áudios).
    """
    file_path = os.path.join(FILES_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return {
        "status": "uploaded",
        "filename": file.filename
    }

