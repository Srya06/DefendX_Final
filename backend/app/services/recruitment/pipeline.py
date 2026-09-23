from sqlalchemy.orm import Session
from app.models.recruitment import RawDocument, ExtractionStatus
from app.services.recruitment.collectors import CollectorService
from app.services.recruitment.parsers import ParserService
from app.services.recruitment.validators import ValidatorService
import uuid

class IngestionPipeline:
    def __init__(self, db: Session):
        self.db = db

    async def ingest_document(self, source_id: str, url: str, title: str, doc_type: str = "RECRUITMENT_NOTIFICATION") -> dict:
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
            page_count=page_count
        )
        self.db.add(doc)
        self.db.commit()
        
        return {
            "status": "SUCCESS",
            "document_id": doc.document_id,
            "extraction_status": extraction_status.value,
            "page_count": page_count
        }
