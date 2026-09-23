from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, AuditLog, Profile
from app.schemas.user import UsernameChangeRequest
from app.schemas.profile import ProfileUpdate, ProfileResponse
from app.api.dependencies import require_candidate

router = APIRouter()

@router.get("", response_model=ProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    return ProfileResponse(
        id=str(current_user.id),
        username=current_user.username,
        role=current_user.role,
        full_name=profile.full_name,
        target_force=profile.target_force
    )

@router.patch("", response_model=ProfileResponse)
def update_profile(
    profile_in: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
        
    db.commit()
    db.refresh(profile)
    
    return ProfileResponse(
        id=str(current_user.id),
        username=current_user.username,
        role=current_user.role,
        full_name=profile.full_name,
        target_force=profile.target_force
    )

@router.patch("/username")
def change_username(
    request_data: UsernameChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate)
):
    if db.query(User).filter(User.username == request_data.new_username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already in use")
        
    old_username = current_user.username
    current_user.username = request_data.new_username
    
    db.add(AuditLog(
        user_id=current_user.id,
        action="USERNAME_CHANGED",
        metadata_info={"old": old_username, "new": request_data.new_username}
    ))
    db.commit()
    return {"status": "Username updated successfully", "new_username": current_user.username}
