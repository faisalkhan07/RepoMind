from fastapi import FastAPI
from pydantic import BaseModel
from ingestion import ingest_repo
from rag_query import ask_question

app = FastAPI()


class IngestRequest(BaseModel):
    repo_url: str


class QuestionRequest(BaseModel):
    question: str
    collection_name: str
    n_results: int = 3


@app.get("/")
def root():
    return {"message": "RepoMind API is running"}


@app.post("/ingest")
def ingest(request: IngestRequest):
    result = ingest_repo(request.repo_url)
    return result


@app.post("/ask")
def ask(request: QuestionRequest):
    result = ask_question(request.question, request.collection_name, request.n_results)
    return result