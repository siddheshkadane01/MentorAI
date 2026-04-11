"""Authentication routes: signup, login, current-user."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import cast

from ..auth import authenticate_user, create_access_token, get_current_user, hash_password
from ..database import get_db
from ..models import User
from ..schemas import BasicMessage, TokenResponse, UserLoginRequest, UserProfile, UserSignupRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=BasicMessage)
def signup_student(payload: UserSignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    student = User(
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role="student",
    )
    db.add(student)
    db.commit()
    return BasicMessage(message="Student account created successfully")


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        role=cast(str, user.role),
        username=cast(str, user.username),
        user_id=cast(int, user.id),
    )


@router.get("/me", response_model=UserProfile)
def me(current_user: User = Depends(get_current_user)):
    return current_user
