# backend/smtp_test.py
import os
from dotenv import load_dotenv
import smtplib, ssl
from email.message import EmailMessage

load_dotenv()

smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT", "587"))
smtp_user = os.getenv("SMTP_USER")
smtp_password = os.getenv("SMTP_PASSWORD")

def main():
    print("SMTP config:")
    print("  SMTP_SERVER=", smtp_server)
    print("  SMTP_PORT=", smtp_port)
    print("  SMTP_USER=", smtp_user)

    if not smtp_server or not smtp_user or not smtp_password:
        print("Missing SMTP configuration. Create backend/.env with SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD")
        return

    msg = EmailMessage()
    msg["Subject"] = "SMTP test"
    msg["From"] = smtp_user
    msg["To"] = smtp_user
    msg.set_content("This is a test email from your app.")

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as s:
            s.starttls(context=ctx)
            s.login(smtp_user, smtp_password)
            s.send_message(msg)
        print("Email sent OK")
    except Exception as e:
        print("Email send failed:", repr(e))

if __name__ == '__main__':
    main()
