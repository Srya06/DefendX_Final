from pydantic import BaseModel, constr, Field
from typing import Optional

class AdminCandidateCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    full_name: str
    target_force: Optional[str] = None

class CandidateEnrollmentResponse(BaseModel):
    user_id: str
    temporary_password: str
    status: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: constr(min_length=8)

class UsernameChangeRequest(BaseModel):
    new_username: constr(min_length=3, max_length=50)

class CurrentUserResponse(BaseModel):
    user_id: str
    role: str
    must_change_password: bool
