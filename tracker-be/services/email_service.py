import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    @staticmethod
    def send_email(subject: str, body: str) -> bool:
        """Send email using SMTP with provided credentials."""
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        email_from = os.getenv("EMAIL_FROM")
        email_to = os.getenv("EMAIL_TO")

        if not all(
            [smtp_host, smtp_port, smtp_user, smtp_password, email_from, email_to]
        ):
            print("Error: Missing SMTP configuration in .env")
            return False

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = email_from
        msg["To"] = email_to

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            print(f"Email sent successfully to {email_to}")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
