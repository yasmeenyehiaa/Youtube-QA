
from collections import defaultdict
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from app.config import MAX_HISTORY_TURNS

sessions: dict[tuple[str, str], list[BaseMessage]] = defaultdict(list)


def get_history(session_id: str, video_id: str) -> list[BaseMessage]:
    return list(sessions[(session_id, video_id)][-2 * MAX_HISTORY_TURNS :])


def add_turn(session_id: str, video_id: str, user_text: str, ai_text: str) -> None:
    key = (session_id, video_id)
    sessions[key].extend([HumanMessage(content=user_text), AIMessage(content=ai_text)])
    sessions[key] = sessions[key][-2 * MAX_HISTORY_TURNS :]


def clear_history(session_id: str, video_id: str) -> None:
    sessions.pop((session_id, video_id), None)
