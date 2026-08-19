from extensions import db
from datetime import datetime

class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id"),   # <-- changed
    unique=True,
    nullable=False
)

    organization_name = db.Column(db.String(150), nullable=True)
    mobile_number = db.Column(db.String(15), nullable=True)
    currency = db.Column(db.String(10), nullable=True)

    monthly_income = db.Column(db.Float, nullable=True)
    monthly_target = db.Column(db.Float, nullable=True)

    occupation = db.Column(db.String(100), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)

    income_source = db.Column(db.String(100), nullable=True)

    profile_photo = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )