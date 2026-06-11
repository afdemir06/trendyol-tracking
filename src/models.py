import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from src.database import Base


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, nullable=False)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    products = relationship("Product", back_populates="search_query", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    search_query_id = Column(Integer, ForeignKey("search_queries.id"), nullable=False)
    product_url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    current_price = Column(Float, nullable=False)
    currency = Column(String, default="TL")
    image_url = Column(String, nullable=True)
    last_checked = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    search_query = relationship("SearchQuery", back_populates="products")
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Float, nullable=False)
    checked_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    product = relationship("Product", back_populates="price_history")
