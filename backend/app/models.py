
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# ==========================================
# USER MODEL
# ==========================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(150), nullable=False)

    email = Column(String(255), unique=True, index=True, nullable=False)

    hashed_password = Column(String(255), nullable=False)

    role = Column(String(50), nullable=False, default="staff")

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ==========================================
# ORGANISATION MODEL
# ==========================================

class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False, index=True)

    registration_number = Column(String(100), unique=True, nullable=True)

    industry = Column(String(150), nullable=True)

    email = Column(String(255), nullable=True)

    phone = Column(String(30), nullable=True)

    website = Column(String(255), nullable=True)

    address = Column(String(500), nullable=True)

    status = Column(String(50), nullable=False, default="pending")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    contacts = relationship(
        "Contact",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )


# ==========================================
# CONTACT MODEL
# ==========================================

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)

    organisation_id = Column(
        Integer,
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
    )

    full_name = Column(String(150), nullable=False)

    email = Column(String(255), nullable=True)

    phone = Column(String(30), nullable=True)

    job_title = Column(String(150), nullable=True)

    is_primary = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organisation = relationship(
        "Organisation",
        back_populates="contacts",
    )
