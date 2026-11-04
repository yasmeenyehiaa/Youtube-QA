from app.config import RETRIEVAL_MIN_SCORE
from app.services import vector_store
from app.services.embeddings import embed_texts


def retrieve(question: str, top_k: int = 4, video_id: str | None = None) -> list[dict]:
    vector = embed_texts([question])[0]
    hits = vector_store.query(vector, top_k=top_k, video_id=video_id)
    return [h for h in hits if h["score"] >= RETRIEVAL_MIN_SCORE]
