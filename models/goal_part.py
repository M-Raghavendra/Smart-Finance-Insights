from extensions import db
from datetime import datetime


class GoalPart(db.Model):

    __tablename__ = "goal_parts"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    goal_id = db.Column(
        db.Integer,
        db.ForeignKey("goals.id"),
        nullable=False
    )

    part_name = db.Column(
        db.String(200),
        nullable=False
    )

    step_order = db.Column(
        db.Integer,
        default=1
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    estimated_cost = db.Column(
        db.Float,
        default=0
    )

    actual_cost = db.Column(
        db.Float,
        default=0
    )

    start_date = db.Column(
        db.Date,
        nullable=True
    )

    completion_date = db.Column(
        db.Date,
        nullable=True
    )

    status = db.Column(
        db.String(50),
        default="Pending"
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    goal = db.relationship(
        "Goal",
        backref=db.backref(
            "parts",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )