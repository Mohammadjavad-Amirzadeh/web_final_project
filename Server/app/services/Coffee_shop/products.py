from ...models.shop import Product
from ...extensions import db
from sqlalchemy.exc import IntegrityError
from ...models.shop import ProductCategory

# Create
def add_product_in_db(name: str, price: float, product_category: str, total_sold: int = 0):
    try:
        category_key = product_category.strip().upper()

        if category_key not in ProductCategory.__members__:
            raise ValueError(f"Invalid category '{product_category}'. Must be one of {list(ProductCategory.__members__.keys())}")

        category_enum = ProductCategory[category_key]

        product = Product(name=name, price=price, category=category_enum, total_sold=total_sold)
        db.session.add(product)
        db.session.commit()
        return True
    except (IntegrityError, ValueError) as err:
        db.session.rollback()
        print(f"Error adding product: {err}")
        return False

# Read
def get_product_by_id_in_db(product_id: int):
    return Product.query.get(product_id)
def get_all_products_in_db():
    return Product.query.all()

# Update
def update_product_in_db(product_id: int, name: str = None, price: float = None, total_sold: int = None, category: str = None):
    product = Product.query.get(product_id)
    if not product:
        return None

    if name is not None:
        product.name = name
    if price is not None:
        product.price = price
    if total_sold is not None:
        product.total_sold = total_sold
    if category is not None:
        category_key = category.strip().upper()
        if category_key not in ProductCategory.__members__:
            return "invalid_category"
        product.category = ProductCategory[category_key]

    try:
        db.session.commit()
        return product
    except IntegrityError:
        db.session.rollback()
        return None

# Delete
def delete_product_in_db(product_id: int):
    product = Product.query.get(product_id)
    if not product:
        return False

    try:
        db.session.delete(product)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False
