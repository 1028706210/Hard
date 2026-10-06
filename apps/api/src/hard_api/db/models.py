from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hard_api.db.base import Base


class Settings(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class DailyGoal(Base):
    __tablename__ = "daily_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    goal_date: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    target_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    target_exercises: Mapped[int] = mapped_column(Integer, nullable=False)


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    lesson_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    course_id: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    module_id: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="not_started", nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    lesson_id: Mapped[str] = mapped_column(String(160), nullable=False)
    score: Mapped[int | None] = mapped_column(Integer)
    exercise_id: Mapped[str | None] = mapped_column(String(192))
    question_type: Mapped[str | None] = mapped_column(String(24))
    hint_level: Mapped[str | None] = mapped_column(String(24))
    raw_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    final_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    placement: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(160))
    normalized_result: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    attempt_id: Mapped[str] = mapped_column(ForeignKey("attempts.id"), nullable=False)
    source_code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str | None] = mapped_column(String(32))
    normalized_result: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class MasterySnapshot(Base):
    __tablename__ = "mastery_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_type: Mapped[str] = mapped_column(String(16), default="course", nullable=False)
    scope_id: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="completed", nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class ReviewItem(Base):
    __tablename__ = "review_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    concept_id: Mapped[str] = mapped_column(String(128), nullable=False)
    lesson_id: Mapped[str | None] = mapped_column(String(160))
    exercise_id: Mapped[str | None] = mapped_column(String(192))
    due_on: Mapped[str] = mapped_column(String(10), nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, nullable=False)
    last_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    status: Mapped[str] = mapped_column(String(24), default="scheduled", nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Favorite(Base):
    __tablename__ = "favorites"

    lesson_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Achievement(Base):
    __tablename__ = "achievements"

    code: Mapped[str] = mapped_column(String(128), primary_key=True)
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class BackupRecord(Base):
    __tablename__ = "backup_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class ContentVersion(Base):
    __tablename__ = "content_versions"

    content_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    version: Mapped[str] = mapped_column(String(128), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    operation: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    response_body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class LearningActivityDay(Base):
    __tablename__ = "learning_activity_days"

    activity_date: Mapped[str] = mapped_column(String(10), primary_key=True)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_exercises: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class ExperienceEvent(Base):
    __tablename__ = "experience_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_key: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    course_id: Mapped[str] = mapped_column(String(32), nullable=False)
    lesson_id: Mapped[str | None] = mapped_column(String(160))
    exercise_id: Mapped[str | None] = mapped_column(String(192))
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
