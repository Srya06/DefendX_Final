from app.db.neo4j import get_neo4j
from app.db.vector import get_vector_store
from app.schemas.rag import Evidence
import uuid

class RetrieverService:
    @staticmethod
    def extract_intent(query: str):
        query_lower = query.lower()
        info_type = None
        
        if "eligibility" in query_lower or "qualification" in query_lower or "age" in query_lower:
            info_type = "ELIGIBILITY"
        elif "education" in query_lower:
            info_type = "EDUCATION"
        elif "physical" in query_lower or "height" in query_lower:
            info_type = "PHYSICAL_STANDARD"
        elif "medical" in query_lower:
            info_type = "MEDICAL_STANDARD"
        elif "selection" in query_lower or "pattern" in query_lower or "process" in query_lower:
            info_type = "SELECTION_STAGE"
        elif "date" in query_lower or "schedule" in query_lower:
            info_type = "IMPORTANT_DATE"
        elif "vacancy" in query_lower or "vacancies" in query_lower or "post" in query_lower:
            info_type = "VACANCY"
            
        return info_type

    @staticmethod
    def retrieve(query: str, force: str, top_k: int = 5):
        info_type = RetrieverService.extract_intent(query)
        evidence_list = []
        seen_texts = set()
        
        # 1. GRAPH RETRIEVAL
        neo4j = get_neo4j()
        if info_type:
            q = """
            MATCH (n:Notification)-[:HAS_FACT]->(f:Fact {type: $fact_type, force: $force_name})
            RETURN f.text AS text, f.source AS source, f.id AS fact_id
            LIMIT $limit
            """
            try:
                results = neo4j.execute_query(q, {"fact_type": info_type, "force_name": force, "limit": top_k})
                if results:
                    for r in results:
                        text = r["text"]
                        if text not in seen_texts:
                            evidence_list.append(Evidence(
                                evidence_id=str(uuid.uuid4()),
                                text=text,
                                source_url=r.get("source"),
                                retrieval_source="GRAPH",
                                score=1.0 # Exact graph match
                            ))
                            seen_texts.add(text)
            except Exception as e:
                print("Neo4j offline. Skipping graph retrieval.")

        # 2. VECTOR RETRIEVAL (with FORCE ISOLATION)
        vector_store = get_vector_store()
        # Pass force metadata to ChromaDB where clause for hard isolation
        where_clause = {"force_name": force} if force else None
        
        v_results = vector_store.search(query=query, top_k=top_k, where=where_clause)
        
        for v in v_results:
            text = v["text"]
            score = 1.0 - (v["distance"] or 0)
            if score < 0.2:
                continue
            if text not in seen_texts:
                evidence_list.append(Evidence(
                    evidence_id=str(uuid.uuid4()),
                    document_id=v["metadata"].get("document_id"),
                    page_start=v["metadata"].get("page_start"),
                    source_url=v["metadata"].get("source_url"),
                    extraction_method=v["metadata"].get("extraction_method"),
                    text=text,
                    retrieval_source="VECTOR",
                    score=score
                ))
                seen_texts.add(text)
                
        # 3. Sort and Cap
        evidence_list = sorted(evidence_list, key=lambda x: x.score or 0, reverse=True)[:top_k]
        
        return evidence_list
