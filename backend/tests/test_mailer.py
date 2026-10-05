"""The email that carries the Patrika. A stand-in takes the place of the mail server."""

import smtplib

import pytest

from app import mailer

SETTINGS = {"SMTP_HOST": "smtp.example.test", "SMTP_PORT": "2525", "SMTP_USER": "user",
            "SMTP_PASSWORD": "secret", "MAIL_FROM": "Janam Patrika <hello@example.test>"}


class FakeServer:
    log = []

    def __init__(self, host, port, timeout):
        FakeServer.log.append(("connect", host, port))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        FakeServer.log.append(("quit",))

    def starttls(self, context):
        FakeServer.log.append(("starttls",))

    def login(self, user, password):
        FakeServer.log.append(("login", user, password))

    def send_message(self, message):
        FakeServer.log.append(("send", message))


@pytest.fixture
def server(monkeypatch):
    FakeServer.log = []
    monkeypatch.setattr(smtplib, "SMTP", FakeServer)
    for name, value in SETTINGS.items():
        monkeypatch.setenv(name, value)
    return FakeServer


def test_nothing_is_sent_until_email_is_set_up(monkeypatch, server):
    monkeypatch.delenv("SMTP_PASSWORD")
    assert mailer.configured() is False
    assert mailer.send_patrika("a@b.co", "hi", "https://x/y", "JP-1", "Brand", b"%PDF") is False
    assert server.log == []


def test_no_address_means_no_email(server):
    assert mailer.send_patrika(None, "hi", "https://x/y", "JP-1", "Brand", b"%PDF") is False
    assert server.log == []


@pytest.mark.parametrize("lang,subject", [("hi", "आपकी जन्म पत्रिका तैयार है"), ("en", "Your Janam Patrika is ready")])
def test_email_carries_the_link_the_receipt_number_and_the_pdf(server, lang, subject):
    link = "https://site.example/thank-you?order=abc"
    assert mailer.send_patrika("rohan@example.com", lang, link, "JP-2026-000007", "पत्रिका सेतु", b"%PDF-1.4 data") is True
    steps = [entry[0] for entry in server.log]
    assert steps == ["connect", "starttls", "login", "send", "quit"]          # encrypted before the password is sent
    assert server.log[0] == ("connect", "smtp.example.test", 2525) and server.log[2] == ("login", "user", "secret")
    message = server.log[3][1]
    assert message["To"] == "rohan@example.com" and message["Subject"] == subject
    assert message["From"] == "Janam Patrika <hello@example.test>"
    body = message.get_body(preferencelist=("plain",)).get_content()
    assert link in body and "JP-2026-000007" in body and "पत्रिका सेतु" in body
    attachment = next(message.iter_attachments())
    assert attachment.get_filename() == "janam-patrika.pdf" and attachment.get_content_type() == "application/pdf"
    assert attachment.get_content() == b"%PDF-1.4 data"
