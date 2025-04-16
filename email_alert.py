# email_alert.py
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_email(customer_email, order_id):
    try:
        msg = MIMEText(
            f"Hello,\n\nYour order with ID {order_id} is now delivered. Thank you for using AutoTrack!\n\nBest regards,\nAutoTrack Bot"
        )
        msg["Subject"] = f"Your Order {order_id} has been delivered!"
        msg["From"] = EMAIL_USER
        msg["To"] = customer_email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
    except Exception:
        pass
