import json

from langchain_core.tools import tool

from app.agent.overview import get_video_overview
from app.services import registry
from app.services.embeddings import embed_texts
from app.services.retrieval import refine_hits, retrieve_many
from app.services import vector_store
from app.utils import mmss

MAX_QUERY_VARIANTS = 2
MAX_CITATIONS = 2


def get_title(video_id: str) -> str:
    rec = registry.get_video(video_id)
    return rec["title"] if rec else video_id


def build_tools(video_id: str, sink: list[dict], original_query: str):
    seen: set[tuple[str, float]] = set()

    def record(hit: dict) -> None:
        key = (hit["video_id"], round(float(hit["start"]), 1))
        if key in seen or len(sink) >= MAX_CITATIONS:
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
    def search_transcript(query_variants: list[str] | None = None) -> str:
        """Search transcript passages using the original question and equivalent phrasings.

        Args:
            query_variants: Up to two concise alternative phrasings. Preserve the user's
                intent and entities, using useful synonyms or transcript wording. Do not
                include an answer.
        """
        queries = [original_query]
        known_queries = {original_query.strip().casefold()}
        for variant in query_variants or []:
            variant = variant.strip()
            normalized = variant.casefold()
            if variant and normalized not in known_queries:
                queries.append(variant)
                known_queries.add(normalized)
            if len(queries) >= MAX_QUERY_VARIANTS + 1:
                break

        query_hits = retrieve_many(queries, top_k=4, video_id=video_id)
        hits_and_queries = [
            (hit, search_query)
            for search_query, hits in zip(queries, query_hits)
            for hit in hits
        ]
        refined_hits = refine_hits(hits_and_queries)

        unique_hits: dict[tuple[str, float], tuple[str, dict]] = {}
        for (original_hit, search_query), refined_hit in zip(
            hits_and_queries,
            refined_hits,
        ):
            hit = {**original_hit, **refined_hit}
            hit["score"] = hit.get("segment_score", original_hit["score"])
            key = (hit["video_id"], round(float(hit["start"]), 1))
            previous = unique_hits.get(key)
            if previous is None or hit["score"] > previous[1]["score"]:
                unique_hits[key] = (search_query, hit)

        if not unique_hits:
            return "No relevant passages found."

        selected_hits = sorted(
            unique_hits.values(),
            key=lambda item: item[1]["score"],
            reverse=True,
        )[:MAX_CITATIONS]

        lines = []
        for search_query, hit in selected_hits:
            record(hit)
            lines.append(
                f"[{mmss(hit['start'])}] ({get_title(hit['video_id'])}) "
                f"{hit['text']} (matched query: {search_query})"
            )
        return "Top matching transcript passages, ordered by relevance:\n" + "\n".join(lines)

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

        segments_by_key: dict[tuple[float, str], dict] = {}
        for row in rows:
            segments = json.loads(row.get("segments") or "[]")
            if not segments:
                segments = [row]
            for segment in segments:
                segment_start = float(segment["start"])
                segment_end = float(segment["end"])
                if segment_end <= start_seconds or segment_start >= end_seconds:
                    continue
                selected = {
                    "video_id": video_id,
                    "start": segment_start,
                    "end": segment_end,
                    "text": segment["text"],
                }
                segments_by_key[(segment_start, segment["text"])] = selected

        selected_segments = sorted(
            segments_by_key.values(),
            key=lambda segment: segment["start"],
        )
        if not selected_segments:
            return "No transcript found in that range."

        citation_positions = (
            [
                round(index * (len(selected_segments) - 1) / (MAX_CITATIONS - 1))
                for index in range(MAX_CITATIONS)
            ]
            if len(selected_segments) > MAX_CITATIONS
            else range(len(selected_segments))
        )
        for position in citation_positions:
            segment = selected_segments[position]
            record(segment)
        return "\n".join(
            f"[{mmss(segment['start'])}] {segment['text']}"
            for segment in selected_segments
        )

    @tool
    def generate_video_overview() -> str:
        """Generate or retrieve this video's overview, chapters, and topic labels. Use for requests for an overall summary or chapter list."""
        try:
            return json.dumps(get_video_overview(video_id), ensure_ascii=False)
        except ValueError as exc:
            return f"Overview unavailable: {exc}"

    return [search_transcript, get_video_info, summarize_time_range, generate_video_overview]
