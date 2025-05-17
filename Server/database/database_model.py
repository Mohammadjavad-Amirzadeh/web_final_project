from sqlalchemy import Column, Integer, String, Enum, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class UserType(enum.Enum):
    NORMAL = "normal"
    SUBSCRIBER = "subscriber"
    VIP = "vip"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Personal info
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(15), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)

    # Account info
    user_type = Column(Enum(UserType), default=UserType.NORMAL)
    credit = Column(Float, default=0.0)
    debt = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    is_debtor = Column(Boolean, default=False)

    # Account timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reservations = relationship("Reservation", back_populates="user")
    invoices = relationship("Invoice", back_populates="user")
    tournament_participations = relationship("TournamentParticipant", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.full_name}, type={self.user_type.name}, debt={self.debt})>"

class DeviceType(enum.Enum):
    PS4 = "ps4"
    PS5 = "ps5"
    BILLIARD = "billiard"
    CAFE = "cafe"

class Device(Base):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    device_type = Column(Enum(DeviceType), nullable=False)
    hourly_rate = Column(Float, nullable=False)
    free_mode_rate = Column(Float, nullable=True)  # optional higher rate for unlimited/free use
    is_available = Column(Boolean, default=True)

    reservations = relationship("Reservation", back_populates="device")


class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=False)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)  # nullable if free mode
    is_free_mode = Column(Boolean, default=False)
    is_paid = Column(Boolean, default=False)
    upfront_paid = Column(Boolean, default=False)  # paid half before start

    user = relationship("User", back_populates="reservations")
    device = relationship("Device", back_populates="reservations")
    invoice_details = relationship("InvoiceDetail", back_populates="reservation")


class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_amount = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="invoices")
    details = relationship("InvoiceDetail", back_populates="invoice")

class InvoiceDetail(Base):
    __tablename__ = 'invoice_details'

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    reservation_id = Column(Integer, ForeignKey('reservations.id'), nullable=True)
    device_name = Column(String(100), nullable=False)
    usage_duration_minutes = Column(Integer, nullable=True)  # Null for free mode
    cost = Column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="details")
    reservation = relationship("Reservation", back_populates="invoice_details")


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    total_sold = Column(Integer, default=0)

    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")



class Tournament(Base):
    __tablename__ = 'tournaments'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    game_type = Column(Enum(DeviceType), nullable=False)
    date = Column(DateTime, nullable=False)

    participants = relationship("TournamentParticipant", back_populates="tournament")

class TournamentParticipant(Base):
    __tablename__ = 'tournament_participants'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))
    score = Column(Integer, nullable=True)  # optional field for ranking

    user = relationship("User", back_populates="tournament_participations")
    tournament = relationship("Tournament", back_populates="participants")
