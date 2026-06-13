from sqlalchemy.orm import Session
from src.models import SearchQuery
from src.schemas import SearchQueryCreate
from src.decorators import log_call
from typing import Optional


@log_call
def create_query(db: Session, data: SearchQueryCreate) -> SearchQuery:
    query = SearchQuery(**data.model_dump())
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


@log_call
def get_all_queries(db: Session) -> list[SearchQuery]:
    return db.query(SearchQuery).all()


@log_call
def get_query(db: Session, query_id: int) -> Optional[SearchQuery]:
    return db.query(SearchQuery).filter(SearchQuery.id == query_id).first()


@log_call
def toggle_query(db: Session, query_id: int) -> SearchQuery:
    query = db.query(SearchQuery).filter(SearchQuery.id == query_id).first()
    if query:
        query.is_active = not query.is_active
        db.commit()
    return query


@log_call
def delete_query(db: Session, query_id: int) -> bool:
    query = db.query(SearchQuery).filter(SearchQuery.id == query_id).first()
    if query:
        db.delete(query)
        db.commit()
        return True
    return False


@log_call
def get_active_queries(db: Session) -> list[SearchQuery]:
    return db.query(SearchQuery).filter(SearchQuery.is_active == True).all()
