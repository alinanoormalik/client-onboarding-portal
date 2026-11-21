from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models import Contact, Organisation, User
from app.security import require_role

from app.database import get_db
from app.models import Contact, Organisation
from app.schemas import (
    ContactCreate,
    ContactRead,
    OrganisationCreate,
    OrganisationDetail,
    OrganisationRead,
    OrganisationUpdate,
)

router = APIRouter(prefix="/organisations", tags=["Organisations"])


# ---------- helpers ----------
def get_org_or_404(db: Session, org_id: int) -> Organisation:
    org = db.get(Organisation, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return org


def build_detail(db: Session, org: Organisation) -> OrganisationDetail:
    contacts = (
        db.query(Contact)
        .filter(Contact.organisation_id == org.id)
        .order_by(Contact.is_primary.desc(), Contact.id)
        .all()
    )
    return OrganisationDetail(
        **OrganisationRead.model_validate(org).model_dump(),
        contacts=[ContactRead.model_validate(c) for c in contacts],
    )


def prepare_contacts(contacts: list[ContactCreate]) -> list[ContactCreate]:
    primaries = [c for c in contacts if c.is_primary]
    if len(primaries) > 1:
        raise HTTPException(
            status_code=422, detail="Only one contact can be the primary contact"
        )
    if contacts and not primaries:
        contacts[0].is_primary = True
    return contacts


def ensure_unique_registration(
    db: Session, reg_no: Optional[str], exclude_id: Optional[int] = None
):
    if not reg_no:
        return
    query = db.query(Organisation).filter(Organisation.registration_number == reg_no)
    if exclude_id:
        query = query.filter(Organisation.id != exclude_id)
    if query.first():
        raise HTTPException(
            status_code=409,
            detail="An organisation with this registration number already exists",
        )


# ---------- routes ----------
@router.get("", response_model=list[OrganisationRead])
def list_organisations(
    search: Optional[str] = None,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Organisation)
    if search:
        like = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Organisation.name.ilike(like),
                Organisation.email.ilike(like),
                Organisation.registration_number.ilike(like),
            )
        )
    if status_filter:
        query = query.filter(Organisation.status == status_filter)
    return query.order_by(Organisation.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=OrganisationDetail, status_code=status.HTTP_201_CREATED)
def create_organisation(payload: OrganisationCreate, db: Session = Depends(get_db)):
    ensure_unique_registration(db, payload.registration_number)
    contacts = prepare_contacts(payload.contacts)

    org = Organisation(**payload.model_dump(exclude={"contacts"}))
    db.add(org)
    db.flush()  # gets org.id without committing

    db.add_all(
        Contact(organisation_id=org.id, **c.model_dump()) for c in contacts
    )
    db.commit()
    db.refresh(org)
    return build_detail(db, org)


@router.get("/{org_id}", response_model=OrganisationDetail)
def get_organisation(org_id: int, db: Session = Depends(get_db)):
    return build_detail(db, get_org_or_404(db, org_id))


@router.put("/{org_id}", response_model=OrganisationDetail)
def update_organisation(
    org_id: int, payload: OrganisationUpdate, db: Session = Depends(get_db)
):
    org = get_org_or_404(db, org_id)
    data = payload.model_dump(exclude_unset=True, exclude={"contacts"})

    for required in ("name", "status"):
        if required in data and data[required] is None:
            raise HTTPException(status_code=422, detail=f"{required} cannot be empty")

    if "registration_number" in data:
        ensure_unique_registration(db, data["registration_number"], exclude_id=org.id)

    for field, value in data.items():
        setattr(org, field, value)
    org.updated_at = datetime.now(timezone.utc)

    if payload.contacts is not None:
        contacts = prepare_contacts(payload.contacts)
        db.query(Contact).filter(Contact.organisation_id == org.id).delete()
        db.add_all(
            Contact(organisation_id=org.id, **c.model_dump()) for c in contacts
        )

    db.commit()
    db.refresh(org)
    return build_detail(db, org)


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organisation(
    org_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    org = get_org_or_404(db, org_id)
    db.delete(org)
    db.commit()