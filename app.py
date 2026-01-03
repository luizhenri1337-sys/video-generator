from fastapi import FastAPI
from pydantic import BaseModel
import edge_tts
import uuid
import os

app = FastAPI()

# Pasta pública para arquivos
FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

class TTSRequest(BaseModel):
    text: str

@app.post("/tts")
async def text_to_speech(req: TTSRequest):
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(FILES_DIR, filename)

    communicate = edge_tts.Communicate(
        text=req.text,
        voice="pt-BR-FranciscaNeural",
        rate="-10%",
        volume="+0%"
    )

    await communicate.save(filepath)

    return {
        "status": "ok",
        "audio_url": f"/files/{filename}"
    }

