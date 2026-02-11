# iam_core/security/email_service.py
import os, smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

def send_otp_email(to_email: str, otp: str):
    user = os.getenv("GMAIL_USER")
    app_pass = os.getenv("GMAIL_APP_PASSWORD")

    if not user or not app_pass:
        raise RuntimeError("GMAIL_USER / GMAIL_APP_PASSWORD missing")

    app_pass = app_pass.replace(" ", "")  # safe

    msg = MIMEText(f"Your OTP is: {otp}\nValid 5 minutes.")
    msg["Subject"] = "Agent Login OTP"
    msg["From"] = user
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(user, app_pass)
        server.send_message(msg)