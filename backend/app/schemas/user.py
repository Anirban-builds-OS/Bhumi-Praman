from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole


class LoginRequest(BaseModel):
    employee_code: str
    password: str
    stay_signed_in: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: "UserOut"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_code: str
    full_name: str
    role: UserRole
    jurisdiction: str | None = None
    is_active: bool
    created_at: datetime


class UserCreate(BaseModel):
    employee_code: str
    full_name: str
    password: str
    role: UserRole
    jurisdiction: str | None = None
