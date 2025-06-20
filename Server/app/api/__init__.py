from .auth import auth_bp
from .device import device_bp
from .reservations import reservation_bp
# from .invoice import invoice_bp
from .coffee_shop import coffee_shop_bp
# from .tournament import tournament_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(device_bp, url_prefix="/device")
    app.register_blueprint(reservation_bp, url_prefix="/reservation")
    # app.register_blueprint(invoice_bp, url_prefix="/invoices")
    app.register_blueprint(coffee_shop_bp, url_prefix="/coffee-shop")
    # app.register_blueprint(tournament_bp, url_prefix="/tournaments")
