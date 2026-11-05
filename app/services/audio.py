
import shutil
import tempfile
from pathlib import Path

from yt_dlp import YoutubeDL

from app.config import OPENAI_STT_MODEL, WHISPER_MAX_BYTES
from app.services.clients import get_openai


def _get(obj, key):
    return obj[key] if isinstance(obj, dict) else getattr(obj, key)


def transcribe_bytes(data: bytes, filename: str) -> dict:
    """Returns {"text": str, "segments": [{"text", "start", "end"}]}."""
    if len(data) > WHISPER_MAX_BYTES:
        raise ValueError("Audio is larger than 24 MB, the Whisper API upload limit.")
    resp = get_openai().audio.transcriptions.create(
        model=OPENAI_STT_MODEL,
        file=(filename, data),
        response_format="verbose_json",
    )
    raw_segments = getattr(resp, "segments", None) or []
    segments = [
        {"text": _get(s, "text"), "start": float(_get(s, "start")), "end": float(_get(s, "end"))}
        for s in raw_segments
    ]
    return {"text": resp.text, "segments": segments}


def transcribe_video_audio(video_id: str) -> list[dict]:
    """Download a video's audio, transcribe it with Whisper, and return segments."""
    workdir = Path(tempfile.mkdtemp(prefix="yt-audio-"))
    try:
        opts = {
            "format": "bestaudio[abr<=64]/bestaudio",
            "outtmpl": str(workdir / "%(id)s.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
        }
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
            path = Path(ydl.prepare_filename(info))
        return transcribe_bytes(path.read_bytes(), path.name)["segments"]
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
