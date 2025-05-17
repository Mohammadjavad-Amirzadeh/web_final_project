from flask import Flask
from .config import Config
from .extensions import db, migrate
from app.models.user import User
from app.models.device import Device, DeviceType
from app.models.reservation import Reservation
from app.models.invoice import Invoice, InvoiceDetail
from app.models.shop import Product, Order, OrderItem
from app.models.tournament import Tournament, TournamentParticipant
from app.models.email_verification import VerificationCode
from .api import register_routes
from .extensions import mail


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    
    mail.init_app(app)


    register_routes(app)
    return app
