"""Admin routes for analytics dashboard."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import require_role
from ..database import get_db
from ..metrics import build_dashboard_metrics
from ..models import QuizAttempt, User
from ..schemas import DashboardResponse, QuizAttemptResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    return build_dashboard_metrics(db)


@router.get("/students/{student_id}/history", response_model=list[QuizAttemptResponse])
def student_history(
    student_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    rows = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == student_id)
        .order_by(QuizAttempt.created_at.desc())
        .limit(100)
        .all()
    )
    return rows
