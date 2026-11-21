from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.records import get_by_id, load_records


def answer_question(question):
    from backend.rag import answer_question as rag_answer_question
    return rag_answer_question(question)

app = FastAPI(title="UGCRuleBook API")

records = load_records()

class Question(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

class AgentRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    fee_paid: float | None = None
    admission_year: int | None = None
    withdrawal_date: str | None = None
    policy_type: str | None = None
    last_date_of_admission: str | None = None
    full_refund_until: str | None = None
    max_deduction_until: str | None = None
    approval_required: bool = False
    approved: bool | None = None
    thread_id: str = "default"
    
@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/records")
def get_records(limit: int = 20):
    return records[:limit]


@app.get("/records/{id}")
def get_record(id: int):
    record = get_by_id(records, id)

    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    return record


@app.get("/search")
def search_records(q: str):
    from backend.smart_search import smart_search
    return smart_search(records, q)


@app.post("/questions")
def ask_question(data: Question):
    from backend.smart_search import smart_search

    results = smart_search(records, data.question)

    return {
        "question": data.question,
        "matching_records": results,
        "message": "Search completed"
    }


@app.post("/chat")
def chat(data: ChatRequest):
    from backend.llm import get_llm_response
    from backend.smart_search import smart_search

    results = smart_search(records, data.question)

    system_prompt = Path("prompts/system.txt").read_text()
    task_prompt = Path("prompts/answer_question.txt").read_text()

    context = "\n".join(str(record) for record in results)

    prompt = task_prompt.format(
        question=data.question,
        context=context
    )

    answer = get_llm_response(prompt, system_prompt)

    follow_up_prompt = Path("prompts/follow_up.txt").read_text()

    follow_up_prompt = follow_up_prompt.format(
        question=data.question,
        answer=answer
    )

    follow_up = get_llm_response(follow_up_prompt, system_prompt)

    return {
        "answer": answer,
        "confidence": "high" if results else "low",
        "follow_up": follow_up
    }


@app.get("/search/semantic")
def semantic_search_endpoint(q: str):
    if not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    from backend.vectorstore import search_documents

    results = search_documents(q, top_k=5)

    return {
        "question": q,
        "total_results": len(results),
        "results": results
    }


@app.post("/ask")
def ask(data: Question):

    result = answer_question(data.question)

    return {
        "question": data.question,
        "answer": result["answer"],
        "citations": result["citations"]
    }


@app.post("/agent")
def agent(data: AgentRequest):
    from backend.graph import run_graph

    try:
        return run_graph(
            question=data.question,
            fee_paid=data.fee_paid,
            admission_year=data.admission_year,
            withdrawal_date=data.withdrawal_date,
            policy_type=data.policy_type,
            last_date_of_admission=data.last_date_of_admission,
            full_refund_until=data.full_refund_until,
            max_deduction_until=data.max_deduction_until,
            approval_required=data.approval_required,
            approved=data.approved,
            thread_id=data.thread_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
