import uuid
from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from app.models.user_model import UserRole


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class AdminCreateUser(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER

class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    profile_photo_url: str | None = None
    bio: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None   # if you use a Gender enum
    nationality: str | None = None
    phone_number: str | None = None
    address: str | None = None

class UserRoleUpdate(BaseModel):
    role: UserRole

class UserResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    profile_photo_url: str | None = None
    bio: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    nationality: str | None = None
    phone_number: str | None = None
    address: str | None = None
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
