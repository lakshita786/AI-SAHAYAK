"""
SabbiAI - AI Livelihood Assistant for Rural Indian Workers
FastAPI server connecting UI to Python backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
from backend.agent import run_agent
from backend.schemes_db import search_schemes, load_schemes
from backend.automl_model import get_eligibility_summary
from backend.nlp_classifier import get_intent

load_dotenv()
app = FastAPI(title="SabbiAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="UI"), name="static")


class ChatRequest(BaseModel):
    message: str
    history: Optional[List] = []
    user_profile: Optional[dict] = None


class EligibilityRequest(BaseModel):
    age: int
    monthly_income: float
    occupation: str
    state: str
    family_size: Optional[int] = 4


@app.get("/")
def home():
    return FileResponse("UI/ai_sahayak_home_screen/code.html")


@app.get("/eligibility")
def eligibility_page():
    return FileResponse("UI/check_eligibility_form/code.html")


@app.get("/schemes")
def schemes_page():
    return FileResponse("UI/scheme_recommendations/code.html")


@app.get("/support")
def support_page():
    return FileResponse("UI/support/code.html")


@app.get("/about")
def about_page():
    return FileResponse("UI/about/code.html")


@app.get("/health")
def health():
    return {"status": "ok", "app": "SabbiAI"}


@app.post("/api/chat")
def chat(req: ChatRequest):
    result = run_agent(
        user_message=req.message,
        user_profile=req.user_profile,
        conversation_history=req.history,
    )
    return result


@app.post("/api/eligibility")
def check_eligibility(req: EligibilityRequest):
    result = get_eligibility_summary(
        age=req.age,
        monthly_income=req.monthly_income,
        occupation=req.occupation,
        state=req.state,
        family_size=req.family_size or 4,
    )
    return result


@app.get("/api/schemes/all")
def all_schemes():
    schemes = load_schemes()
    return {"schemes": schemes}


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "hi-IN-SwaraNeural"
    rate: Optional[str] = "+0%"


@app.post("/api/tts")
async def text_to_speech(req: TTSRequest):
    from backend.speech_api import generate_speech_async, VOICE_HINDI_FEMALE

    voice = req.voice if req.voice else VOICE_HINDI_FEMALE
    audio = await generate_speech_async(req.text, voice, req.rate or "+0%")

    return Response(
        content=audio,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"inline; filename=speech.mp3"},
    )


@app.get("/api/tts/{filename}")
async def get_tts_audio(filename: str):
    from backend.speech_api import TEMP_DIR

    filepath = TEMP_DIR / filename
    if filepath.exists():
        return FileResponse(str(filepath), media_type="audio/mpeg")
    return {"error": "File not found"}


if __name__ == "__main__":
    print("=" * 50)
    print("🌾 SabbiAI - AI Livelihood Assistant")
    print("=" * 50)
    print("🌾 SabbiAI running at http://localhost:8000")
    print("   Home:       http://localhost:8000")
    print("   Eligibility: http://localhost:8000/eligibility")
    print("   Schemes:    http://localhost:8000/schemes")
    print("   Support:    http://localhost:8000/support")
    print("   About:      http://localhost:8000/about")
    print("   API Docs:   http://localhost:8000/docs")
    print("=" * 50)
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
