from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from datetime import datetime
import os
import edge_tts

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
async def generate_video(data: VideoRequest):
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    audio_path = f"{FILES_DIR}/audio_{timestamp}.mp3"

    communicate = edge_tts.Communicate(
        text=data.script,
        voice="pt-BR-AntonioNeural"
    )

    await communicate.save(audio_path)

    return {
        "status": "success",
        "audio_file": audio_path
    }


@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(FILES_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return {
        "status": "uploaded",
        "filename": file.filename
    }


