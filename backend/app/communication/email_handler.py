"""Email handling — send and read emails via SMTP/IMAP."""

from __future__ import annotations

import email
import imaplib
import smtplib
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_settings
from app.utils.logger import setup_logger

logger = setup_logger("jarvis.communication.email")


@dataclass
class EmailMessage:
    """An email message."""

    subject: str
    sender: str
    to: str
    body: str
    date: str = ""
    is_read: bool = False


class EmailHandler:
    """Send and read emails."""

    def __init__(self) -> None:
        settings = get_settings()
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.email_address = settings.email_address
        self.email_password = settings.email_password

    @property
    def is_configured(self) -> bool:
        """Check if email is configured."""
        return bool(self.email_address and self.email_password)

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> dict[str, str]:
        """Send an email."""
        if not self.is_configured:
            return {"status": "error", "message": "Email not configured"}

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.email_address
            msg["To"] = to
            msg["Subject"] = subject

            content_type = "html" if html else "plain"
            msg.attach(MIMEText(body, content_type))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)  # type: ignore[arg-type]
                server.send_message(msg)

            logger.info(f"Email sent to {to}: {subject}")
            return {"status": "success", "message": f"Email sent to {to}"}
        except Exception as exc:
            logger.error(f"Failed to send email: {exc}")
            return {"status": "error", "message": str(exc)}

    def read_emails(
        self, folder: str = "INBOX", limit: int = 10
    ) -> list[EmailMessage]:
        """Read recent emails from the mailbox."""
        if not self.is_configured:
            return []

        try:
            imap_host = self.smtp_host.replace("smtp", "imap")
            with imaplib.IMAP4_SSL(imap_host) as imap:
                imap.login(self.email_address, self.email_password)  # type: ignore[arg-type]
                imap.select(folder)

                _, msg_ids = imap.search(None, "ALL")
                ids = msg_ids[0].split()[-limit:]

                messages: list[EmailMessage] = []
                for msg_id in reversed(ids):
                    _, data = imap.fetch(msg_id, "(RFC822)")
                    raw = data[0][1]  # type: ignore[index]
                    msg = email.message_from_bytes(raw)  # type: ignore[arg-type]

                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(  # type: ignore[union-attr]
                                    errors="replace"
                                )
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors="replace")  # type: ignore[union-attr]

                    messages.append(
                        EmailMessage(
                            subject=msg.get("Subject", ""),
                            sender=msg.get("From", ""),
                            to=msg.get("To", ""),
                            body=body[:500],
                            date=msg.get("Date", ""),
                        )
                    )

                return messages
        except Exception as exc:
            logger.error(f"Failed to read emails: {exc}")
            return []
