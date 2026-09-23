from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.models.fitness import FitnessAssessment
from app.models.user import User
from app.schemas.fitness import FitnessAssessmentCreate, FitnessAssessmentResponse
from app.api.dependencies import get_current_user

router = APIRouter()

@router.post("/assessments", response_model=FitnessAssessmentResponse)
def create_assessment(
    assessment: FitnessAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate negative values and impossible form scores just in case schema validation is bypassed
    if assessment.duration_seconds < 0 or assessment.total_reps < 0:
        raise HTTPException(status_code=422, detail="Negative metrics are not allowed.")
        
    if not (0 <= assessment.form_score <= 100):
        raise HTTPException(status_code=422, detail="Form score must be between 0 and 100.")
        
    db_assessment = FitnessAssessment(
        id=assessment.id,
        user_id=current_user.id,
        exercise_type=assessment.exercise_type,
        started_at=assessment.started_at,
        completed_at=assessment.completed_at,
        duration_seconds=assessment.duration_seconds,
        total_reps=assessment.total_reps,
        valid_reps=assessment.valid_reps,
        invalid_reps=assessment.invalid_reps,
        average_confidence=assessment.average_confidence,
        form_score=assessment.form_score,
        form_warnings=assessment.form_warnings,
        status=assessment.status
    )
    
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment

@router.get("/assessments", response_model=List[FitnessAssessmentResponse])
def get_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Enforce isolation: return only the authenticated candidate's assessments
    assessments = db.query(FitnessAssessment).filter(FitnessAssessment.user_id == current_user.id).order_by(FitnessAssessment.created_at.desc()).all()
    return assessments

@router.get("/assessments/{assessment_id}", response_model=FitnessAssessmentResponse)
def get_assessment(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assessment = db.query(FitnessAssessment).filter(FitnessAssessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
        
    # Enforce isolation: Candidate A cannot read Candidate B's assessment
    if assessment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this assessment")
        
    return assessment
