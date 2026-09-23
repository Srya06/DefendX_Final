import asyncio
import os
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.services.recruitment.pipeline import IngestionPipeline
from app.models.recruitment import RawDocument, SourceRegistry, RecruitmentNotification, PhysicalStandard
from app.db.neo4j import get_neo4j
from app.db.vector import get_vector_store
from app.services.rag.retriever import RetrieverService
from app.services.recruitment.parsers import ParserService, ExtractionStatus

async def verify():
    print("=== DEFEND-X PHASE 5.1 VERIFICATION ===")
    
    # 4. VERIFY GRAPH INGESTION
    print("\n--- 4. VERIFY GRAPH INGESTION ---")
    db = SessionLocal()
    pipeline = IngestionPipeline(db)
    
    filepath = "storage/documents/mock_navy.pdf"
    content_hash = ParserService.compute_content_hash(filepath)
    ext_status, page_count, pages_dict = ParserService.extract_text_from_pdf(filepath)
    ext_method = "OCR" if ext_status == ExtractionStatus.OCR_REQUIRED else "TEXT"
    
    doc = db.query(RawDocument).filter_by(content_hash=content_hash).first()
    if doc:
        print("Document already exists in PostgreSQL.")
    else:
        print("Document missing in PostgreSQL.")
    
    neo4j = get_neo4j()
    
    # Check node labels and counts
    print("\nGraph Node Labels & Counts:")
    res_nodes = neo4j.execute_query("MATCH (n) RETURN labels(n) AS labels, count(n) AS count ORDER BY count DESC")
    for r in res_nodes:
        print(f"  Labels: {r['labels']}, Count: {r['count']}")
        
    print("\nGraph Relationship Types & Counts:")
    res_rels = neo4j.execute_query("MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY count DESC")
    for r in res_rels:
        print(f"  Type: {r['type']}, Count: {r['count']}")
        
    print("\nSample Relationship Query (PostgreSQL doc vs Neo4j graph):")
    sample = neo4j.execute_query("MATCH (n:Notification)-[r:HAS_FACT]->(f:Fact) RETURN n.id as notif, type(r) as rel, f.type as ftype, f.text as text LIMIT 1")
    if sample:
        print(f"  Sample result found matching Notification and Fact: {sample[0]['ftype']} - {sample[0]['text'][:30]}...")
    else:
        print("  No sample result found.")

    # 5. VERIFY GRAPH RETRIEVAL
    print("\n--- 5. VERIFY GRAPH RETRIEVAL ---")
    print("Query: 'Navy physical standards', Force: 'Indian Navy'")
    # We will simulate the graph query directly since RetrieverService combines them
    info_type = RetrieverService.extract_intent("Navy physical standards")
    print(f"Extracted Intent: {info_type}")
    q = """
    MATCH (n:Notification)-[:HAS_FACT]->(f:Fact {type: $fact_type, force: $force_name})
    RETURN f.text AS text, f.source AS source, f.id AS fact_id
    LIMIT 5
    """
    g_res = neo4j.execute_query(q, {"fact_type": info_type, "force_name": "Indian Navy"})
    print(f"Graph result count: {len(g_res)}")
    for r in g_res:
        print(f"  - Graph Evidence: {r['text'].strip()[:50]}...")
        print(f"  - Document ID/Source: {r.get('source')}")

    # 6. VERIFY TRUE HYBRID RETRIEVAL
    print("\n--- 6. VERIFY TRUE HYBRID RETRIEVAL ---")
    client = TestClient(app)
    # The API might be something like POST /api/v1/rag/retrieve
    # Let's hit RetrieverService directly as the API wrapper
    res = RetrieverService.retrieve("Navy physical standards", force="Indian Navy")
    print(f"Final Combined Results: {len(res)}")
    graph_count = sum(1 for r in res if r.retrieval_source == "GRAPH")
    vec_count = sum(1 for r in res if r.retrieval_source == "VECTOR")
    print(f"GRAPH results: {graph_count}")
    print(f"VECTOR results: {vec_count}")
    for i, r in enumerate(res):
        print(f"  Result {i+1} ({r.retrieval_source}): {r.text.strip()[:60]}... (Score: {r.score})")

    # 7. VERIFY FORCE ISOLATION
    print("\n--- 7. VERIFY FORCE ISOLATION ---")
    res_iso = RetrieverService.retrieve("Indian Army age limit", force="Indian Navy")
    print(f"Force = Indian Navy, Query = 'Indian Army age limit'")
    print(f"Army evidence returned count: {len(res_iso)}")

    # 8. VERIFY INSUFFICIENT_EVIDENCE
    print("\n--- 8. VERIFY INSUFFICIENT_EVIDENCE ---")
    res_nons = RetrieverService.retrieve("Nonsense aliens", force="Indian Navy")
    if len(res_nons) == 0:
        print("API Response/Result: INSUFFICIENT_EVIDENCE")
    else:
        print(f"Returned unexpected results: {len(res_nons)}")

if __name__ == "__main__":
    asyncio.run(verify())
