from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_learning_engine"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("lesson_progress", sa.Column("course_id", sa.String(length=32), nullable=False, server_default=""))
    op.add_column("lesson_progress", sa.Column("module_id", sa.String(length=128), nullable=False, server_default=""))
    op.add_column("lesson_progress", sa.Column("time_spent_seconds", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("lesson_progress", sa.Column("status", sa.String(length=24), nullable=False, server_default="not_started"))
    op.add_column("lesson_progress", sa.Column("updated_at", sa.DateTime(), nullable=True))

    op.add_column("attempts", sa.Column("exercise_id", sa.String(length=192), nullable=True))
    op.add_column("attempts", sa.Column("question_type", sa.String(length=24), nullable=True))
    op.add_column("attempts", sa.Column("hint_level", sa.String(length=24), nullable=True))
    op.add_column("attempts", sa.Column("raw_score", sa.Numeric(5, 2), nullable=True))
    op.add_column("attempts", sa.Column("final_score", sa.Numeric(5, 2), nullable=True))
    op.add_column("attempts", sa.Column("passed", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("attempts", sa.Column("placement", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("attempts", sa.Column("idempotency_key", sa.String(length=160), nullable=True))
    op.add_column("attempts", sa.Column("normalized_result", sa.Text(), nullable=True))

    op.add_column("submissions", sa.Column("language", sa.String(length=32), nullable=True))
    op.add_column("submissions", sa.Column("normalized_result", sa.Text(), nullable=True))
    op.add_column("submissions", sa.Column("duration_ms", sa.Integer(), nullable=True))

    op.add_column("mastery_snapshots", sa.Column("scope_type", sa.String(length=16), nullable=False, server_default="course"))
    op.add_column("mastery_snapshots", sa.Column("scope_id", sa.String(length=160), nullable=False, server_default=""))
    op.add_column("mastery_snapshots", sa.Column("status", sa.String(length=24), nullable=False, server_default="completed"))

    op.add_column("review_items", sa.Column("lesson_id", sa.String(length=160), nullable=True))
    op.add_column("review_items", sa.Column("exercise_id", sa.String(length=192), nullable=True))
    op.add_column("review_items", sa.Column("last_score", sa.Numeric(5, 2), nullable=True))
    op.add_column("review_items", sa.Column("status", sa.String(length=24), nullable=False, server_default="scheduled"))
    op.add_column("review_items", sa.Column("updated_at", sa.DateTime(), nullable=True))

    op.add_column("idempotency_keys", sa.Column("operation", sa.String(length=64), nullable=False, server_default=""))
    op.add_column("idempotency_keys", sa.Column("request_fingerprint", sa.String(length=64), nullable=False, server_default=""))
    op.create_index("ux_notes_lesson_id", "notes", ["lesson_id"], unique=True)

    op.create_table(
        "learning_activity_days",
        sa.Column("activity_date", sa.String(length=10), primary_key=True),
        sa.Column("time_spent_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_exercises", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ux_review_items_active_lesson_exercise",
        "review_items",
        ["lesson_id", "exercise_id"],
        unique=True,
        sqlite_where=sa.text("status IN ('wrong_answer', 'scheduled')"),
    )
    op.create_table(
        "experience_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_key", sa.String(length=256), nullable=False, unique=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("course_id", sa.String(length=32), nullable=False),
        sa.Column("lesson_id", sa.String(length=160)),
        sa.Column("exercise_id", sa.String(length=192)),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_index("ux_review_items_active_lesson_exercise", table_name="review_items")
    op.drop_table("experience_events")
    op.drop_table("learning_activity_days")
    op.drop_index("ux_notes_lesson_id", table_name="notes")

    with op.batch_alter_table("idempotency_keys") as batch:
        batch.drop_column("request_fingerprint")
        batch.drop_column("operation")
    with op.batch_alter_table("review_items") as batch:
        batch.drop_column("updated_at")
        batch.drop_column("status")
        batch.drop_column("last_score")
        batch.drop_column("exercise_id")
        batch.drop_column("lesson_id")
    with op.batch_alter_table("mastery_snapshots") as batch:
        batch.drop_column("status")
        batch.drop_column("scope_id")
        batch.drop_column("scope_type")
    with op.batch_alter_table("submissions") as batch:
        batch.drop_column("duration_ms")
        batch.drop_column("normalized_result")
        batch.drop_column("language")
    with op.batch_alter_table("attempts") as batch:
        batch.drop_column("normalized_result")
        batch.drop_column("idempotency_key")
        batch.drop_column("placement")
        batch.drop_column("passed")
        batch.drop_column("final_score")
        batch.drop_column("raw_score")
        batch.drop_column("hint_level")
        batch.drop_column("question_type")
        batch.drop_column("exercise_id")
    with op.batch_alter_table("lesson_progress") as batch:
        batch.drop_column("updated_at")
        batch.drop_column("status")
        batch.drop_column("time_spent_seconds")
        batch.drop_column("module_id")
        batch.drop_column("course_id")
