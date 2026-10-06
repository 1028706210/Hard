from __future__ import annotations

from alembic import op
import sqlalchemy as sa



revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "settings",
        sa.Column("key", sa.String(length=128), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "daily_goals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("goal_date", sa.String(length=10), nullable=False, unique=True),
        sa.Column("target_minutes", sa.Integer(), nullable=False),
        sa.Column("target_exercises", sa.Integer(), nullable=False),
    )
    op.create_table(
        "lesson_progress",
        sa.Column("lesson_id", sa.String(length=160), primary_key=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("completed_at", sa.DateTime()),
    )
    op.create_table(
        "attempts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("lesson_id", sa.String(length=160), nullable=False),
        sa.Column("score", sa.Integer()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "submissions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("attempt_id", sa.String(length=36), sa.ForeignKey("attempts.id"), nullable=False),
        sa.Column("source_code", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "mastery_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.String(length=32), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "review_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("concept_id", sa.String(length=128), nullable=False),
        sa.Column("due_on", sa.String(length=10), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=False),
    )
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lesson_id", sa.String(length=160), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "favorites",
        sa.Column("lesson_id", sa.String(length=160), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "achievements",
        sa.Column("code", sa.String(length=128), primary_key=True),
        sa.Column("earned_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "backup_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "content_versions",
        sa.Column("content_id", sa.String(length=160), primary_key=True),
        sa.Column("version", sa.String(length=128), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "idempotency_keys",
        sa.Column("key", sa.String(length=128), primary_key=True),
        sa.Column("response_body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.execute(
        "CREATE VIRTUAL TABLE search_documents "
        "USING fts5(document_type UNINDEXED, document_id UNINDEXED, content)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS search_documents")
    op.drop_table("idempotency_keys")
    op.drop_table("content_versions")
    op.drop_table("backup_records")
    op.drop_table("achievements")
    op.drop_table("favorites")
    op.drop_table("notes")
    op.drop_table("review_items")
    op.drop_table("mastery_snapshots")
    op.drop_table("submissions")
    op.drop_table("attempts")
    op.drop_table("lesson_progress")
    op.drop_table("daily_goals")
    op.drop_table("settings")
