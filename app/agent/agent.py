from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from app.agent.tools import build_tools
from app.config import MAX_AGENT_ITERATIONS, OPENAI_API_KEY, OPENAI_CHAT_MODEL

SYSTEM = """You answer questions about YouTube videos using only the results of your tools.

You may only use evidence from this video.

Rules:
- For questions about specific video content, call search_transcript first.
- For an overall video summary or chapter list, use generate_video_overview instead.
- Use summarize_time_range when the user asks for a summary of a section.
- Support each claim with the timestamp of its source, written as (mm:ss), for example (12:40).
- If the tools return nothing relevant, reply: "This isn't covered in the video."
- Do not add facts from outside the transcripts.
- Keep answers short and clear."""

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

def run_agent(message: str, history: list[BaseMessage], video_id: str, sink: list[dict]) -> str:
    llm = ChatOpenAI(
        model=OPENAI_CHAT_MODEL, 
        api_key=OPENAI_API_KEY, 
        temperature=0
    )
    tools = build_tools(video_id, sink)
    agent = create_tool_calling_agent(llm, tools, PROMPT)
    executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        max_iterations=MAX_AGENT_ITERATIONS,
        early_stopping_method="generate",
        handle_parsing_errors=True
    )
    result = executor.invoke(
        {
            "input": message, 
            "chat_history": history, 
        }
    )
    return result["output"]
