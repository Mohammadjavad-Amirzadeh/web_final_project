from ..extensions import db
import enum
from datetime import datetime

class UserType(enum.Enum):
    NORMAL = "normal"
    SUBSCRIBER = "subscriber"
    VIP = "vip"

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)

    user_type = db.Column(db.Enum(UserType), default=UserType.NORMAL)
    credit = db.Column(db.Float, default=0.0)
    debt = db.Column(db.Float, default=0.0)
    total_spent = db.Column(db.Float, default=0.0)
    is_debtor = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reservations = db.relationship("Reservation", back_populates="user")
    invoices = db.relationship("Invoice", back_populates="user")
    tournament_participations = db.relationship("TournamentParticipant", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.full_name})>"
