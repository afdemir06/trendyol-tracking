import datetime
from sqlalchemy.orm import Session
from src.models import Product, PriceHistory
from typing import Optional


def get_products(db: Session, query_id: Optional[int] = None) -> list[Product]:
    q = db.query(Product)
    if query_id:
        q = q.filter(Product.search_query_id == query_id)
    return q.all()


def get_product_by_url(db: Session, url: str) -> Optional[Product]:
    return db.query(Product).filter(Product.product_url == url).first()


def create_product(db: Session, **kwargs) -> Product:
    product = Product(**kwargs)
    db.add(product)
    db.flush()
    return product


def update_product_price(db: Session, product: Product, new_price: float) -> Product:
    product.current_price = new_price
    product.last_checked = datetime.datetime.now(datetime.timezone.utc)
    db.flush()
    return product


def add_price_history(db: Session, product_id: int, price: float) -> PriceHistory:
    history = PriceHistory(product_id=product_id, price=price)
    db.add(history)
    db.flush()
    return history


def get_price_history(db: Session, product_id: int) -> list[PriceHistory]:
    return (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.checked_at)
        .all()
    )
