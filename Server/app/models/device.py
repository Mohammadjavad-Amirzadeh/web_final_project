from ..extensions import db
import enum

class DeviceType(enum.Enum):
    PS4 = "ps4"
    PS5 = "ps5"
    BILLIARD = "billiard"
    CAFE = "cafe"

class Device(db.Model):
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.Enum(DeviceType), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    free_mode_rate = db.Column(db.Float, nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    picture_url = db.Column(db.String(255), nullable=False)

    reservations = db.relationship("Reservation", back_populates="device")
