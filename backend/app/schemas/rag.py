from pydantic import BaseModel
from typing import List, Optional

class Evidence(BaseModel):
    evidence_id: str
    document_id: Optional[str] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    source_url: Optional[str] = None
    content_hash: Optional[str] = None
    extraction_method: Optional[str] = None
    text: str
    retrieval_source: str # "GRAPH", "VECTOR", "BOTH"
    score: Optional[float] = None

class RetrievalRequest(BaseModel):
    query: str
    force: str
    top_k: int = 5

class RetrievalResponse(BaseModel):
    query: str
    results: List[Evidence] = []
    grounding_status: str # "GROUNDED" | "INSUFFICIENT_EVIDENCE"
