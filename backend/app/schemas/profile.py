from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal

TargetForce = Literal["Indian Army", "Indian Navy", "Indian Air Force", "Police"]

class ProfileBase(BaseModel):
    full_name: str
    target_force: Optional[TargetForce] = None

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    target_force: Optional[TargetForce] = None

class ProfileResponse(ProfileBase):
    id: str
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)
