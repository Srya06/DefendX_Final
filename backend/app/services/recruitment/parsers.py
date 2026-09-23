import hashlib
from typing import Tuple, Dict, Any, List
import PyPDF2
from app.models.recruitment import ExtractionStatus

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
    def compute_text_hash(text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    @staticmethod
    def extract_text_from_pdf(filepath: str) -> Tuple[ExtractionStatus, int, List[Dict[str, Any]]]:
        """
        Extracts text from PDF page by page.
        Identifies if OCR is required.
        """
        extracted_pages = []
        total_text_length = 0
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                num_pages = len(reader.pages)
                for i in range(num_pages):
                    page = reader.pages[i]
                    text = page.extract_text()
                    if text:
                        clean_text = text.strip()
                        extracted_pages.append({
                            "page_number": i + 1,
                            "text": clean_text,
                            "content_hash": ParserService.compute_text_hash(clean_text)
                        })
                        total_text_length += len(clean_text)
                    else:
                        extracted_pages.append({
                            "page_number": i + 1,
                            "text": "",
                            "content_hash": ParserService.compute_text_hash("")
                        })

            if total_text_length < (num_pages * 50): # Arbitrary threshold for scanned PDF detection
                return ExtractionStatus.OCR_REQUIRED, num_pages, extracted_pages
                
            return ExtractionStatus.SUCCESS, num_pages, extracted_pages
        except Exception:
            return ExtractionStatus.FAILED, 0, []

    @staticmethod
    def detect_sections(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Heuristic-based section detection across pages.
        """
        sections = []
        current_section = None
        
        section_keywords = {
            "ELIGIBILITY": [r"eligibility criteria", r"educational qualification", r"age limit"],
            "PHYSICAL_STANDARD": [r"physical standard", r"physical fitness", r"height"],
            "MEDICAL_STANDARD": [r"medical standard", r"medical examination"],
            "VACANCY": [r"vacancies", r"number of posts"],
            "IMPORTANT_DATE": [r"important dates", r"schedule"],
            "SELECTION_STAGE": [r"selection process", r"scheme of examination"]
        }
        
        for page in pages:
            text = page["text"]
            lines = text.split('\n')
            
            for line in lines:
                line_clean = line.strip().lower()
                if not line_clean:
                    continue
                    
                # Check for headers
                matched_section = None
                for sec_type, keywords in section_keywords.items():
                    for kw in keywords:
                        if kw in line_clean and len(line_clean) < 50:
                            matched_section = sec_type
                            break
                    if matched_section:
                        break
                        
                if matched_section:
                    if current_section:
                        sections.append(current_section)
                    
                    current_section = {
                        "section_type": matched_section,
                        "page_start": page["page_number"],
                        "page_end": page["page_number"],
                        "text": line + "\n"
                    }
                elif current_section:
                    current_section["text"] += line + "\n"
                    current_section["page_end"] = page["page_number"]
                    
        if current_section:
            sections.append(current_section)
            
        return sections
        
    @staticmethod
    def extract_semantic_facts(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Converts generic sections into structured facts.
        """
        facts = []
        for sec in sections:
            fact_type = sec["section_type"]
            text = sec["text"].strip()
            if not text:
                continue
                
            facts.append({
                "fact_type": fact_type,
                "text": text,
                "structured_value": "NOT_AVAILABLE",
                "confidence": 0.8,
                "page_start": sec["page_start"],
                "page_end": sec["page_end"],
                "content_hash": ParserService.compute_text_hash(text)
            })
            
        return facts
