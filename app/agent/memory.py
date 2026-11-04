
from collections import defaultdict
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from app.config import MAX_HISTORY_TURNS

sessions: dict[str, list[BaseMessage]] = defaultdict(list)


def get_history(session_id: str) -> list[BaseMessage]:
    return list(sessions[session_id][-2 * MAX_HISTORY_TURNS :])


def add_turn(session_id: str, user_text: str, ai_text: str) -> None:
    sessions[session_id].extend([HumanMessage(content=user_text), AIMessage(content=ai_text)])
