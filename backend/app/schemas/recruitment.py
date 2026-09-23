from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ProvenanceBase(BaseModel):
    document_id: Optional[str] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    source_url: Optional[str] = None
    content_hash: Optional[str] = None
    extraction_method: Optional[str] = None

class ForceResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ExamResponse(BaseModel):
    id: str
    force_id: str
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class RecruitmentCategoryResponse(BaseModel):
    id: str
    exam_id: str
    name: str
    model_config = ConfigDict(from_attributes=True)

class RequirementResponse(ProvenanceBase):
    id: str
    notification_id: str
    text_content: str
    model_config = ConfigDict(from_attributes=True)

class ImportantDateResponse(ProvenanceBase):
    id: str
    notification_id: str
    event_name: str
    date_value: Optional[datetime] = None
    text_content: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class VacancyResponse(ProvenanceBase):
    id: str
    notification_id: str
    position: str
    count: Optional[int] = None
    text_content: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class NotificationListResponse(BaseModel):
    id: str
    category_id: str
    title: str
    status: str
    model_config = ConfigDict(from_attributes=True)

class NotificationDetailResponse(NotificationListResponse):
    eligibility_requirements: List[RequirementResponse] = []
    physical_standards: List[RequirementResponse] = []
    medical_standards: List[RequirementResponse] = []
    selection_stages: List[RequirementResponse] = []
    important_dates: List[ImportantDateResponse] = []
    vacancies: List[VacancyResponse] = []
    model_config = ConfigDict(from_attributes=True)
