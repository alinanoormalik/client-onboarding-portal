from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Contact, Organisation
from app.schemas import ContactCreate, ContactRead, ContactUpdate

router = APIRouter(tags=["Contacts"])


def _get_contact(db: Session, contact_id: int) -> Contact:
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


def _clear_primary(db: Session, org_id: int, except_id: int | None = None):
    query = db.query(Contact).filter(
        Contact.organisation_id == org_id, Contact.is_primary.is_(True)
    )
    if except_id:
        query = query.filter(Contact.id != except_id)
    query.update({"is_primary": False})


@router.get("/organisations/{org_id}/contacts", response_model=list[ContactRead])
def list_contacts(org_id: int, db: Session = Depends(get_db)):
    if not db.get(Organisation, org_id):
        raise HTTPException(status_code=404, detail="Organisation not found")
    return (
        db.query(Contact)
        .filter(Contact.organisation_id == org_id)
        .order_by(Contact.is_primary.desc(), Contact.id)
        .all()
    )


@router.post(
    "/organisations/{org_id}/contacts",
    response_model=ContactRead,
    status_code=status.HTTP_201_CREATED,
)
def create_contact(org_id: int, payload: ContactCreate, db: Session = Depends(get_db)):
    if not db.get(Organisation, org_id):
        raise HTTPException(status_code=404, detail="Organisation not found")
    has_contacts = db.query(Contact).filter(Contact.organisation_id == org_id).first()
    data = payload.model_dump()
    if not has_contacts:
        data["is_primary"] = True
    elif data["is_primary"]:
        _clear_primary(db, org_id)
    contact = Contact(organisation_id=org_id, **data)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/contacts/{contact_id}", response_model=ContactRead)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    return _get_contact(db, contact_id)


@router.put("/contacts/{contact_id}", response_model=ContactRead)
def update_contact(contact_id: int, payload: ContactUpdate, db: Session = Depends(get_db)):
    contact = _get_contact(db, contact_id)
    data = payload.model_dump(exclude_unset=True)
    if "full_name" in data and not data["full_name"]:
        raise HTTPException(status_code=422, detail="full_name cannot be empty")
    if data.get("is_primary"):
        _clear_primary(db, contact.organisation_id, except_id=contact.id)
    for field, value in data.items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = _get_contact(db, contact_id)
    org_id, was_primary = contact.organisation_id, contact.is_primary
    db.delete(contact)
    db.flush()
    if was_primary:
        next_contact = (
            db.query(Contact)
            .filter(Contact.organisation_id == org_id)
            .order_by(Contact.id)
            .first()
        )
        if next_contact:
            next_contact.is_primary = True
    db.commit()