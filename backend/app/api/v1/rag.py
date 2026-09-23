from fastapi import APIRouter
from app.schemas.rag import RetrievalRequest, RetrievalResponse
from app.services.rag.retriever import RetrieverService

router = APIRouter()

@router.post("/retrieve", response_model=RetrievalResponse)
def retrieve_evidence(request: RetrievalRequest):
    evidence_list = RetrieverService.retrieve(
        query=request.query,
        force=request.force,
        top_k=request.top_k
    )
    
    grounding_status = "GROUNDED" if evidence_list else "INSUFFICIENT_EVIDENCE"
    
    return RetrievalResponse(
        query=request.query,
        results=evidence_list,
        grounding_status=grounding_status
    )
