from .auth import auth_bp
from .device import device_bp
# from .reservation import reservation_bp
# from .invoice import invoice_bp
# from .shop import shop_bp
# from .tournament import tournament_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(device_bp, url_prefix="/device")
    # app.register_blueprint(reservation_bp, url_prefix="/reservations")
    # app.register_blueprint(invoice_bp, url_prefix="/invoices")
    # app.register_blueprint(shop_bp, url_prefix="/shop")
    # app.register_blueprint(tournament_bp, url_prefix="/tournaments")
