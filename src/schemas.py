from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SearchQueryCreate(BaseModel):
    keyword: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None


class SearchQueryOut(BaseModel):
    id: int
    keyword: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductOut(BaseModel):
    id: int
    product_url: str
    title: str
    current_price: float
    currency: str
    image_url: Optional[str] = None
    last_checked: datetime

    model_config = {"from_attributes": True}


class PriceHistoryOut(BaseModel):
    id: int
    price: float
    checked_at: datetime

    model_config = {"from_attributes": True}
