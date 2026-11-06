import json

from langchain_core.tools import tool

from app.agent.overview import get_video_overview
from app.services import registry
from app.services.embeddings import embed_texts
from app.services.retrieval import refine_hit,retrieve
from app.services import vector_store
from app.utils import mmss


def get_title(video_id: str) -> str:
    rec = registry.get_video(video_id)
    return rec["title"] if rec else video_id


def build_tools(video_id: str, sink: list[dict]):
    seen: set[tuple[str, float]] = set()

    def record(hit: dict) -> None:
        key = (hit["video_id"], round(float(hit["start"]), 1))
        if key in seen:
            return
        seen.add(key)
        sink.append(
            {
                "video_id": hit["video_id"],
                "title": get_title(hit["video_id"]),
                "start": float(hit["start"]),
                "end": float(hit["end"]),
                "text": hit["text"],
            }
        )

    @tool
    def search_transcript(query: str) -> str:
        """Search the transcripts for passages relevant to a question. Use this for any question about what a video says."""
        hits = retrieve(query, top_k=4, video_id=video_id)
        if not hits:
            return "No relevant passages found."
        lines = []
        for h in hits:
            h = refine_hit(h, query)
            record(h)
            lines.append(f"[{mmss(h['start'])}] ({get_title(h['video_id'])}) {h['text']}")
        return "\n".join(lines)

    @tool
    def get_video_info() -> str:
        """Get the title, length, and caption source of this video."""
        rec = registry.get_video(video_id)
        if not rec:
            return "Video not found."
        return f"Title: {rec['title']}. Length: about {mmss(rec['duration_seconds'])}. Source: {rec['source']}."

    @tool
    def summarize_time_range(start_seconds: float, end_seconds: float) -> str:
        """Return the transcript between two timestamps, in seconds, of this video."""
        vector = embed_texts(["summary of the video"])[0]
        rows = vector_store.fetch_time_range(video_id, vector, start_seconds, end_seconds)
        if not rows:
            return "No transcript found in that range."
        for r in rows[:3]:
            record(r)
        return "\n".join(f"[{mmss(r['start'])}] {r['text']}" for r in rows)

    @tool
    def generate_video_overview() -> str:
        """Generate or retrieve this video's overview, chapters, and topic labels. Use for requests for an overall summary or chapter list."""
        try:
            return json.dumps(get_video_overview(video_id), ensure_ascii=False)
        except ValueError as exc:
            return f"Overview unavailable: {exc}"

    return [search_transcript, get_video_info, summarize_time_range, generate_video_overview]
