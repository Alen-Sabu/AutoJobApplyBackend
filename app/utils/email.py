"""
Simple email sending utility using SMTP.
"""
import smtplib
from email.message import EmailMessage

from app.core.config import settings
from app.utils.logger import logger


def send_email(to_email: str, subject: str, text_body: str, html_body: str | None = None) -> None:
    """
    Send an email using SMTP settings from configuration.

    If SMTP_HOST is not configured, logs a warning and does not raise, so local
    development can proceed without a mail server.
    """
    if not settings.SMTP_HOST:
        logger.warning("SMTP_HOST not configured; skipping email to %s with subject '%s'", to_email, subject)
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg.set_content(text_body)

    if html_body:
        msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as exc:  # pragma: no cover - network dependent
        logger.error("Failed to send email to %s: %s", to_email, exc)
        raise

