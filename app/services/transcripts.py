import re
from youtube_transcript_api import YouTubeTranscriptApi
from app.config import CHUNK_SECONDS, TRANSCRIPT_LANGUAGES

class TranscriptUnavailable(Exception):
    """The video has no usable captions. Ingestion falls back to Whisper."""

def extract_video_id(url_or_id: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})", url_or_id)
    if match:
        return match.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id.strip()):
        return url_or_id.strip()
    raise ValueError(f"Could not find a YouTube video ID in: {url_or_id}")


def fetch_caption_segments(video_id: str) -> list[dict]:
    try:
        fetched = YouTubeTranscriptApi().fetch(video_id, languages=list(TRANSCRIPT_LANGUAGES))
    except Exception as exc:
        raise TranscriptUnavailable(str(exc)) from exc
    snippets = fetched.snippets if hasattr(fetched, "snippets") else list(fetched)
    return [{"text": s.text, "start": s.start, "end": s.start + s.duration} for s in snippets]


def chunk_segments(segments: list[dict], target_seconds: int = CHUNK_SECONDS) -> list[dict]:
    chunks, current, start, end = [], [], None, 0.0
    for seg in segments:
        if start is None:
            start = seg["start"]
        current.append(seg["text"].strip())
        end = seg["end"]
        if end - start >= target_seconds:
            chunks.append({"text": " ".join(current), "start": start, "end": end})
            current, start = [], None
    if current:
        chunks.append({"text": " ".join(current), "start": start, "end": end})
    return chunks
