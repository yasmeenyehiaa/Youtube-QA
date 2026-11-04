from app.config import OPENAI_EMBED_MODEL
from app.services.clients import get_openai

def embed_texts(texts: list[str]) -> list[list[float]]:
    vectors: list[list[float]] = []
    for i in range(0, len(texts), 256):
        resp = get_openai().embeddings.create(model=OPENAI_EMBED_MODEL, input=texts[i : i + 256])
        vectors.extend(item.embedding for item in resp.data)
    return vectors