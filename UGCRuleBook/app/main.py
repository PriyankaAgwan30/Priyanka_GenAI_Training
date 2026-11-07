
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.smart_search import smart_search

from app.records import load_records, get_by_id, search


app = FastAPI(title="UGCRuleBook API")

records = load_records()


class Question(BaseModel):
    question: str


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
    results = smart_search(records, q)
    return results


@app.post("/questions")
def ask_question(data: Question):
    results = smart_search(records, data.question)

    return {
        "question": data.question,
        "matching_records": results,
        "message": "Search completed"
    }