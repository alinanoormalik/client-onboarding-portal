from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

OrgStatus = Literal["pending", "active", "inactive"]


# ---------- Contacts ----------
class ContactBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    job_title: Optional[str] = Field(default=None, max_length=150)
    is_primary: bool = False


class ContactCreate(ContactBase):
    pass


class ContactRead(ContactBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organisation_id: int
    created_at: Optional[datetime] = None


# ---------- Organisations ----------
class OrganisationBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    registration_number: Optional[str] = Field(default=None, max_length=100)
    industry: Optional[str] = Field(default=None, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    website: Optional[str] = Field(default=None, max_length=255)
    address: Optional[str] = Field(default=None, max_length=500)
    status: OrgStatus = "pending"


class OrganisationCreate(OrganisationBase):
    contacts: list[ContactCreate] = []


class OrganisationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    registration_number: Optional[str] = Field(default=None, max_length=100)
    industry: Optional[str] = Field(default=None, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    website: Optional[str] = Field(default=None, max_length=255)
    address: Optional[str] = Field(default=None, max_length=500)
    status: Optional[OrgStatus] = None
    # If provided, the organisation's contacts are replaced with this list
    contacts: Optional[list[ContactCreate]] = None


class OrganisationRead(OrganisationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OrganisationDetail(OrganisationRead):
    contacts: list[ContactRead] = []

# ---------- Users / Auth ----------
UserRole = Literal["admin", "staff"]


class UserCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: UserRole = "staff"


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead