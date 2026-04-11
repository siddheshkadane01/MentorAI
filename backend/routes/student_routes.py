"""Student routes for attempts and interaction logging."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user, require_role
from ..database import get_db
from ..models import InteractionLog, QuestionEvaluation, QuizAttempt, User
from ..schemas import (
    BasicMessage,
    InteractionLogCreate,
    QuizAttemptCreate,
    QuizAttemptResponse,
)

router = APIRouter(prefix="/student", tags=["student"])


@router.post("/attempts", response_model=QuizAttemptResponse)
def submit_attempt(
    payload: QuizAttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    attempt = QuizAttempt(
        user_id=current_user.id,
        topic=payload.topic,
        difficulty=payload.difficulty,
        query_text=payload.query_text,
        overall_score=payload.overall_score,
        correct_answers=payload.correct_answers,
        incorrect_answers=payload.incorrect_answers,
        total_questions=payload.total_questions,
        accuracy=payload.accuracy,
        precision=payload.precision,
        recall=payload.recall,
        f1_score=payload.f1_score,
        latency_ms=payload.latency_ms,
        generation_latency_ms=payload.generation_latency_ms,
        evaluation_latency_ms=payload.evaluation_latency_ms,
        hallucination_score=payload.hallucination_score,
        hallucination_flag=payload.hallucination_flag,
    )
    db.add(attempt)
    db.flush()

    for row in payload.evaluations:
        db.add(
            QuestionEvaluation(
                attempt_id=attempt.id,
                question_number=row.question_number,
                question_text=row.question_text,
                question_type=row.question_type,
                difficulty=row.difficulty,
                student_answer=row.student_answer,
                correct_answer=row.correct_answer,
                is_correct=row.is_correct,
                score=row.score,
                feedback=row.feedback,
            )
        )

    db.commit()
    db.refresh(attempt)
    return attempt


@router.get("/history", response_model=list[QuizAttemptResponse])
def my_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    rows = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == current_user.id)
        .order_by(QuizAttempt.created_at.desc())
        .limit(50)
        .all()
    )
    return rows


@router.post("/interactions", response_model=BasicMessage)
def log_interaction(
    payload: InteractionLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    row = InteractionLog(
        user_id=current_user.id,
        interaction_type=payload.interaction_type,
        topic=payload.topic,
        query_text=payload.query_text,
        response_text=payload.response_text,
        response_latency_ms=payload.response_latency_ms,
        retrieval_context_length=payload.retrieval_context_length,
        hallucination_score=payload.hallucination_score,
    )
    db.add(row)
    db.commit()
    return BasicMessage(message="Interaction logged")
