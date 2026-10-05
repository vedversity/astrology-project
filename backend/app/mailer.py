"""Sends the finished Patrika by email, through any SMTP sender (Brevo, Resend, Gmail ...).

Switched off until these are in backend/.env:

    SMTP_HOST=smtp-relay.brevo.com
    SMTP_PORT=587
    SMTP_USER=...
    SMTP_PASSWORD=...
    MAIL_FROM=Janam Patrika <hello@your-domain.example>

Without them nothing is sent, and the customer still gets the download page.
"""

import os
import smtplib
import ssl
from email.message import EmailMessage

TEXT = {
    "hi": {
        "subject": "आपकी जन्म पत्रिका तैयार है",
        "body": "नमस्ते,\n\nआपकी जन्म पत्रिका इस ईमेल के साथ संलग्न है। आप इसे इस लिंक से भी डाउनलोड कर सकते हैं:\n{link}\n\n"
                "रसीद संख्या: {invoice}\n\nयह पत्रिका मार्गदर्शन के लिए है, गारंटी नहीं।\n\nशुभकामनाओं सहित,\n{brand}",
    },
    "en": {
        "subject": "Your Janam Patrika is ready",
        "body": "Namaste,\n\nYour Janam Patrika is attached to this email. You can also download it here:\n{link}\n\n"
                "Receipt number: {invoice}\n\nThe Patrika is for guidance, not a guarantee.\n\nWith good wishes,\n{brand}",
    },
}


def configured():
    return all(os.environ.get(name) for name in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "MAIL_FROM"))


def send_patrika(to, lang, link, invoice, brand, pdf):
    """Send the PDF. Returns True if sent, False if email is not set up. Raises on a sending error."""
    if not configured() or not to:
        return False
    text = TEXT.get(lang, TEXT["en"])
    message = EmailMessage()
    message["Subject"] = text["subject"]
    message["From"] = os.environ["MAIL_FROM"]
    message["To"] = to
    message.set_content(text["body"].format(link=link, invoice=invoice, brand=brand))
    message.add_attachment(pdf, maintype="application", subtype="pdf", filename="janam-patrika.pdf")
    port = int(os.environ.get("SMTP_PORT", "587"))
    with smtplib.SMTP(os.environ["SMTP_HOST"], port, timeout=30) as server:
        server.starttls(context=ssl.create_default_context())
        server.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        server.send_message(message)
    return True
