from concurrent.futures import ThreadPoolExecutor
import json

from app.config import RETRIEVAL_MIN_SCORE
from app.services import vector_store
from app.services.embeddings import embed_texts


def retrieve(question: str, top_k: int = 4, video_id: str | None = None) -> list[dict]:
    vector = embed_texts([question])[0]
    hits = vector_store.query(vector, top_k=top_k, video_id=video_id)
    return [h for h in hits if h["score"] >= RETRIEVAL_MIN_SCORE]


def retrieve_many(
    questions: list[str],
    top_k: int = 4,
    video_id: str | None = None,
) -> list[list[dict]]:
    if not questions:
        return []

    vectors = embed_texts(questions)

    def query_vector(vector: list[float]) -> list[dict]:
        hits = vector_store.query(vector, top_k=top_k, video_id=video_id)
        return [hit for hit in hits if hit["score"] >= RETRIEVAL_MIN_SCORE]

    with ThreadPoolExecutor(max_workers=min(len(vectors), 4)) as executor:
        return list(executor.map(query_vector, vectors))


def refine_hit(hit: dict, question: str) -> dict:
    """Move start and end to the single line that best matches the question."""
    segs = json.loads(hit.get("segments") or "[]")
    if len(segs) < 2:
        return hit  # old vectors or a single line: nothing to refine

    vectors = embed_texts([question] + [s["text"] for s in segs])
    q, lines = vectors[0], vectors[1:]
    scores = [sum(a * b for a, b in zip(q, v)) for v in lines]  # unit vectors: dot = cosine
    best = segs[max(range(len(scores)), key=scores.__getitem__)]
    return {**hit, "start": best["start"], "end": best["end"]}


def refine_hits(hits_and_questions: list[tuple[dict, str]]) -> list[dict]:
    """Refine multiple hits in one embeddings request."""
    refined_hits = [hit for hit, _ in hits_and_questions]
    batches: list[tuple[int, list[dict], int]] = []
    texts: list[str] = []

    for index, (hit, question) in enumerate(hits_and_questions):
        segments = json.loads(hit.get("segments") or "[]")
        if len(segments) < 2:
            continue
        query_index = len(texts)
        texts.extend([question, *(segment["text"] for segment in segments)])
        batches.append((index, segments, query_index))

    if not batches:
        return refined_hits

    embeddings = embed_texts(texts)
    for index, segments, query_index in batches:
        query_vector = embeddings[query_index]
        segment_vectors = embeddings[query_index + 1 : query_index + 1 + len(segments)]
        scores = [
            sum(a * b for a, b in zip(query_vector, vector))
            for vector in segment_vectors
        ]
        best_index = max(range(len(scores)), key=scores.__getitem__)
        best = segments[best_index]
        refined_hits[index] = {
            **refined_hits[index],
            "start": best["start"],
            "end": best["end"],
            "segment_score": scores[best_index],
        }

    return refined_hits