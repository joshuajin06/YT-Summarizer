from fastapi import APIRouter, HTTPException

from models.schemas import QueryRequest, QueryResponse
from services.retrieval import retrieve

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    try: 
        res = retrieve(request.url, request.question)
        return QueryResponse(chunks=res)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
