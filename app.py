from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import os
import subprocess
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


@app.post("/generate-video-mp4")
async def generate_video_mp4(data: VideoRequest):
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    audio_path = f"{FILES_DIR}/audio_{timestamp}.mp3"
    video_path = f"{FILES_DIR}/video_{timestamp}.mp4"

    # Gerar áudio
    communicate = edge_tts.Communicate(
        text=data.script,
        voice="pt-BR-AntonioNeural"
    )
    await communicate.save(audio_path)

    # Sanitizar texto para FFmpeg
    safe_title = data.title.replace("'", "").replace(":", "")

    # Gerar vídeo com imagem + texto + áudio
    command = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", f"{FILES_DIR}/background.jpg",
        "-i", audio_path,
        "-shortest",
        "-vf",
        f"scale=1080:1920,drawtext=text='{safe_title}':fontcolor=white:fontsize=64:x=(w-text_w)/2:y=150",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        video_path
    ]

    subprocess.run(command, check=True)

    return {
        "status": "success",
        "video_file": video_path
    }


@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = os.path.join(FILES_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=filename
    )
