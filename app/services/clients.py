from openai import OpenAI
from app.config import OPENAI_API_KEY

client: OpenAI | None = None

def get_openai() -> OpenAI:
    global client
    if client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set. Add it to .env")
        client = OpenAI(api_key=OPENAI_API_KEY)
    return client
