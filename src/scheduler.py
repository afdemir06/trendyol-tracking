import datetime
import os
import schedule
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.database import SessionLocal
from src.queries.search_queries import get_active_queries
from src.queries.product_queries import (
    get_product_by_url,
    create_product,
    add_price_history,
)
from src.scraper import scrape_trendyol
from src.notifier import send_price_alert
from src.decorators import log_call

os.makedirs("logs", exist_ok=True)


@log_call
def run_daily_check():
    db = SessionLocal()

    try:
        queries = get_active_queries(db)
        changes = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_map = {
                executor.submit(scrape_trendyol, q.keyword, q.min_price, q.max_price): q
                for q in queries
            }
            for future in as_completed(future_map):
                query = future_map[future]
                try:
                    scraped = future.result()
                except Exception:
                    continue

                for item in scraped:
                    existing = get_product_by_url(db, item["product_url"])

                    if existing:
                        old_price = existing.current_price
                        if abs(old_price - item["current_price"]) > 0.01:
                            existing.current_price = item["current_price"]
                            existing.last_checked = datetime.datetime.now(datetime.timezone.utc)
                            add_price_history(db, existing.id, item["current_price"])

                            changes.append({
                                "title": item["title"],
                                "old_price": old_price,
                                "new_price": item["current_price"],
                                "url": item["product_url"],
                            })
                    else:
                        product = create_product(
                            db,
                            search_query_id=query.id,
                            product_url=item["product_url"],
                            title=item["title"],
                            current_price=item["current_price"],
                            currency=item.get("currency", "TL"),
                            image_url=item.get("image_url"),
                            last_checked=datetime.datetime.now(datetime.timezone.utc),
                        )
                        add_price_history(db, product.id, item["current_price"])

                db.commit()

        if not changes:
            return

        send_price_alert(changes)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def start_scheduler():
    schedule.every().day.at("09:00").do(run_daily_check)

    while True:
        schedule.run_pending()
        time.sleep(60)
