"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UserSignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=128)
    full_name: Optional[str] = None


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    user_id: int


class UserProfile(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    role: str

    class Config:
        from_attributes = True


class QuestionEvaluationPayload(BaseModel):
    question_number: int
    question_text: Optional[str] = None
    question_type: Optional[str] = "multiple_choice"
    difficulty: Optional[str] = None
    student_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    is_correct: bool = False
    score: float = 0.0
    feedback: Optional[str] = None


class QuizAttemptCreate(BaseModel):
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    query_text: Optional[str] = None

    overall_score: float = 0.0
    correct_answers: int = 0
    incorrect_answers: int = 0
    total_questions: int = 0
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0

    latency_ms: float = 0.0
    generation_latency_ms: float = 0.0
    evaluation_latency_ms: float = 0.0

    hallucination_score: float = 0.0
    hallucination_flag: bool = False

    evaluations: List[QuestionEvaluationPayload] = []


class QuizAttemptResponse(BaseModel):
    id: int
    user_id: int
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    overall_score: float
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    latency_ms: float
    hallucination_score: float
    hallucination_flag: bool
    created_at: datetime

    class Config:
        from_attributes = True


class InteractionLogCreate(BaseModel):
    interaction_type: str
    topic: Optional[str] = None
    query_text: Optional[str] = None
    response_text: Optional[str] = None
    response_latency_ms: float = 0.0
    retrieval_context_length: int = 0
    hallucination_score: float = 0.0


class BasicMessage(BaseModel):
    message: str


class TopicMetric(BaseModel):
    topic: str
    attempts: int
    avg_accuracy: float
    avg_score: float


class DifficultyFitMetric(BaseModel):
    difficulty: str
    attempts: int
    success_rate: float


class StudentTrendMetric(BaseModel):
    user_id: int
    username: str
    attempts: int
    avg_accuracy: float
    latest_accuracy: float


class DashboardResponse(BaseModel):
    total_students: int
    total_attempts: int
    avg_accuracy: float
    avg_score: float
    avg_precision: float
    avg_recall: float
    avg_f1_score: float
    avg_latency_ms: float
    avg_hallucination_score: float
    hallucination_rate: float
    topic_metrics: List[TopicMetric]
    question_fit_metrics: List[DifficultyFitMetric]
    student_trends: List[StudentTrendMetric]
