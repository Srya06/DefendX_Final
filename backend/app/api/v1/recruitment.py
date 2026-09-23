from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.api.dependencies import get_current_user
from app.models.recruitment import Force, Exam, RecruitmentNotification, PhysicalStandard, EligibilityRequirement, RecruitmentCategory
from app.schemas.recruitment import ForceResponse, ExamResponse, NotificationListResponse, NotificationDetailResponse, RequirementResponse

router = APIRouter()

@router.get("/forces", response_model=List[ForceResponse])
def get_forces(db: Session = Depends(get_db)):
    forces = db.query(Force).all()
    return forces

@router.get("/exams", response_model=List[ExamResponse])
def get_exams(force_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Exam)
    if force_id:
        query = query.filter(Exam.force_id == force_id)
    return query.all()

@router.get("/notifications", response_model=List[NotificationListResponse])
def get_notifications(
    target_force: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(RecruitmentNotification)
    if target_force:
        # Join category -> exam -> force to filter
        query = query.join(RecruitmentCategory).join(Exam).join(Force).filter(Force.name == target_force)
    return query.all()

@router.get("/notifications/{notification_id}", response_model=NotificationDetailResponse)
def get_notification_detail(notification_id: str, db: Session = Depends(get_db)):
    notification = db.query(RecruitmentNotification).filter(RecruitmentNotification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.get("/physical-standards", response_model=List[RequirementResponse])
def get_physical_standards(notification_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(PhysicalStandard)
    if notification_id:
        query = query.filter(PhysicalStandard.notification_id == notification_id)
    return query.all()

@router.get("/eligibility", response_model=List[RequirementResponse])
def get_eligibility(notification_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(EligibilityRequirement)
    if notification_id:
        query = query.filter(EligibilityRequirement.notification_id == notification_id)
    return query.all()
