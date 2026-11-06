import logging

import httpx
from app.services import registry
from app.services.audio import transcribe_video_audio
from app.services.embeddings import embed_texts
from app.services.transcripts import (
    chunk_segments,
    extract_video_id,
    fetch_caption_segments,
)
from app.services.vector_store import replace_video

logger = logging.getLogger(__name__)


def fetch_title(video_id: str) -> str:
    try:
        resp = httpx.get(
            "https://www.youtube.com/oembed",
            params={"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get("title", video_id)
    except Exception:
        return video_id

def ingest_video(url_or_id: str) -> dict:
    """Ingest a video into the vector store."""
    video_id = extract_video_id(url_or_id)
    try:
        segments = fetch_caption_segments(video_id)
        source = "captions"
    except Exception:
        logger.warning(
            "Caption retrieval failed for video %s; falling back to audio transcription.",
            video_id,
            exc_info=True,
        )
        segments = transcribe_video_audio(video_id)
        source = "whisper"

    chunks = chunk_segments(segments)
    if not chunks:
        raise ValueError("No speech found in this video.")

    embeddings = embed_texts([c["text"] for c in chunks])
    replace_video(video_id, chunks, embeddings)

    record = {
        "video_id": video_id,
        "title": fetch_title(video_id),
        "source": source,
        "chunks": len(chunks),
        "duration_seconds": max(c["end"] for c in chunks),
    }

    registry.put_video(record)
    return record