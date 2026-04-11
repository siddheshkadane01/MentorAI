"""SQLAlchemy ORM models for auth, attempts, and telemetry."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="student")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    interaction_logs = relationship("InteractionLog", back_populates="user", cascade="all, delete-orphan")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    topic = Column(String(200), nullable=True, index=True)
    difficulty = Column(String(20), nullable=True, index=True)
    query_text = Column(Text, nullable=True)

    overall_score = Column(Float, default=0.0)
    correct_answers = Column(Integer, default=0)
    incorrect_answers = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    precision = Column(Float, default=0.0)
    recall = Column(Float, default=0.0)
    f1_score = Column(Float, default=0.0)

    latency_ms = Column(Float, default=0.0)
    generation_latency_ms = Column(Float, default=0.0)
    evaluation_latency_ms = Column(Float, default=0.0)

    hallucination_score = Column(Float, default=0.0)
    hallucination_flag = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="attempts")
    question_evaluations = relationship(
        "QuestionEvaluation", back_populates="attempt", cascade="all, delete-orphan"
    )


class QuestionEvaluation(Base):
    __tablename__ = "question_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=False, index=True)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=True)
    question_type = Column(String(50), nullable=True)
    difficulty = Column(String(20), nullable=True)

    student_answer = Column(Text, nullable=True)
    correct_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, default=False)
    score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)

    attempt = relationship("QuizAttempt", back_populates="question_evaluations")


class InteractionLog(Base):
    __tablename__ = "interaction_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    interaction_type = Column(String(50), nullable=False)
    topic = Column(String(200), nullable=True)
    query_text = Column(Text, nullable=True)
    response_text = Column(Text, nullable=True)

    response_latency_ms = Column(Float, default=0.0)
    retrieval_context_length = Column(Integer, default=0)
    hallucination_score = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="interaction_logs")
