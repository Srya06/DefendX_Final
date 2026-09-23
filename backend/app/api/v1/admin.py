from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserCredential, Profile, AuditLog
from app.schemas.user import AdminCandidateCreate, CandidateEnrollmentResponse
from app.core.security import get_password_hash, generate_temporary_password
from app.api.dependencies import require_role

router = APIRouter()

@router.post("/candidates", response_model=CandidateEnrollmentResponse)
def create_candidate(
    candidate: AdminCandidateCreate, 
    db: Session = Depends(get_db), 
    admin_user: User = Depends(require_role("ADMIN"))
):
    if db.query(User).filter(User.username == candidate.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
        
    temp_password = generate_temporary_password()
    hashed_password = get_password_hash(temp_password)
    
    new_user = User(
        username=candidate.username,
        role="CANDIDATE",
        must_change_password=True
    )
    db.add(new_user)
    db.flush() # get ID
    
    new_cred = UserCredential(
        user_id=new_user.id,
        password_hash=hashed_password
    )
    db.add(new_cred)
    
    new_profile = Profile(
        user_id=new_user.id,
        full_name=candidate.full_name,
        target_force=candidate.target_force
    )
    db.add(new_profile)
    
    db.add(AuditLog(
        user_id=admin_user.id,
        action="CANDIDATE_CREATED",
        metadata_info={"created_username": candidate.username}
    ))
    
    db.commit()
    
    return CandidateEnrollmentResponse(
        user_id=new_user.username,
        temporary_password=temp_password,
        status="Candidate enrolled successfully"
    )
