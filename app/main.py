from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent.agent import run_agent
from app.agent.memory import add_turn, get_history
from app.config import CORS_ORIGINS
from app.services import registry
from app.services.ingest import ingest_video
from app.services import vector_store
from app.services.audio import transcribe_bytes
from app.services.transcripts import (
    TranscriptAccessBlocked,
    TranscriptRetrievalError,
)

app = FastAPI(title="YouTube QA API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IngestRequest(BaseModel):
    url: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
    video_id: str | None = None


class Citation(BaseModel):
    video_id: str
    title: str
    start: float
    end: float
    text: str

    
class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]


@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/videos")
def list_videos():
    return registry.list_videos()

@app.post("/api/videos")
def add_video(req: IngestRequest):
    try:
        return ingest_video(req.url)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    except TranscriptAccessBlocked as exc:
        raise HTTPException(503, str(exc))
    except TranscriptRetrievalError as exc:
        raise HTTPException(502, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"Ingestion failed: {exc}")

@app.delete("/api/videos/{video_id}")
def remove_video(video_id: str):
    if not registry.get_video(video_id):
        raise HTTPException(404, "Video not found")
    vector_store.delete_video(video_id)
    registry.remove_video(video_id)
    return {"deleted": video_id}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    history = get_history(req.session_id)
    sink: list[dict] = []
    try:
        answer = run_agent(req.message, history, req.video_id, sink)
    except Exception as exc:
        raise HTTPException(502, f"Agent error: {exc}")
    add_turn(req.session_id, req.message, answer)
    return ChatResponse(answer=answer, citations=[Citation(**c) for c in sink])

@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    data = await file.read()
    try:
        result = transcribe_bytes(data, file.filename or "question.webm")
    except ValueError as exc:
        raise HTTPException(413, str(exc))
    except Exception as exc:
        raise HTTPException(502, f"Transcription failed: {exc}")
    return {"text": result["text"]}