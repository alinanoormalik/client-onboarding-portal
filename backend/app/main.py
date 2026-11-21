from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.routers import auth, organisations
from app.security import get_current_user

from app.database import get_db
from app.routers import organisations

app = FastAPI(
    title="Client Onboarding Portal API",
    description="Backend API for managing organisations and contacts.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(organisations.router)


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

app.include_router(auth.router)
app.include_router(organisations.router, dependencies=[Depends(get_current_user)])