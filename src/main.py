from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from src.database import engine, get_db, Base
from src.schemas import SearchQueryCreate, SearchQueryOut, ProductOut, PriceHistoryOut
from src.scraper import scrape_trendyol
from src.scheduler import run_daily_check
from src.queries import search_queries as sq, product_queries as pq


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Trendyol Price Tracker", lifespan=lifespan)


@app.post("/search-queries", response_model=SearchQueryOut)
def create_search_query(data: SearchQueryCreate, db: Session = Depends(get_db)):
    return sq.create_query(db, data)


@app.get("/search-queries", response_model=list[SearchQueryOut])
def list_search_queries(db: Session = Depends(get_db)):
    return sq.get_all_queries(db)


@app.get("/search-queries/{query_id}", response_model=SearchQueryOut)
def get_search_query(query_id: int, db: Session = Depends(get_db)):
    return sq.get_query(db, query_id)


@app.post("/search-queries/{query_id}/toggle")
def toggle_search_query(query_id: int, db: Session = Depends(get_db)):
    query = sq.toggle_query(db, query_id)
    return {"active": query.is_active if query else False}


@app.delete("/search-queries/{query_id}")
def delete_search_query(query_id: int, db: Session = Depends(get_db)):
    ok = sq.delete_query(db, query_id)
    return {"ok": ok}


@app.post("/scrape")
def scrape_now(
    keyword: str = Query(...),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
):
    results = scrape_trendyol(keyword, min_price, max_price)
    return {"results": results}


@app.post("/run-daily-check")
def trigger_daily_check():
    run_daily_check()
    return {"ok": True}


@app.get("/products", response_model=list[ProductOut])
def list_products(query_id: Optional[int] = None, db: Session = Depends(get_db)):
    return pq.get_products(db, query_id)


@app.get("/products/{product_id}/history", response_model=list[PriceHistoryOut])
def product_price_history(product_id: int, db: Session = Depends(get_db)):
    return pq.get_price_history(db, product_id)
