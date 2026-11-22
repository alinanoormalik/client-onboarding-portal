from datetime import datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

OrgStatus = Literal["pending", "active", "inactive"]
ContactType = Literal["general", "billing", "technical", "legal", "other"]
UserRole = Literal["admin", "staff"]

UK_POSTCODE = r"^[A-Za-z]{1,2}\d[A-Za-z\d]?\s*\d[A-Za-z]{2}$"
Postcode = Annotated[
    str, StringConstraints(strip_whitespace=True, to_upper=True, pattern=UK_POSTCODE)
]


# ---------- Contacts ----------
class ContactBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    job_title: Optional[str] = Field(default=None, max_length=150)
    contact_type: ContactType = "general"
    is_primary: bool = False


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    job_title: Optional[str] = Field(default=None, max_length=150)
    contact_type: Optional[ContactType] = None
    is_primary: Optional[bool] = None


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
    address_line1: Optional[str] = Field(default=None, max_length=200)
    address_line2: Optional[str] = Field(default=None, max_length=200)
    city: Optional[str] = Field(default=None, max_length=100)
    county: Optional[str] = Field(default=None, max_length=100)
    postcode: Optional[Postcode] = None
    country: Optional[str] = Field(default=None, max_length=100)
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
    address_line1: Optional[str] = Field(default=None, max_length=200)
    address_line2: Optional[str] = Field(default=None, max_length=200)
    city: Optional[str] = Field(default=None, max_length=100)
    county: Optional[str] = Field(default=None, max_length=100)
    postcode: Optional[Postcode] = None
    country: Optional[str] = Field(default=None, max_length=100)
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


# ---------- Address lookup ----------
class AddressSuggestion(BaseModel):
    label: str
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    postcode: Optional[str] = None
    country: str = "United Kingdom"