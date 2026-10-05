"""Razorpay: creating an order and checking that a payment is genuine.

Nothing here works until the keys are in backend/.env:

    RAZORPAY_KEY_ID=rzp_test_...        (TEST keys first; rzp_live_... when going live)
    RAZORPAY_KEY_SECRET=...
    RAZORPAY_WEBHOOK_SECRET=...         (the secret typed when adding the webhook in Razorpay)

Without keys the site runs in "test" mode on a developer's PC (orders are made
without charging) and refuses orders on the live server.

The rule that keeps money safe: a PDF is released only after a signature made
with our secret has been checked. What the customer's browser says is never trusted.
"""

import hashlib
import hmac
import os

import httpx

API = "https://api.razorpay.com/v1"


def _key_id():
    return os.environ.get("RAZORPAY_KEY_ID", "").strip()


def _key_secret():
    return os.environ.get("RAZORPAY_KEY_SECRET", "").strip()


def mode():
    """"razorpay" = keys present; "test" = no keys, not the live server; "off" = live server without keys."""
    if _key_id() and _key_secret():
        return "razorpay"
    return "off" if os.environ.get("ENV") == "production" else "test"


def public_key():
    """The key id is safe to give to the browser; the secret never leaves the server."""
    return _key_id()


def is_live():
    return _key_id().startswith("rzp_live_")


def create_order(amount_rupees, receipt):
    """Ask Razorpay to open an order. Returns its id. Raises httpx.HTTPError if it cannot."""
    response = httpx.post(
        f"{API}/orders", auth=(_key_id(), _key_secret()), timeout=20,
        json={"amount": amount_rupees * 100, "currency": "INR", "receipt": receipt[:40]})
    response.raise_for_status()
    return response.json()["id"]


def _matches(message, signature, secret):
    if not secret or not signature:
        return False
    expected = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def checkout_is_genuine(gateway_order_id, payment_id, signature):
    """The signature the browser hands back after a payment."""
    return _matches(f"{gateway_order_id}|{payment_id}".encode(), signature, _key_secret())


def webhook_is_genuine(body, signature):
    """The signature Razorpay puts on a webhook call (header X-Razorpay-Signature)."""
    return _matches(body, signature, os.environ.get("RAZORPAY_WEBHOOK_SECRET", "").strip())
