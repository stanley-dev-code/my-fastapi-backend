from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerCreate(BaseModel):
    full_name: str
    email: EmailStr | None = None
    phone: str | None = None
    company_name: str | None = None
    address: str | None = None


class CustomerUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    company_name: str | None = None
    address: str | None = None
    is_active: bool | None = None


class CustomerResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr | None
    phone: str | None
    company_name: str | None
    address: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)