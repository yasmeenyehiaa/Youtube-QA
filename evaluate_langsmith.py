import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langsmith import Client
from pydantic import BaseModel

load_dotenv()

from app.agent.agent import run_agent


class JudgeGrade(BaseModel):
    answer_correct: bool
    grounded_in_evidence: bool
    citations_supported: bool
    explanation: str


judge = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(
    JudgeGrade
)


def target(inputs: dict) -> dict:
    citations: list[dict] = []
    answer = run_agent(
        message=inputs["question"],
        history=[],
        video_id=inputs["video_id"],
        sink=citations,
    )
    return {"answer": answer, "citations": citations}


def evaluate_answer(
    inputs: dict,
    outputs: dict,
    reference_outputs: dict,
) -> dict:
    grade = judge.invoke(
        [
            (
                "system",
                (
                    "You are evaluating a YouTube video question-answering system. "
                    "Judge the answer only against the supplied reference evidence. "
                    "Do not require the answer to use the same wording as the expected "
                    "answer. Check that the answer is correct and supported by the "
                    "evidence, and that the returned citations support its claims. "
                    "If the evidence does not answer the question, the answer should "
                    "say that it is not covered rather than guess."
                ),
            ),
            (
                "human",
                json.dumps(
                    {
                        "question": inputs["question"],
                        "expected_answer": reference_outputs["answer"],
                        "reference_evidence": reference_outputs["evidence"],
                        "actual_answer": outputs["answer"],
                        "actual_citations": outputs["citations"],
                    },
                    ensure_ascii=False,
                ),
            ),
        ]
    )

    passed = (
        grade.answer_correct
        and grade.grounded_in_evidence
        and grade.citations_supported
    )
    return {
        "key": "video_qa_quality",
        "score": passed,
        "comment": grade.explanation,
    }


results = Client().evaluate(
    target,
    data="youtube-qa-golden-one",
    evaluators=[evaluate_answer],
    experiment_prefix="youtube-qa-baseline",
)
print(results)