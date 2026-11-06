import re
import json

from youtube_transcript_api import (
    NoTranscriptFound,
    RequestBlocked,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
    YouTubeTranscriptApiException,
)
from app.config import CHUNK_SECONDS, TRANSCRIPT_LANGUAGES

class TranscriptUnavailable(Exception):
    """The video has no usable captions, so ingestion can fall back to audio."""


class TranscriptAccessBlocked(Exception):
    """YouTube blocked caption retrieval from this server."""


class TranscriptRetrievalError(Exception):
    """Caption retrieval failed for a reason other than missing captions."""


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
    except RequestBlocked as exc:
        raise TranscriptAccessBlocked(
            "YouTube blocked caption requests from this server. "
            "Try again later, or provide an authorized transcript or audio source."
        ) from exc
    except (NoTranscriptFound, TranscriptsDisabled) as exc:
        raise TranscriptUnavailable(str(exc)) from exc
    except YouTubeTranscriptApiException as exc:
        raise TranscriptRetrievalError(f"Could not retrieve YouTube captions: {exc}") from exc
    snippets = fetched.snippets if hasattr(fetched, "snippets") else list(fetched)
    return [{"text": s.text, "start": s.start, "end": s.start + s.duration} for s in snippets]

def chunk_segments(segments: list[dict], window: float = CHUNK_SECONDS, overlap: float = 5) -> list[dict]:
    if not segments:
        return []
    video_end = segments[-1]["end"]
    chunks, t = [], segments[0]["start"]
    while t < video_end:
        inside = [s for s in segments if s["end"] > t and s["start"] < t + window]
        if inside:
            chunks.append({
                "text": " ".join(s["text"].strip() for s in inside),
                "start": inside[0]["start"],
                "end": inside[-1]["end"],
                "segments": json.dumps([
                    {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
                    for s in inside
                ]),
            })
        t += window - overlap
    return chunks
