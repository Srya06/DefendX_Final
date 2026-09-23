from sqlalchemy.orm import Session
from app.models.recruitment import RawDocument, ExtractionStatus, PhysicalStandard, EligibilityRequirement
from app.services.recruitment.collectors import CollectorService
from app.services.recruitment.parsers import ParserService
from app.services.recruitment.validators import ValidatorService
from app.db.neo4j import get_neo4j
from app.db.vector import get_vector_store
import uuid

class IngestionPipeline:
    def __init__(self, db: Session):
        self.db = db

    async def ingest_document(self, source_id: str, url: str, title: str, doc_type: str = "RECRUITMENT_NOTIFICATION", target_notification_id: str = None) -> dict:
        # 1. Validation
        if not ValidatorService.validate_source_url(self.db, source_id, url):
            return {"status": "FAILED", "reason": "VALIDATION_FAILED", "detail": "URL does not match official source domain."}
            
        # 2. Collection
        filepath = await CollectorService.fetch_document(url)
        if not filepath:
            return {"status": "FAILED", "reason": "DOWNLOAD_FAILED", "detail": "Could not fetch document from source."}
            
        # 3. Parsing & Hashing
        content_hash = ParserService.compute_content_hash(filepath)
        
        # 4. Deduplication
        existing_doc = self.db.query(RawDocument).filter(RawDocument.content_hash == content_hash).first()
        if existing_doc:
            return {"status": "SUCCESS", "reason": "DUPLICATE_FOUND", "document_id": existing_doc.document_id}
            
        # 5. Extraction
        extraction_status, page_count, pages_dict = ParserService.extract_text_from_pdf(filepath)
        extraction_method = "OCR" if extraction_status == ExtractionStatus.OCR_REQUIRED else "TEXT"
        
        # 6. Database storage (RawDocument)
        doc = RawDocument(
            source_id=source_id,
            title=title,
            source_url=url,
            document_type=doc_type,
            content_hash=content_hash,
            file_type="application/pdf",
            storage_location=filepath,
            extraction_status=extraction_status.value,
            extraction_method=extraction_method,
            page_count=page_count
        )
        self.db.add(doc)
        self.db.commit()
        
        # 7. Section Detection & Fact Extraction
        sections = ParserService.detect_sections(pages_dict)
        facts = ParserService.extract_semantic_facts(sections)
        
        chunks_for_vector = []
        
        # Save facts to PostgreSQL if we have a target_notification_id
        if target_notification_id:
            for fact in facts:
                model_class = None
                if fact["fact_type"] == "PHYSICAL_STANDARD":
                    model_class = PhysicalStandard
                elif fact["fact_type"] == "ELIGIBILITY":
                    model_class = EligibilityRequirement
                    
                if model_class:
                    fact_obj = model_class(
                        notification_id=target_notification_id,
                        document_id=doc.document_id,
                        text_content=fact["text"],
                        page_start=fact["page_start"],
                        page_end=fact["page_end"],
                        source_url=url,
                        content_hash=fact["content_hash"],
                        extraction_method=extraction_method
                    )
                    self.db.add(fact_obj)
                    self.db.commit()
                    
                    # Push to Graph
                    neo4j = get_neo4j()
                    neo4j.execute_query(
                        """
                        MERGE (n:Notification {id: $notif_id})
                        MERGE (f:Fact {id: $fact_id})
                        SET f.type = $fact_type, f.text = $text, f.source = $source_url, f.force = $force_name
                        MERGE (n)-[:HAS_FACT]->(f)
                        """,
                        {"notif_id": target_notification_id, "fact_id": fact_obj.id, "fact_type": fact["fact_type"], "text": fact["text"], "source_url": url, "force_name": source_id} # We use source_id as proxy for force here temporarily for the metadata
                    )
                    
                    # Prepare for Vector
                    chunks_for_vector.append({
                        "id": fact_obj.id,
                        "text": fact["text"],
                        "metadata": {
                            "document_id": doc.document_id,
                            "fact_type": fact["fact_type"],
                            "source_url": url,
                            "page_start": fact["page_start"],
                            "notification_id": target_notification_id,
                            "force_name": source_id # Temporary proxy to be updated below
                        }
                    })

        # 8. Push to Vector Store
        if chunks_for_vector:
            vector_store = get_vector_store()
            vector_store.add_chunks(chunks_for_vector)

        return {
            "status": "SUCCESS",
            "document_id": doc.document_id,
            "extraction_status": extraction_status.value,
            "page_count": page_count,
            "facts_extracted": len(facts)
        }
