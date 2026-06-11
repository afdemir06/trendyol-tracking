import datetime
import logging
import os
import schedule
import time

from src.database import SessionLocal
from src.queries.search_queries import get_active_queries
from src.queries.product_queries import (
    get_product_by_url,
    create_product,
    add_price_history,
)
from src.scraper import scrape_trendyol
from src.notifier import send_price_alert

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/scheduler.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run_daily_check():
    logger.info("Starting daily price check...")
    db = SessionLocal()

    try:
        queries = get_active_queries(db)
        changes = []

        for query in queries:
            logger.info("Scraping: %s", query.keyword)
            scraped = scrape_trendyol(query.keyword, query.min_price, query.max_price)

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

        if changes:
            send_price_alert(changes)
        else:
            logger.info("No price changes detected.")

    except Exception as e:
        logger.error("Error during daily check: %s", e)
        db.rollback()
    finally:
        db.close()

    logger.info("Daily check finished.")


def start_scheduler():
    schedule.every().day.at("09:00").do(run_daily_check)
    logger.info("Scheduler started. Will run daily at 09:00.")

    while True:
        schedule.run_pending()
        time.sleep(60)
