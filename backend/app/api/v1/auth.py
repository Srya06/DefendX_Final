from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserCredential, Session as DBSession, AuditLog
from app.schemas.user import LoginRequest, ChangePasswordRequest, CurrentUserResponse
from app.core.security import verify_password, get_password_hash, generate_session_identifier
from app.api.dependencies import get_current_user, get_current_active_user, AUTH_COOKIE_NAME
from datetime import datetime, timedelta

router = APIRouter()

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

@router.post("/login")
def login(request_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request_data.username).first()
    
    # Generic error to prevent enumeration
    generic_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    if not user:
        raise generic_error
        
    cred = user.credential
    if not cred:
        raise generic_error
        
    if cred.locked_until and cred.locked_until > datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Account temporarily locked")
        
    if not verify_password(request_data.password, cred.password_hash):
        cred.failed_login_attempts += 1
        if cred.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
            cred.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            db.add(AuditLog(user_id=user.id, action="ACCOUNT_LOCKED", ip_address=None)) # simplified for phase 2
        db.add(AuditLog(user_id=user.id, action="LOGIN_FAILED", ip_address=None))
        db.commit()
        raise generic_error
        
    # Success
    cred.failed_login_attempts = 0
    cred.locked_until = None
    user.last_login_at = datetime.utcnow()
    
    # Create session
    session_id = generate_session_identifier()
    expires_at = datetime.utcnow() + timedelta(days=1)
    new_session = DBSession(user_id=user.id, session_identifier=session_id, expires_at=expires_at)
    db.add(new_session)
    
    db.add(AuditLog(user_id=user.id, action="LOGIN_SUCCESS", ip_address=None))
    db.commit()
    
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=False, # Set True for production https
        max_age=86400
    )
    return {"status": "ok", "must_change_password": user.must_change_password}

@router.post("/change-password")
def change_password(request_data: ChangePasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if request_data.new_password == current_user.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password cannot be same as username")
        
    cred = current_user.credential
    if not verify_password(request_data.current_password, cred.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")
        
    if verify_password(request_data.new_password, cred.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different")
        
    cred.password_hash = get_password_hash(request_data.new_password)
    cred.password_changed_at = datetime.utcnow()
    current_user.must_change_password = False
    
    # Revoke other sessions (optional, but good practice. For simplicity here, we leave it or just revoke current)
    # Ideally revoke all older sessions
    db.query(DBSession).filter(DBSession.user_id == current_user.id).update({"revoked_at": datetime.utcnow()})
    
    db.add(AuditLog(user_id=current_user.id, action="PASSWORD_CHANGED", ip_address=None))
    db.commit()
    return {"status": "password updated successfully. Please login again."}

@router.post("/logout")
def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    from app.api.dependencies import get_session_token
    token = get_session_token(request)
    if token:
        db_session = db.query(DBSession).filter(DBSession.session_identifier == token).first()
        if db_session:
            db_session.revoked_at = datetime.utcnow()
            db.add(AuditLog(user_id=db_session.user_id, action="LOGOUT", ip_address=None))
            db.commit()
            
    response.delete_cookie(AUTH_COOKIE_NAME)
    return {"status": "logged out"}

@router.get("/me", response_model=CurrentUserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    return CurrentUserResponse(
        user_id=current_user.username,
        role=current_user.role,
        must_change_password=current_user.must_change_password
    )
