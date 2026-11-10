import json

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from app.config import OPENAI_API_KEY, OPENAI_CHAT_MODEL
from app.services import registry
from app.services import vector_store
from app.services.embeddings import embed_texts


class Chapter(BaseModel):
    title: str
    summary: str
    start_seconds: float = Field(ge=0)


class VideoOverview(BaseModel):
    summary: str
    chapters: list[Chapter]
    topics: list[str]


def generate_overview(video_id: str) -> dict:
    vector = embed_texts(["transcript overview"])
    chunks = vector_store.query(vector[0], top_k=10_000, video_id=video_id)
    ordered_chunks = sorted(chunks, key=lambda item: item["start"])
    if not ordered_chunks:
        raise ValueError("No transcript is available for this video.")

    lines = [f"[{chunk['start']:.1f}] {chunk['text']}" for chunk in ordered_chunks]
    batches: list[list[str]] = []
    current_batch: list[str] = []
    current_length = 0
    for line in lines:
        if current_batch and current_length + len(line) > 16_000:
            batches.append(current_batch)
            current_batch = []
            current_length = 0
        current_batch.append(line)
        current_length += len(line)
    if current_batch:
        batches.append(current_batch)

    model = ChatOpenAI(
        model=OPENAI_CHAT_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0,
    ).with_structured_output(VideoOverview)

    def summarize(transcript: str, final: bool) -> VideoOverview:
        if final:
            instruction = (
                "Combine these ordered transcript section summaries into one "
                "accurate video overview. Return a 2-4 sentence overall summary, "
                "3-8 chronological chapters, and up to 8 short topic labels. "
                "Only use chapter start_seconds values listed in the input. "
                "Write in the primary language of the transcript sections."
            )
        else:
            instruction = (
                "Summarize this transcript section accurately. Return 1-3 short "
                "sentences, chronological chapters, and up to 5 short topic "
                "labels. Every chapter start_seconds must be a timestamp that "
                "appears in the transcript. Do not invent facts. "
                "Write in the transcript's language."
            )
        return model.invoke([("system", instruction), ("human", transcript)])

    if len(batches) == 1:
        result = summarize("\n".join(batches[0]), final=False)
    else:
        sections = [
            summarize("\n".join(batch), final=False).model_dump()
            for batch in batches
        ]
        result = summarize(json.dumps(sections), final=True)

    starts = [float(chunk["start"]) for chunk in ordered_chunks]
    chapters = []
    for chapter in result.chapters:
        nearest_start = min(starts, key=lambda start: abs(start - chapter.start_seconds))
        chapters.append(
            {
                **chapter.model_dump(),
                "start_seconds": nearest_start,
            }
        )
    chapters.sort(key=lambda chapter: chapter["start_seconds"])
    topics = list(dict.fromkeys(topic.strip() for topic in result.topics if topic.strip()))
    return {
        "summary": result.summary.strip(),
        "chapters": chapters,
        "topics": topics[:8],
    }


def get_video_overview(video_id: str) -> dict:
    record = registry.get_video(video_id)
    if not record:
        raise ValueError("Video not found.")
    if record.get("overview"):
        return record["overview"]

    overview = generate_overview(video_id)
    record["overview"] = overview
    record["topics"] = overview["topics"]
    registry.put_video(record)
    return overview
