import asyncio
import os
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.recruitment.pipeline import IngestionPipeline
from app.models.recruitment import RawDocument, SourceRegistry, RecruitmentNotification, PhysicalStandard, EligibilityRequirement, ExtractionStatus
from app.db.neo4j import get_neo4j
from app.db.vector import get_vector_store
from app.services.rag.retriever import RetrieverService

async def verify():
    print("=== DEFEND-X PHASE 5 VERIFICATION ===")
    
    db = SessionLocal()
    
    # 1. Setup mock authoritative source and notification
    source = db.query(SourceRegistry).filter_by(id="11111111-1111-1111-1111-111111111111").first()
    if not source:
        source = SourceRegistry(id="11111111-1111-1111-1111-111111111111", force="Indian Navy", organization="Navy", source_type="Website", official_url="joinindiannavy.gov.in", name="Indian Navy")
        db.add(source)
    
    from app.models.recruitment import Force, RecruitmentCategory, Exam
    f = db.query(Force).filter_by(id="22222222-2222-2222-2222-222222222222").first()
    if not f:
        f = Force(id="22222222-2222-2222-2222-222222222222", name="Indian Navy")
        db.add(f)
    e = db.query(Exam).filter_by(id="33333333-3333-3333-3333-333333333333").first()
    if not e:
        e = Exam(id="33333333-3333-3333-3333-333333333333", force_id="22222222-2222-2222-2222-222222222222", name="SSR Exam")
        db.add(e)
    c = db.query(RecruitmentCategory).filter_by(id="44444444-4444-4444-4444-444444444444").first()
    if not c:
        c = RecruitmentCategory(id="44444444-4444-4444-4444-444444444444", exam_id="33333333-3333-3333-3333-333333333333", name="SSR")
        db.add(c)
        
    notif = db.query(RecruitmentNotification).filter_by(id="55555555-5555-5555-5555-555555555555").first()
    if not notif:
        notif = RecruitmentNotification(id="55555555-5555-5555-5555-555555555555", category_id="44444444-4444-4444-4444-444444444444", title="Navy SSR", status="ACTIVE")
        db.add(notif)
    db.commit()

    # Create a mock highly realistic PDF file to ingest
    # We will just write a text file and rename it to PDF? No, PyPDF2 requires a real PDF.
    # Let's generate a real PDF using reportlab.
    try:
        from reportlab.pdfgen import canvas
        c = canvas.Canvas("storage/documents/mock_navy.pdf")
        c.drawString(100, 750, "INDIAN NAVY - SSR RECRUITMENT")
        c.drawString(100, 730, "Eligibility Criteria: Age limit 17-21 years.")
        c.drawString(100, 710, "Educational Qualification: 10+2 with Maths & Physics.")
        c.showPage()
        c.drawString(100, 750, "Physical Standards")
        c.drawString(100, 730, "Minimum height 157 cm. Vision 6/6.")
        c.save()
    except ImportError:
        import subprocess
        subprocess.run(["pip", "install", "reportlab"])
        from reportlab.pdfgen import canvas
        os.makedirs("storage/documents", exist_ok=True)
        c = canvas.Canvas("storage/documents/mock_navy.pdf")
        c.drawString(100, 750, "INDIAN NAVY - SSR RECRUITMENT")
        c.drawString(100, 730, "Eligibility Criteria: Age limit 17-21 years.")
        c.drawString(100, 710, "Educational Qualification: 10+2 with Maths & Physics.")
        c.showPage()
        c.drawString(100, 750, "Physical Standards")
        c.drawString(100, 730, "Minimum height 157 cm. Vision 6/6.")
        c.save()

    print("\n--- 1. DOCUMENT INTELLIGENCE ---")
    pipeline = IngestionPipeline(db)
    
    # Actually, pipeline.ingest_document downloads from URL.
    # I'll modify the mock to bypass download and just parse.
    from app.services.recruitment.parsers import ParserService
    filepath = "storage/documents/mock_navy.pdf"
    content_hash = ParserService.compute_content_hash(filepath)
    ext_status, page_count, pages_dict = ParserService.extract_text_from_pdf(filepath)
    ext_method = "OCR" if ext_status == ExtractionStatus.OCR_REQUIRED else "TEXT"
    
    doc = db.query(RawDocument).filter_by(content_hash=content_hash).first()
    if not doc:
        doc = RawDocument(
            source_id="11111111-1111-1111-1111-111111111111", title="Navy SSR Notification", source_url="https://joinindiannavy.gov.in/mock_navy.pdf", document_type="RECRUITMENT_NOTIFICATION",
            content_hash=content_hash, file_type="application/pdf", storage_location=filepath,
            extraction_status=ext_status.value, extraction_method=ext_method, page_count=page_count
        )
        db.add(doc)
        db.commit()

    sections = ParserService.detect_sections(pages_dict)
    facts = ParserService.extract_semantic_facts(sections)
    
    print(f"Document Title: Navy SSR Notification")
    print(f"Document ID: {doc.document_id}")
    print(f"Source URL: {doc.source_url}")
    print(f"Document Type: {doc.document_type}")
    print(f"Page Count: {page_count}")
    print(f"Extraction Status: {ext_status.value}")
    print(f"Extraction Method: {ext_method}")
    print(f"Parser Version: {doc.parser_version}")
    print(f"Extracted Pages: {len(pages_dict)}")
    print(f"Detected Sections: {len(sections)}")
    print(f"Semantic Facts: {len(facts)}")
    print(f"Content Hash: {content_hash}")
    
    print("\nExtracted Facts:")
    for f in facts:
        print(f"  - Fact Type: {f['fact_type']}")
        print(f"  - Extracted Value: {f['text'].strip()}")
        print(f"  - Page Number: {f['page_start']}")
        print(f"  - Source URL: {doc.source_url}")
        print(f"  - Confidence: {f['confidence']}")
        print(f"  - Extraction Method: {ext_method}")
        print(f"  - Document ID: {doc.document_id}\n")

    # Push to DB, Graph, Vector
    chunks_for_vector = []
    neo4j = get_neo4j()
    for fact in facts:
        fact_obj = PhysicalStandard(
            notification_id="55555555-5555-5555-5555-555555555555", document_id=doc.document_id, text_content=fact["text"],
            page_start=fact["page_start"], page_end=fact["page_end"], source_url=doc.source_url,
            content_hash=fact["content_hash"], extraction_method=ext_method
        )
        db.add(fact_obj)
        db.commit()
        try:
            neo4j.execute_query(
                "MERGE (n:Notification {id: $notif_id}) MERGE (f:Fact {id: $fact_id}) SET f.type = $fact_type, f.text = $text, f.source = $source_url, f.force = $force_name MERGE (n)-[:HAS_FACT]->(f)",
                {"notif_id": "55555555-5555-5555-5555-555555555555", "fact_id": fact_obj.id, "fact_type": fact["fact_type"], "text": fact["text"], "source_url": doc.source_url, "force_name": "Indian Navy"}
            )
        except Exception as e:
            print("Failed to push to Neo4j. Is it running locally? Error:", e)
        chunks_for_vector.append({
            "id": fact_obj.id, "text": fact["text"],
            "metadata": {"document_id": doc.document_id, "fact_type": fact["fact_type"], "source_url": doc.source_url, "page_start": fact["page_start"], "notification_id": "55555555-5555-5555-5555-555555555555", "force_name": "Indian Navy", "extraction_method": ext_method}
        })
    get_vector_store().add_chunks(chunks_for_vector)
    
    print("\n--- 2. PROVENANCE ---")
    print("See Extracted Facts above for document->page->text->fact traceability.")

    print("\n--- 3. OCR SAFETY ---")
    print(f"Demonstrated: normal text PDF -> {ext_method} extraction")

    print("\n--- 4. NEO4J ---")
    try:
        n_notif = neo4j.execute_query("MATCH (n:Notification) RETURN count(n) as c")[0]["c"]
        n_fact = neo4j.execute_query("MATCH (f:Fact) RETURN count(f) as c")[0]["c"]
        print(f"Number of Notification nodes: {n_notif}")
        print(f"Number of Fact nodes: {n_fact}")
        sample = neo4j.execute_query("MATCH (n:Notification)-[r:HAS_FACT]->(f:Fact) RETURN n.id as notif, type(r) as rel, f.type as ftype, f.text as text LIMIT 1")
        print(f"Sample Graph Query: MATCH (n:Notification)-[r:HAS_FACT]->(f:Fact) RETURN n, r, f LIMIT 1")
        print(f"Sample Query Result: {sample}")
    except Exception as e:
        print("Neo4j database is unreachable. Cannot verify graph nodes.", e)

    print("\n--- 5. VECTOR STORE ---")
    col = get_vector_store().collection
    print(f"Collection Name: {col.name}")
    print("Embedding Model: all-MiniLM-L6-v2")
    print(f"Number of Chunks: {col.count()}")
    peek = col.peek(1)
    if peek and peek["metadatas"]:
        print(f"Metadata Fields: {list(peek['metadatas'][0].keys())}")
        print(f"Example Metadata: {peek['metadatas'][0]}")

    print("\n--- 6. HYBRID RETRIEVAL ---")
    queries = [
        ("Navy physical standards", "Indian Navy"),
        ("Army age limit", "Indian Army"),
        ("Air Force eligibility", "Indian Air Force")
    ]
    for q, force in queries:
        print(f"\nQuery: '{q}', Force: {force}")
        res = RetrieverService.retrieve(q, force=force)
        print(f"Final Results Count: {len(res)}")
        for i, r in enumerate(res):
            print(f"  Result {i+1}:")
            print(f"    Retrieval Mode: {r.retrieval_source}")
            print(f"    Snippet: {r.text.strip()}")
            print(f"    Page: {r.page_start}")
            print(f"    Source URL: {r.source_url}")
            print(f"    Score: {r.score}")

    print("\n--- 7. FORCE ISOLATION / NEGATIVE RETRIEVAL ---")
    res = RetrieverService.retrieve("Indian Army age limit", force="Indian Navy")
    print(f"Navy Force querying Army Limit: Results Count = {len(res)}")
    res2 = RetrieverService.retrieve("Nonsense unsupported query", force="Indian Navy")
    print(f"Unsupported query: Results Count = {len(res2)}")
    print("Expected Behavior: INSUFFICIENT_EVIDENCE")

if __name__ == "__main__":
    asyncio.run(verify())
