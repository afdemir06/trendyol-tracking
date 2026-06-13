import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from src.decorators import log_call

load_dotenv()


@log_call
def send_price_alert(products_with_changes: list[dict]) -> bool:
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    to_email = os.getenv("TO_EMAIL")

    if not all([email_address, email_password, to_email]):
        return False

    subject = "Trendyol Price Tracker - Price Changes Detected"
    body_lines = ["The following products have price changes:\n"]
    for item in products_with_changes:
        body_lines.extend([
            f"Product: {item['title']}",
            f"Old Price: {item.get('old_price', 'N/A')} TL",
            f"New Price: {item['new_price']} TL",
            f"URL: {item['url']}",
            "-" * 40,
        ])
    body = "\n".join(body_lines)

    msg = MIMEMultipart()
    msg["From"] = email_address
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_address, email_password)
        server.send_message(msg)
    return True
