from ..extensions import db
from datetime import datetime

class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="invoices")
    details = db.relationship("InvoiceDetail", back_populates="invoice")


class InvoiceDetail(db.Model):
    __tablename__ = 'invoice_details'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id'), nullable=True)
    device_name = db.Column(db.String(100), nullable=False)
    usage_duration_minutes = db.Column(db.Integer, nullable=True)
    cost = db.Column(db.Float, nullable=False)

    invoice = db.relationship("Invoice", back_populates="details")
    reservation = db.relationship("Reservation", back_populates="invoice_details")
