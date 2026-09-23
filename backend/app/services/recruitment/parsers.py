import hashlib
from typing import Tuple, Dict, Any
import PyPDF2
from app.models.recruitment import ExtractionStatus
import os

class ParserService:
    @staticmethod
    def compute_content_hash(filepath: str) -> str:
        """Compute SHA-256 hash of a file for deduplication."""
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    @staticmethod
    def extract_text_from_pdf(filepath: str) -> Tuple[ExtractionStatus, int, Dict[int, str]]:
        """
        Extracts text from PDF page by page.
        Identifies if OCR is required.
        """
        extracted_pages = {}
        total_text_length = 0
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                num_pages = len(reader.pages)
                for i in range(num_pages):
                    page = reader.pages[i]
                    text = page.extract_text()
                    if text:
                        extracted_pages[i + 1] = text.strip()
                        total_text_length += len(text.strip())
                    else:
                        extracted_pages[i + 1] = ""

            if total_text_length < (num_pages * 50): # Arbitrary threshold for scanned PDF detection
                return ExtractionStatus.OCR_REQUIRED, num_pages, extracted_pages
                
            return ExtractionStatus.SUCCESS, num_pages, extracted_pages
        except Exception:
            return ExtractionStatus.FAILED, 0, {}
