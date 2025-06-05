from ...models.shop import Product
from ...extensions import db


def add_product(name: str, price: float, total_sold: int = 0):
    product = Product(name=name, price=price, total_sold=total_sold)
    db.session.add(product)
    db.session.commit()
    return product