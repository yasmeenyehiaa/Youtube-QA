import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
OPENAI_EMBED_DIM = 1536
OPENAI_STT_MODEL = os.getenv("OPENAI_STT_MODEL", "whisper-1")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "youtube-qa")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
NAMESPACE_PREFIX = "video-"

CHUNK_SECONDS = 45
TRANSCRIPT_LANGUAGES = ("en",)
RETRIEVAL_MIN_SCORE = float(os.getenv("RETRIEVAL_MIN_SCORE", "0.25"))
MAX_HISTORY_TURNS = 10
MAX_AGENT_ITERATIONS = 10
WHISPER_MAX_BYTES = 24 * 1024 * 1024

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]