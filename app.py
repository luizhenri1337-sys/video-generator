from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
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


@app.get("/audio/{filename}")
def get_audio(filename: str):
    file_path = os.path.join(FILES_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio not found")

    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename
    )


import subprocess


@app.post("/generate-video-mp4")
async def generate_video_mp4(data: VideoRequest):
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    audio_path = f"{FILES_DIR}/audio_{timestamp}.mp3"
    video_path = f"{FILES_DIR}/video_{timestamp}.mp4"

    # 1. Gerar áudio
    communicate = edge_tts.Communicate(
        text=data.script,
        voice="pt-BR-AntonioNeural"
    )
    await communicate.save(audio_path)

    # 2. Gerar vídeo simples com FFmpeg (fundo preto + áudio)
    command = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", "color=c=black:s=1080x1920",
        "-i", audio_path,
        "-shortest",
        "-c:v", "libx264",
        "-c:a", "aac",
        video_path
    ]

    subprocess.run(command, check=True)

    return {
        "status": "success",
        "video_file": video_path
    }
