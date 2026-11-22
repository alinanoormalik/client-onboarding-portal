import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers import addresses, auth, contacts, organisations
from app.security import get_current_user

app = FastAPI(
    title="Client Onboarding Portal API",
    description="Backend API for managing organisations and contacts.",
    version="1.0.0",
)

origins = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(organisations.router, dependencies=[Depends(get_current_user)])
app.include_router(contacts.router, dependencies=[Depends(get_current_user)])
app.include_router(addresses.router, dependencies=[Depends(get_current_user)])


@app.get("/")
def root():
    return {"message": "Client Onboarding Portal API is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "connected",
        "database": "PostgreSQL",
        "message": "Database connection successful!",
    }