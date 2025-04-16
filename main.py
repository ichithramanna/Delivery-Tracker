# main.py
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import sqlite3
import time
from dotenv import load_dotenv
import os
from email_alert import send_email

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "database.db")
ORDERS_CSV = os.getenv("ORDERS_CSV", "orders.csv")

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer TEXT,
            status TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def load_orders():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    df = pd.read_csv(ORDERS_CSV)
    for row in df.itertuples(index=False):
        cur.execute(
            "INSERT OR IGNORE INTO orders (order_id, customer, status) VALUES (?, ?, ?)",
            (row.order_id, row.customer, row.status)
        )
    conn.commit()
    conn.close()

def update_status():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cur.execute(
        "SELECT order_id, customer FROM orders WHERE status <> 'Delivered'"
    )
    rows = cur.fetchall()
    if rows:
        for order_id, customer in rows:
            cur.execute(
                "UPDATE orders SET status = 'Delivered' WHERE order_id = ?", (order_id,)
            )
            send_email(customer, order_id)
        conn.commit()
    conn.close()

init_db()
load_orders()
scheduler = BackgroundScheduler()
scheduler.add_job(update_status, 'interval', seconds=30)
scheduler.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    scheduler.shutdown()

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

# orders.csv (sample)
order_id,customer,status
A001,customer1@example.com,Shipped
A002,customer2@example.com,Processing
A003,customer3@example.com,Processing

# requirements.txt
pandas
APScheduler
python-dotenv

# README.md
# AutoTrack

##Smart Python-based delivery/order tracker.

## Features
- Read orders from `orders.csv`
- Store and manage orders in SQLite (`database.db`)
- Send email alerts when status changes to delivered
- Automate checks using APScheduler

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file:
```bash
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
EMAIL_USER=you@example.com
EMAIL_PASS=your_email_password
DB_PATH=database.db       # optional
ORDERS_CSV=orders.csv     # optional
```

3. Populate `orders.csv` with your orders.

4. Run:
```bash
python main.py
```
