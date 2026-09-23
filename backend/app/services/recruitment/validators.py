from sqlalchemy.orm import Session
from app.models.recruitment import SourceRegistry
from urllib.parse import urlparse

class ValidatorService:
    @staticmethod
    def validate_source_url(db: Session, source_id: str, url: str) -> bool:
        """
        Validates that a URL belongs to the registered source's official domain.
        """
        source = db.query(SourceRegistry).filter(SourceRegistry.id == source_id).first()
        if not source:
            return False
            
        try:
            official_domain = urlparse(source.official_url).netloc
            target_domain = urlparse(url).netloc
            # Check if target domain matches or is a subdomain of official domain
            return official_domain in target_domain or target_domain in official_domain
        except Exception:
            return False
