from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import subprocess
import os

app = FastAPI()

@app.post("/video")
async def create_video(
    audio: UploadFile = File(...),
    image: UploadFile = File(...)
):
    uid = str(uuid.uuid4())

    audio_path = f"/tmp/{uid}.mp3"
    image_path = f"/tmp/{uid}.jpg"
    video_path = f"/tmp/{uid}.mp4"

    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    with open(image_path, "wb") as f:
        f.write(await image.read())

    command = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", image_path,
        "-i", audio_path,
        "-c:a", "aac",
        "-c:v", "libx264",
        "-shortest",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1080:1920",
        video_path
    ]

    subprocess.run(command, check=True)

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename="short.mp4"
    )
