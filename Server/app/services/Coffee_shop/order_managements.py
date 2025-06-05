from ...models.shop import Order
from ...models.shop import OrderItem
from ...models.shop import Product
from ...extensions import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# Order Item
# -----------------------------------------------------------------------------------------------------
# CREATE
def add_order_item(order_id: int, product_id: int, quantity: int):
    product = Product.query.get(product_id)
    if not product:
        return None
    try:
        order_item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=product.price
        )
        
        db.session.add(order_item)
        product.total_sold += quantity
        db.session.commit()
        return order_item
    except Exception:
        db.session.rollback()
        return None

# READ
def get_order_item_by_id(order_item_id: int):
    return OrderItem.query.get(order_item_id)

# UPDATE
def update_order_item(order_item_id: int, quantity: int = None):
    item = OrderItem.query.get(order_item_id)
    if not item:
        return None
    try:
        if quantity is not None:
            item.quantity = quantity
        db.session.commit()
        return item
    except Exception:
        db.session.rollback()
        return None

# DELETE
def delete_order_item(order_item_id: int):
    item = OrderItem.query.get(order_item_id)
    if not item:
        return False
    try:
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


# Order
# -----------------------------------------------------------------------------------------------------
# CREATE
def add_order(user_id: int):
    status = -1
    try:
        existing_order = Order.query.filter_by(user_id=user_id, is_completed=False).first()
        if existing_order:
            status = 0
            return 'opened order error', status

        new_order = Order(user_id=user_id, created_at=datetime.now())
        db.session.add(new_order)
        db.session.commit()
        status = 1
        return new_order, status
    except Exception:
        db.session.rollback()
        status = 2
        return None, status


# READ
def get_order_by_id(order_id: int):
    return Order.query.get(order_id)
def get_all_orders():
    return Order.query.all()

# UPDATE
# def update_order(order_id: int, user_id: int = None, items: list = None):
#     order = Order.query.get(order_id)
#     if not order:
#         return None  

#     try:
#         if user_id is not None:
#             order.user_id = user_id

#         if items is not None:
#             for item in order.items:
#                 product = Product.query.get(item.product_id)
#                 if product:
#                     product.total_sold -= item.quantity  
#                 db.session.delete(item)

#             for item in items:
#                 product_id = item.get('product_id')
#                 quantity = item.get('quantity', 1)
#                 product = Product.query.get(product_id)
#                 if not product:
#                     continue  

#                 new_item = OrderItem(
#                     order_id=order.id,
#                     product_id=product_id,
#                     quantity=quantity,
#                     unit_price=product.price
#                 )
#                 db.session.add(new_item)
#                 product.total_sold += quantity  

#         db.session.commit()
#         return order
#     except Exception as e:
#         db.session.rollback()
#         return None

# DELETE
def delete_order(order_id: int):
    order = Order.query.get(order_id)
    if not order:
        return False
    try:
        db.session.delete(order)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False
