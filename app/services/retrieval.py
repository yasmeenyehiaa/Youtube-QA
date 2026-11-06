import json
from app.config import RETRIEVAL_MIN_SCORE
from app.services import vector_store
from app.services.embeddings import embed_texts


def retrieve(question: str, top_k: int = 4, video_id: str | None = None) -> list[dict]:
    vector = embed_texts([question])[0]
    hits = vector_store.query(vector, top_k=top_k, video_id=video_id)
    return [h for h in hits if h["score"] >= RETRIEVAL_MIN_SCORE]

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