import logging
import os
import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException


def extract_price(text: str) -> Optional[float]:
    cleaned = text.replace(".", "").replace(",", ".").strip()
    digits = "".join(c for c in cleaned if c.isdigit() or c == ".")
    try:
        return float(digits)
    except ValueError:
        return None


def scrape_trendyol(keyword: str, min_price: Optional[float] = None, max_price: Optional[float] = None):
    logger = logging.getLogger(__name__)

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.page_load_strategy = "eager"
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    remote_url = os.environ.get("SELENIUM_REMOTE_URL")
    try:
        if remote_url:
            driver = webdriver.Remote(command_executor=remote_url, options=options)
        else:
            driver = webdriver.Chrome(options=options)
    except WebDriverException as e:
        logger.error("Failed to launch browser: %s", e)
        return []

    driver.set_page_load_timeout(30)
    results = []
    seen_links = set()

    try:
        url = f"https://www.trendyol.com/sr?q={keyword.replace(' ', '%20')}"
        driver.get(url)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.product-card"))
        )
        time.sleep(1)

        for _ in range(2):
            cards = driver.find_elements(By.CSS_SELECTOR, "a.product-card")

            for card in cards:
                try:
                    link = card.get_attribute("href")
                    if link in seen_links:
                        continue
                    seen_links.add(link)

                    brand = card.find_element(By.CSS_SELECTOR, "span.product-brand").text
                    name = card.find_element(By.CSS_SELECTOR, "span.product-name").text
                    title = f"{brand} {name}".strip()

                    price_text = card.find_element(By.CSS_SELECTOR, "div.price-section").text
                    price = extract_price(price_text)
                    if not price:
                        continue
                    if min_price and price < min_price:
                        continue
                    if max_price and price > max_price:
                        continue

                    try:
                        img_el = card.find_element(By.CSS_SELECTOR, "img.image")
                        img_url = img_el.get_attribute("src") or ""
                    except NoSuchElementException:
                        img_url = ""

                    results.append({
                        "title": title,
                        "product_url": link,
                        "current_price": price,
                        "currency": "TL",
                        "image_url": img_url,
                    })
                except NoSuchElementException:
                    continue

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

    except TimeoutException:
        logger.error("Timeout while scraping '%s'", keyword)
    except WebDriverException as e:
        logger.error("Browser error while scraping '%s': %s", keyword, e)
    finally:
        driver.quit()

    return results
