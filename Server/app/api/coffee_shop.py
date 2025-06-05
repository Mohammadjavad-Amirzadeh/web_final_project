from flask import Blueprint, request, jsonify
from ..services.Coffee_shop.products import *
from ..services.Coffee_shop.order_managements import *
from ..utils.jwt_token_handler import verify_jwt_request
from ..models.user import User
from collections import defaultdict


coffee_shop_bp = Blueprint('coffee_shop', __name__, url_prefix='/coffee-shop')


@coffee_shop_bp.route('/add-product', methods=['POST'])
def add_product():
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    user_id = payload.get("user_id")
    user = User.query.get(user_id)
    if not user or not getattr(user, 'is_admin', False):
        return jsonify({"error": "Permission denied. Admins only."}), 403

    data = request.form

    product_name = data.get('product_name')
    product_price = data.get('product_price')
    product_category = data.get('product_category')

    if not product_name or not product_price or not product_category:
        return jsonify({'error': 'product_name and product_price and product_category are required'}), 400

    try:
        product_price = float(product_price)
    except ValueError:
        return jsonify({'error': 'Invalid price format'}), 400

    if add_product_in_db(name=product_name, price=product_price, product_category=product_category):
        return jsonify({'message': 'Product Added Successfully'}), 200
    else:
        return jsonify({'error': 'Failed to add product'}), 500

@coffee_shop_bp.route('/get-all-products', methods=['GET'])
def get_all_products():
    products = get_all_products_in_db()

    unique_categories = set(
        product.category.value
        for product in products
    )

    categorized_products = {}

    for category in unique_categories:
        categorized_products[category] = [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "total_sold": product.total_sold
            }
            for product in products
            if (product.category.value) == category
        ]

    return jsonify({
        "products_by_category": categorized_products,
        "total_products": len(products)
    }), 200

@coffee_shop_bp.route('/get-product/<int:product_id>')
def get_product_by_id(product_id):
    try:
        product = get_product_by_id_in_db(product_id=product_id)
        return jsonify({
            'product':{
                'name': product.name,
                'price': product.price
            }
        })
    except Exception as err:
        return jsonify({
            'message': 'Can`t find product'
        })
        
@coffee_shop_bp.route('/update/<int:product_id>', methods=['PATCH'])
def update_product(product_id):
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    user_id = payload.get("user_id")
    user = User.query.get(user_id)
    if not user or not getattr(user, 'is_admin', False):
        return jsonify({"error": "Permission denied. Admins only."}), 403

    data = request.form

    product_name = data.get('product_name')
    product_price = data.get('product_price')
    product_total_sold = data.get('total_sold')
    product_category = data.get('product_category')

    price = None
    if product_price:
        try:
            price = float(product_price)
        except ValueError:
            return jsonify({'error': 'Invalid price format'}), 400

    total_sold = None
    if product_total_sold:
        try:
            total_sold = int(product_total_sold)
        except ValueError:
            return jsonify({'error': 'Invalid total_sold format'}), 400

    result = update_product_in_db(
        product_id=product_id,
        name=product_name,
        price=price,
        total_sold=total_sold,
        category=product_category
    )

    if result is None:
        return jsonify({'error': 'Product not found or update failed'}), 404
    elif result == "invalid_category":
        return jsonify({
            'error': f"Invalid category. Must be one of {list(ProductCategory.__members__.keys())}"
        }), 400

    return jsonify({'message': 'Product updated successfully'}), 200

@coffee_shop_bp.route('/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    user_id = payload.get("user_id")
    user = User.query.get(user_id)
    if not user or not getattr(user, 'is_admin', False):
        return jsonify({"error": "Permission denied. Admins only."}), 403

    success = delete_product_in_db(product_id)
    if success:
        return jsonify({'message': 'Product deleted successfully'}), 200
    else:
        return jsonify({'error': 'Product not found or could not be deleted'}), 404

# -----------------------------------------------------------------------------------------------------------------------------------------

@coffee_shop_bp.route('/create-order-item', methods=['POST'])
def create_order_item():
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    user_id = payload.get("user_id")

    data = request.form
    order_id = data.get("order_id")
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not all([order_id, product_id]):
        return jsonify({"error": "order_id and product_id are required"}), 400

    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    if order.user_id != user_id:
        return jsonify({"error": "Permission denied. You do not own this order."}), 403

    item = add_order_item(order_id, product_id, int(quantity))
    if item:
        return jsonify({"message": "Order item added", "order_item_id": item.id}), 201
    return jsonify({"error": "Failed to add order item"}), 500

@coffee_shop_bp.route('/get-order-item/<int:item_id>', methods=['GET'])
def read_order_item(item_id):
    item = get_order_item_by_id(item_id)
    if not item:
        return jsonify({"error": "Order item not found"}), 404

    return jsonify({
        "id": item.id,
        "order_id": item.order_id,
        "product_id": item.product_id,
        "quantity": item.quantity,
        "unit_price": item.unit_price
    }), 200

@coffee_shop_bp.route('/update-order-item/<int:item_id>', methods=['PATCH'])
def edit_order_item(item_id):
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    user_id = payload.get("user_id")

    data = request.form
    quantity = data.get("quantity")

    if quantity is None:
        return jsonify({"error": "Quantity is required"}), 400

    item = OrderItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Order item not found"}), 404

    if item.order.user_id != user_id:
        return jsonify({"error": "Permission denied. You do not own this order item."}), 403

    updated_item = update_order_item(item_id, quantity=quantity)
    if not updated_item:
        return jsonify({"error": "Failed to update order item"}), 500

    return jsonify({"message": "Order item updated"}), 200

@coffee_shop_bp.route('/remove-order-item/<int:item_id>', methods=['DELETE'])
def remove_order_item(item_id):
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    user_id = payload.get("user_id")

    item = OrderItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Order item not found"}), 404

    if item.order.user_id != user_id:
        return jsonify({"error": "Permission denied. You do not own this order item."}), 403

    success = delete_order_item(item_id)
    if success:
        return jsonify({"message": "Order item deleted"}), 200
    return jsonify({"error": "Failed to delete order item"}), 500

# -----------------------------------------------------------------------------------------------------------------------------------------

@coffee_shop_bp.route('/create-order', methods=['POST'])
def create_order():
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    user_id = payload.get("user_id")

    order, status = add_order(user_id=user_id)
    if status == 0:
        return jsonify({"error": "You Have Open Order"}), 404
    elif status == 1:
        return jsonify({"message": "Order created", "order_id": order.id}), 201
    else:
        return jsonify({"error": "Failed to create order"}), 500

@coffee_shop_bp.route('/delete-order/<int:order_id>', methods=['DELETE'])
def delete_order_api(order_id):
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    user_id = payload.get("user_id")
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.user_id != user_id and not getattr(user, 'is_admin', False):
        return jsonify({"error": "Permission denied"}), 403

    success = delete_order(order_id)
    if success:
        return jsonify({"message": "Order deleted"}), 200
    return jsonify({"error": "Failed to delete order"}), 500

