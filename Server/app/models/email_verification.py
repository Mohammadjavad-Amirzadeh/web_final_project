from ..extensions import db
from datetime import datetime, timedelta

class VerificationCode(db.Model):
    __tablename__ = 'verification_codes'

    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email = db.Column(db.String(100), nullable=False) 
    code = db.Column(db.Integer, nullable=False)
    expire_time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now() + timedelta(minutes=10))

    user = db.relationship("User", backref=db.backref("verification_codes", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<VerificationCode(user_id={self.user_id}, email={self.email}, code={self.code}, expire_time={self.expire_time})>"
