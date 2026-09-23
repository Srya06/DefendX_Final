from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class FitnessAssessmentCreate(BaseModel):
    id: str = Field(..., description="Unique client-generated UUID for the assessment")
    exercise_type: str = Field(..., description="Type of exercise, e.g., 'pushups', 'squats'")
    started_at: datetime
    completed_at: datetime
    duration_seconds: float = Field(..., ge=0.0)
    total_reps: int = Field(..., ge=0)
    valid_reps: int = Field(..., ge=0)
    invalid_reps: int = Field(..., ge=0)
    average_confidence: float = Field(..., ge=0.0, le=1.0)
    form_score: float = Field(..., ge=0.0, le=100.0)
    form_warnings: Optional[str] = None
    status: str = "COMPLETED"

class FitnessAssessmentResponse(BaseModel):
    id: str
    user_id: str
    exercise_type: str
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    total_reps: int
    valid_reps: int
    invalid_reps: int
    average_confidence: float
    form_score: float
    form_warnings: Optional[str]
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
