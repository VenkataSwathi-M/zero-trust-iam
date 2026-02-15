import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from pathlib import Path

# ✅ force .env from project root
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

GMAIL_USER = (os.getenv("GMAIL_USER") or "").strip()
GMAIL_PASS = (os.getenv("GMAIL_APP_PASSWORD") or "").strip()

def send_otp_email(to_email: str, otp: str):
    if not GMAIL_USER or not GMAIL_PASS:
        raise RuntimeError(f"Missing GMAIL_USER or GMAIL_APP_PASSWORD in {ENV_PATH}")

    msg = MIMEText(f"Your OTP is: {otp}\nValid for 5 minutes.")
    msg["Subject"] = "Your Agent Login OTP"
    msg["From"] = GMAIL_USER
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)