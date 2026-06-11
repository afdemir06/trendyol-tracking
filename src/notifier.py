import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


def send_price_alert(products_with_changes: list[dict]) -> bool:
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    to_email = os.getenv("TO_EMAIL")

    if not all([email_address, email_password, to_email]):
        print("Email settings incomplete. Set SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD, TO_EMAIL in .env")
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

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
        print(f"Price alert email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
