from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, Session as DBSession
from datetime import datetime
from typing import Optional

AUTH_COOKIE_NAME = "defendx_session"

def get_session_token(request: Request) -> Optional[str]:
    return request.cookies.get(AUTH_COOKIE_NAME)

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = get_session_token(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    db_session = db.query(DBSession).filter(DBSession.session_identifier == token).first()
    if not db_session or db_session.revoked_at or db_session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session invalid or expired")
    
    # Update last activity
    db_session.last_activity_at = datetime.utcnow()
    db.commit()

    user = db_session.user
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user

def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
        return current_user
    return role_checker

def require_candidate(current_user: User = Depends(get_current_active_user)) -> User:
    # If the user is active, but MUST change password, they can't access normal endpoints
    if current_user.must_change_password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Must change password before proceeding")
    
    if current_user.role != "CANDIDATE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Candidate access required")
    return current_user
