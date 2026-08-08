from datetime import datetime
from extensions import db


class Investment(db.Model):
    __tablename__ = "investments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    instrument_name = db.Column(
        db.String(100),
        nullable=False
    )

    asset_type = db.Column(
        db.String(50),
        nullable=False
    )

    quantity = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    invested_amount = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    current_value = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    purchase_date = db.Column(
        db.Date,
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Investment {self.instrument_name}>"