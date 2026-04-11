"""Aggregation helpers for admin dashboard metrics."""

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from .models import QuizAttempt, User


def _safe_avg(value):
    return round(float(value or 0.0), 2)


def build_dashboard_metrics(db: Session) -> dict:
    total_students = db.query(User).filter(User.role == "student").count()
    total_attempts = db.query(QuizAttempt).count()

    aggregates = db.query(
        func.avg(QuizAttempt.accuracy),
        func.avg(QuizAttempt.overall_score),
        func.avg(QuizAttempt.precision),
        func.avg(QuizAttempt.recall),
        func.avg(QuizAttempt.f1_score),
        func.avg(QuizAttempt.latency_ms),
        func.avg(QuizAttempt.hallucination_score),
        func.avg(case((QuizAttempt.hallucination_flag.is_(True), 1), else_=0)),
    ).first()

    topic_rows = (
        db.query(
            QuizAttempt.topic,
            func.count(QuizAttempt.id),
            func.avg(QuizAttempt.accuracy),
            func.avg(QuizAttempt.overall_score),
        )
        .filter(QuizAttempt.topic.isnot(None))
        .group_by(QuizAttempt.topic)
        .order_by(func.count(QuizAttempt.id).desc())
        .limit(12)
        .all()
    )

    fit_rows = (
        db.query(
            QuizAttempt.difficulty,
            func.count(QuizAttempt.id),
            func.avg(QuizAttempt.accuracy),
        )
        .filter(QuizAttempt.difficulty.isnot(None))
        .group_by(QuizAttempt.difficulty)
        .order_by(func.count(QuizAttempt.id).desc())
        .all()
    )

    student_rows = (
        db.query(
            User.id,
            User.username,
            func.count(QuizAttempt.id),
            func.avg(QuizAttempt.accuracy),
            func.max(QuizAttempt.created_at),
        )
        .join(QuizAttempt, QuizAttempt.user_id == User.id)
        .filter(User.role == "student")
        .group_by(User.id, User.username)
        .order_by(func.max(QuizAttempt.created_at).desc())
        .limit(20)
        .all()
    )

    latest_accuracy_map = {}
    if student_rows:
        student_ids = [row[0] for row in student_rows]
        latest_per_student = (
            db.query(QuizAttempt.user_id, func.max(QuizAttempt.created_at))
            .filter(QuizAttempt.user_id.in_(student_ids))
            .group_by(QuizAttempt.user_id)
            .all()
        )
        for user_id, latest_ts in latest_per_student:
            latest_attempt = (
                db.query(QuizAttempt)
                .filter(QuizAttempt.user_id == user_id, QuizAttempt.created_at == latest_ts)
                .first()
            )
            latest_accuracy_map[user_id] = _safe_avg(latest_attempt.accuracy if latest_attempt else 0.0)

    return {
        "total_students": total_students,
        "total_attempts": total_attempts,
        "avg_accuracy": _safe_avg(aggregates[0] if aggregates else 0.0),
        "avg_score": _safe_avg(aggregates[1] if aggregates else 0.0),
        "avg_precision": _safe_avg(aggregates[2] if aggregates else 0.0),
        "avg_recall": _safe_avg(aggregates[3] if aggregates else 0.0),
        "avg_f1_score": _safe_avg(aggregates[4] if aggregates else 0.0),
        "avg_latency_ms": _safe_avg(aggregates[5] if aggregates else 0.0),
        "avg_hallucination_score": _safe_avg(aggregates[6] if aggregates else 0.0),
        "hallucination_rate": _safe_avg((aggregates[7] if aggregates else 0.0) * 100.0),
        "topic_metrics": [
            {
                "topic": row[0] or "Unknown",
                "attempts": int(row[1] or 0),
                "avg_accuracy": _safe_avg(row[2]),
                "avg_score": _safe_avg(row[3]),
            }
            for row in topic_rows
        ],
        "question_fit_metrics": [
            {
                "difficulty": row[0] or "unknown",
                "attempts": int(row[1] or 0),
                "success_rate": _safe_avg(row[2]),
            }
            for row in fit_rows
        ],
        "student_trends": [
            {
                "user_id": int(row[0]),
                "username": row[1],
                "attempts": int(row[2] or 0),
                "avg_accuracy": _safe_avg(row[3]),
                "latest_accuracy": latest_accuracy_map.get(int(row[0]), 0.0),
            }
            for row in student_rows
        ],
    }
