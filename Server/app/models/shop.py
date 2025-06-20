from ..extensions import db
from datetime import datetime
import enum

class ProductCategory(enum.Enum):
    FOODS = 'FOODS'
    HOT_DRINKS = 'HOT_DRINKS'
    COLD_DRINKS = 'COLD_DRINKS'
    CAKES = 'CAKES'
    SNACKS = 'SNACKS'



class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_sold = db.Column(db.Integer, default=0)

    category = db.Column(db.Enum(ProductCategory), nullable=False)

    order_items = db.relationship("OrderItem", back_populates="product")


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    is_completed = db.Column(db.Boolean, default=False)

    user = db.relationship("User")
    items = db.relationship("OrderItem", back_populates="order")


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float)

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product", back_populates="order_items")
