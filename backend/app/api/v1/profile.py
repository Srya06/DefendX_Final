from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, AuditLog
from app.schemas.user import UsernameChangeRequest
from app.api.dependencies import require_candidate

router = APIRouter()

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
