from ..extensions import db
from datetime import datetime

class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    is_free_mode = db.Column(db.Boolean, default=False)
    is_paid = db.Column(db.Boolean, default=False)
    upfront_paid = db.Column(db.Boolean, default=False)

    user = db.relationship("User", back_populates="reservations")
    device = db.relationship("Device", back_populates="reservations")
    invoice_details = db.relationship("InvoiceDetail", back_populates="reservation")
