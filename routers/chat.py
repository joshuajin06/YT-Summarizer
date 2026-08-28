from fastapi import APIRouter, HTTPException

from models.schemas import ChatResponse, QueryRequest
from services.generation import answer_question
from services.retrieval import retrieve

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: QueryRequest):
    try:
        data = retrieve(request.url, request.question)
        res = answer_question(request.question, data)
        return ChatResponse(answer=res, citations=data)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc))