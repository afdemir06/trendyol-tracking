# Trendyol Price Tracker

Trendyol is one of the largest e-commerce platforms in Turkey, and prices on it change frequently. Checking products manually every day is tedious, and its easy to miss a good deal. This project automates that process - you tell it what products you are interested in via search keywords, and it scrapes Trendyol daily, records prices to a database, and sends you an email whenever a price change is detected.

## Tech Stack

- **Python** — core language
- **FastAPI** — backend API with auto-generated OpenAPI docs
- **Streamlit** — frontend UI for managing queries and viewing data
- **SQLAlchemy + SQLite** — ORM and database
- **Selenium** — browser automation for scraping Trendyol
- **Docker** — containerized deployment with docker-compose
- **SMTP** — email notifications for price alerts
- **Schedule** — in-process task scheduler for daily checks

## Quick Start

```bash
# Clone and enter the project
git clone https://github.com/afdemir06/trendyol-tracking.git
cd trendyol-price-tracker

# Configure email (optional)
cp .env.example .env
# Edit .env with your SMTP credentials

# With Docker
docker compose up -d
# Open http://localhost:8501

# Or without Docker (local development)
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\uvicorn src.main:app --reload     # Terminal 1
.venv\Scripts\streamlit run streamlit_app/app.py # Terminal 2
```

## How It Works

1. Add search keywords (e.g. `kulaklık`, `telefon`, `saat`) and optional price filters through the Streamlit UI
2. The FastAPI backend uses Selenium to scrape Trendyol search results and stores products with their prices in SQLite
3. A daily scheduler runs at 09:00, re-scrapes all active queries, compares prices, and logs any changes
4. If a price change is found, an email notification is sent via SMTP with the old and new prices

## Email Setup

Copy `.env.example` to `.env` and fill in your SMTP credentials:

| Variable | Description |
|---|---|
| `SMTP_SERVER` | SMTP server (e.g. `smtp.gmail.com`) |
| `SMTP_PORT` | SMTP port (e.g. `587`) |
| `EMAIL_ADDRESS` | Your email address |
| `EMAIL_PASSWORD` | App password (not regular password) |
| `TO_EMAIL` | Recipient email for alerts |

## Project Structure

```
├── src/                    # Backend
│   ├── main.py             # FastAPI endpoints
│   ├── database.py         # SQLite connection
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── scraper.py          # Selenium scraper
│   ├── notifier.py         # Email notifications
│   ├── scheduler.py        # Daily check scheduler
│   └── queries/            # DB query helpers
├── streamlit_app/
│   └── app.py              # UI
├── data/                   # SQLite database
├── logs/                   # Scheduler logs
├── Dockerfile.api
├── Dockerfile.streamlit
└── docker-compose.yml
```
