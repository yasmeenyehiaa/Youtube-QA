from pinecone import Pinecone, ServerlessSpec
from app.config import (
    NAMESPACE_PREFIX,
    OPENAI_EMBED_DIM,
    PINECONE_API_KEY,
    PINECONE_CLOUD,
    PINECONE_INDEX_NAME,
    PINECONE_REGION,
)

index = None

def get_index():
    global index
    if index is None:
        if not PINECONE_API_KEY:
            raise RuntimeError("PINECONE_API_KEY is not set. Add it to .env")
        pc = Pinecone(api_key=PINECONE_API_KEY)
        if not pc.has_index(PINECONE_INDEX_NAME):
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=OPENAI_EMBED_DIM,
                metric="cosine",
                spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
            )
        index = pc.Index(PINECONE_INDEX_NAME)
    return index

def namespace_for(video_id: str) -> str:
    return f"{NAMESPACE_PREFIX}{video_id}"

def replace_video(video_id: str, chunks: list[dict], embeddings: list[list[float]]) -> int:
    index = get_index()
    ns = namespace_for(video_id)
    try:
        index.delete(delete_all=True, namespace=ns)
    except Exception:
        pass  # namespace did not exist yet

    vectors = [
        {
            "id": f"{i:05d}",
            "values": emb,
            "metadata": {
                "video_id": video_id,
                "start": float(c["start"]),
                "end": float(c["end"]),
                "text": c["text"],
            },
        }
        for i, (c, emb) in enumerate(zip(chunks, embeddings))
    ]
    for i in range(0, len(vectors), 100):
        index.upsert(vectors=vectors[i : i + 100], namespace=ns)
    return len(vectors)

def delete_video(video_id: str) -> None:
    try:
        get_index().delete(delete_all=True, namespace=namespace_for(video_id))
    except Exception:
        pass

def list_video_namespaces() -> list[str]:
    stats = get_index().describe_index_stats()
    return [ns for ns in stats.namespaces if ns.startswith(NAMESPACE_PREFIX)]


def query(vector: list[float], top_k: int = 4, video_id: str | None = None) -> list[dict]:
    index = get_index()
    namespaces = [namespace_for(video_id)] if video_id else list_video_namespaces()
    hits = []
    for ns in namespaces:
        res = index.query(vector=vector, top_k=top_k, namespace=ns, include_metadata=True)
        hits.extend({"score": m.score, **(m.metadata or {})} for m in res.matches)
    hits.sort(key=lambda h: h["score"], reverse=True)
    return hits[:top_k]


def fetch_time_range(video_id: str, vector: list[float], start_gte: float, start_lte: float, limit: int = 200) -> list[dict]:
    res = get_index().query(
        vector=vector,
        top_k=limit,
        namespace=namespace_for(video_id),
        include_metadata=True,
        filter={"start": {"$gte": start_gte, "$lte": start_lte}},
    )
    rows = [dict(m.metadata or {}) for m in res.matches]
    return sorted(rows, key=lambda r: r["start"])

