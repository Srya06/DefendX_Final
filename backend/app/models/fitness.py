from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base

class FitnessAssessment(Base):
    __tablename__ = "fitness_assessments"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    exercise_type = Column(String, nullable=False) # e.g. "pushups", "squats"
    
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=False)
    duration_seconds = Column(Float, nullable=False)
    
    total_reps = Column(Integer, default=0, nullable=False)
    valid_reps = Column(Integer, default=0, nullable=False)
    invalid_reps = Column(Integer, default=0, nullable=False)
    
    average_confidence = Column(Float, default=0.0, nullable=False)
    form_score = Column(Float, default=0.0, nullable=False)
    
    # Store aggregated JSON or string of major warnings for candidate feedback
    form_warnings = Column(String, nullable=True) 
    
    status = Column(String, default="COMPLETED", nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="fitness_assessments")
