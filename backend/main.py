"""FastAPI backend entrypoint for MentorAI role-based auth and analytics."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .auth import hash_password
from .database import Base, SessionLocal, engine
from .models import User
from .routes.admin_routes import router as admin_router
from .routes.auth_routes import router as auth_router
from .routes.student_routes import router as student_router

app = FastAPI(title="MentorAI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed_admin_user()


def seed_admin_user():
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == admin_username).first()
        if existing:
            return

        db.add(
            User(
                username=admin_username,
                full_name="Default Admin",
                hashed_password=hash_password(admin_password),
                role="admin",
                is_active=True,
            )
        )
        db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(student_router)
app.include_router(admin_router)
