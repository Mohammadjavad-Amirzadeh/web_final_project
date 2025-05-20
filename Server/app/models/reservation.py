from ..extensions import db
from datetime import datetime
import uuid

class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    
    pending_id = db.Column(db.String(36), unique=True)
    half_completed_id = db.Column(db.String(36), nullable=True)
    completed_id = db.Column(db.String(36), nullable=True)
    
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    is_free_mode = db.Column(db.Boolean, default=False)
    is_paid = db.Column(db.Boolean, default=False)
    upfront_paid = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    confirmed_at = db.Column(db.DateTime, nullable=True)         
    half_paid_at = db.Column(db.DateTime, nullable=True)         
    fully_paid_at = db.Column(db.DateTime, nullable=True)        

    user = db.relationship("User", back_populates="reservations")
    device = db.relationship("Device", back_populates="reservations")
    invoice_details = db.relationship("InvoiceDetail", back_populates="reservation")
