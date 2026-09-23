import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.database import Base
from app.models.user import UUID_COL
import enum

class ExtractionStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    OCR_REQUIRED = "OCR_REQUIRED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"

class SourceRegistry(Base):
    __tablename__ = "source_registry"

    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    force = Column(String, nullable=False, index=True)
    organization = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    official_url = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="ACTIVE")
    last_checked_at = Column(DateTime, nullable=True)
    
    documents = relationship("RawDocument", back_populates="source")

class RawDocument(Base):
    __tablename__ = "raw_documents"

    document_id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(UUID_COL(), ForeignKey("source_registry.id"), nullable=False)
    title = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    document_type = Column(String, nullable=False)
    content_hash = Column(String, unique=True, index=True, nullable=False)
    retrieved_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    file_type = Column(String, nullable=False)
    storage_location = Column(String, nullable=False)
    extraction_status = Column(String, default=ExtractionStatus.PENDING.value)
    page_count = Column(Integer, nullable=True)
    extraction_method = Column(String, default="TEXT")
    parser_version = Column(String, default="1.0")
    language = Column(String, default="en")

    source = relationship("SourceRegistry", back_populates="documents")


# Structured Models with Provenance

class Force(Base):
    __tablename__ = "forces"
    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    exams = relationship("Exam", back_populates="force")


class Exam(Base):
    __tablename__ = "exams"
    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    force_id = Column(UUID_COL(), ForeignKey("forces.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    force = relationship("Force", back_populates="exams")
    categories = relationship("RecruitmentCategory", back_populates="exam")


class RecruitmentCategory(Base):
    __tablename__ = "recruitment_categories"
    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(UUID_COL(), ForeignKey("exams.id"), nullable=False)
    name = Column(String, nullable=False)

    exam = relationship("Exam", back_populates="categories")
    notifications = relationship("RecruitmentNotification", back_populates="category")


class RecruitmentNotification(Base):
    __tablename__ = "recruitment_notifications"
    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = Column(UUID_COL(), ForeignKey("recruitment_categories.id"), nullable=False)
    title = Column(String, nullable=False)
    document_id = Column(UUID_COL(), ForeignKey("raw_documents.document_id"), nullable=True)
    status = Column(String, default="ACTIVE")

    category = relationship("RecruitmentCategory", back_populates="notifications")
    document = relationship("RawDocument")
    
    eligibility_requirements = relationship("EligibilityRequirement", back_populates="notification")
    physical_standards = relationship("PhysicalStandard", back_populates="notification")
    medical_standards = relationship("MedicalStandard", back_populates="notification")
    selection_stages = relationship("SelectionStage", back_populates="notification")
    important_dates = relationship("ImportantDate", back_populates="notification")
    vacancies = relationship("Vacancy", back_populates="notification")


# Provenance Mixin for Structured Details
class ProvenanceMixin:
    page_start = Column(Integer, nullable=True)
    page_end = Column(Integer, nullable=True)
    source_url = Column(String, nullable=True)
    content_hash = Column(String, nullable=True)
    extraction_method = Column(String, nullable=True)


class EligibilityRequirement(Base, ProvenanceMixin):
    __tablename__ = "eligibility_requirements"
    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    notification_id = Column(UUID_COL(), ForeignKey("recruitment_notifications.id"), nullable=False)
    document_id = Column(UUID_COL(), ForeignKey("raw_documents.document_id"), nullable=True)
    text_content = Column(Text, nullable=False)

    notification = relationship("RecruitmentNotification", back_populates="eligibility_requirements")
    document = relationship("RawDocument")


class PhysicalStandard(Base, ProvenanceMixin):
    __tablename__ = "physical_standards"
    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    notification_id = Column(UUID_COL(), ForeignKey("recruitment_notifications.id"), nullable=False)
    document_id = Column(UUID_COL(), ForeignKey("raw_documents.document_id"), nullable=True)
    text_content = Column(Text, nullable=False)

    notification = relationship("RecruitmentNotification", back_populates="physical_standards")
    document = relationship("RawDocument")


class MedicalStandard(Base, ProvenanceMixin):
    __tablename__ = "medical_standards"
    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    notification_id = Column(UUID_COL(), ForeignKey("recruitment_notifications.id"), nullable=False)
    document_id = Column(UUID_COL(), ForeignKey("raw_documents.document_id"), nullable=True)
    text_content = Column(Text, nullable=False)

    notification = relationship("RecruitmentNotification", back_populates="medical_standards")
    document = relationship("RawDocument")


class SelectionStage(Base, ProvenanceMixin):
    __tablename__ = "selection_stages"
    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    notification_id = Column(UUID_COL(), ForeignKey("recruitment_notifications.id"), nullable=False)
    document_id = Column(UUID_COL(), ForeignKey("raw_documents.document_id"), nullable=True)
    text_content = Column(Text, nullable=False)

    notification = relationship("RecruitmentNotification", back_populates="selection_stages")
    document = relationship("RawDocument")


class ImportantDate(Base, ProvenanceMixin):
    __tablename__ = "important_dates"
    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    notification_id = Column(UUID_COL(), ForeignKey("recruitment_notifications.id"), nullable=False)
    document_id = Column(UUID_COL(), ForeignKey("raw_documents.document_id"), nullable=True)
    event_name = Column(String, nullable=False)
    date_value = Column(DateTime, nullable=True)
    text_content = Column(Text, nullable=True)

    notification = relationship("RecruitmentNotification", back_populates="important_dates")
    document = relationship("RawDocument")


class Vacancy(Base, ProvenanceMixin):
    __tablename__ = "vacancies"
    id = Column(UUID_COL(), primary_key=True, default=lambda: str(uuid.uuid4()))
    notification_id = Column(UUID_COL(), ForeignKey("recruitment_notifications.id"), nullable=False)
    document_id = Column(UUID_COL(), ForeignKey("raw_documents.document_id"), nullable=True)
    position = Column(String, nullable=False)
    count = Column(Integer, nullable=True)
    text_content = Column(Text, nullable=True)

    notification = relationship("RecruitmentNotification", back_populates="vacancies")
    document = relationship("RawDocument")
