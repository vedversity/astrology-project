"""Orders, payment checks, delivery, coupons and the owner's view.

No real payment service, browser or email is touched: Razorpay's order call and
the PDF maker are replaced by stand-ins, and the database is a temporary file.
"""

import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from app import orders, payments, store
from app.main import app

ADMIN = {"X-Admin-Token": "a-long-test-password"}
SECRET = "test-key-secret"
WEBHOOK_SECRET = "test-webhook-secret"
ORDER = {
    "date": "1990-01-15", "time": "04:30", "latitude": 28.6139, "longitude": 77.2090, "timezone": "Asia/Kolkata",
    "gender": "male", "variant": "full", "lang": "en", "child_name": "Rohan Sharma", "surname": "Sharma",
    "whatsapp": "9876543210", "email": "rohan@example.com", "consent": True,
}
BABY = {**ORDER, "date": "2026-09-27", "time": "20:00", "variant": "premium"}


@pytest.fixture
def shop(tmp_path, monkeypatch):
    """A client with an empty database and a stand-in PDF maker that counts its calls."""
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "app.db"))
    monkeypatch.setenv("ADMIN_TOKEN", ADMIN["X-Admin-Token"])
    for name in ("RAZORPAY_KEY_ID", "RAZORPAY_KEY_SECRET", "RAZORPAY_WEBHOOK_SECRET", "ENV"):
        monkeypatch.delenv(name, raising=False)
    made = []

    def fake_pdf(report, person, variant, lang):
        made.append((variant, lang, report["audience"]))
        return b"%PDF-fake " + variant.encode()

    monkeypatch.setattr(orders, "generate_pdf", fake_pdf)
    monkeypatch.setattr(orders, "html_to_pdf", lambda html: b"%PDF-receipt " + html[:0].encode())
    orders.order_limit.seen.clear()
    client = TestClient(app)
    client.made = made
    return client


@pytest.fixture
def paid_shop(shop, monkeypatch):
    """The same, with Razorpay keys set: real payment is required."""
    monkeypatch.setenv("RAZORPAY_KEY_ID", "rzp_test_abc123")
    monkeypatch.setenv("RAZORPAY_KEY_SECRET", SECRET)
    monkeypatch.setenv("RAZORPAY_WEBHOOK_SECRET", WEBHOOK_SECRET)
    counter = iter(range(1, 1000))
    asked = []

    def fake_create(amount, receipt):
        asked.append(amount)
        return f"order_T{next(counter)}"

    monkeypatch.setattr(payments, "create_order", fake_create)
    shop.asked = asked
    return shop


def sign(gateway_order_id, payment_id, secret=SECRET):
    return hmac.new(secret.encode(), f"{gateway_order_id}|{payment_id}".encode(), hashlib.sha256).hexdigest()


def webhook(client, gateway_order_id, payment_id="pay_W1", event_id="evt_1", secret=WEBHOOK_SECRET):
    body = json.dumps({"event": "payment.captured",
                       "payload": {"payment": {"entity": {"id": payment_id, "order_id": gateway_order_id}}}}).encode()
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return client.post("/webhooks/razorpay", content=body, headers={
        "X-Razorpay-Signature": signature, "X-Razorpay-Event-Id": event_id, "Content-Type": "application/json"})


# ---------- test mode (no keys): the order is delivered without charging ----------

def test_test_mode_delivers_without_payment(shop):
    assert shop.get("/site").json()["payments"] == "test"
    placed = shop.post("/orders", json=ORDER).json()
    assert placed["checkout"] is None and placed["order"]["test"] is True
    order_id = placed["order"]["id"]
    status = shop.get(f"/orders/{order_id}").json()
    assert status["status"] == "delivered" and status["amount"] == 101 and status["invoice_no"].startswith("JP-")
    assert shop.made == [("full", "en", "adult")]
    pdf = shop.get(f"/orders/{order_id}/pdf")
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF-fake")
    assert shop.get(f"/orders/{order_id}/receipt").content.startswith(b"%PDF-receipt")


def test_the_browser_never_sees_personal_details(shop):
    order_id = shop.post("/orders", json=ORDER).json()["order"]["id"]
    public = json.dumps(shop.get(f"/orders/{order_id}").json())
    for private in ("Rohan", "9876543210", "rohan@example.com", "1990-01-15"):
        assert private not in public
    assert len(order_id) >= 30                                   # long enough that it cannot be guessed
    assert shop.get("/orders/not-a-real-order").status_code == 404


@pytest.mark.parametrize("change", [
    {"consent": False}, {"whatsapp": "12345"}, {"whatsapp": "5876543210"}, {"email": "not-an-email"},
    {"variant": "gold"}, {"variant": "premium"},                 # premium is for a child; this birth is an adult's
])
def test_bad_orders_are_refused(shop, change):
    assert shop.post("/orders", json={**ORDER, **change}).status_code == 422
    assert shop.made == []


def test_premium_is_allowed_for_a_child(shop):
    placed = shop.post("/orders", json=BABY).json()
    assert placed["order"]["amount"] == 251 and shop.made == [("premium", "en", "child")]


# ---------- coupons ----------

def test_coupons(shop):
    assert shop.post("/admin/coupons", json={"code": "diwali20", "percent": 20, "max_uses": 2}, headers=ADMIN).status_code == 200
    assert shop.post("/admin/coupons", json={"code": "FREE", "percent": 100}, headers=ADMIN).status_code == 200
    check = shop.post("/coupons/check", json={"code": "Diwali20", "plan": "full"}).json()
    assert check == {"code": "DIWALI20", "price": 101, "discount": 20, "amount": 81}
    assert shop.post("/coupons/check", json={"code": "NOPE", "plan": "full"}).status_code == 422

    first = shop.post("/orders", json={**ORDER, "coupon": "diwali20"}).json()["order"]
    assert (first["price"], first["discount"], first["amount"]) == (101, 20, 81)
    shop.post("/orders", json={**ORDER, "coupon": "DIWALI20"})
    assert shop.post("/orders", json={**ORDER, "coupon": "DIWALI20"}).status_code == 422      # used up
    assert shop.post("/orders", json={**ORDER, "coupon": "WRONG"}).status_code == 422
    coupons = {c["code"]: c for c in shop.get("/admin/coupons", headers=ADMIN).json()}
    assert coupons["DIWALI20"]["used"] == 2
    assert shop.delete("/admin/coupons/FREE", headers=ADMIN).status_code == 200
    assert shop.post("/admin/coupons", json={"code": "x", "percent": 150}, headers=ADMIN).status_code == 422
    assert shop.get("/admin/coupons").status_code == 401


# ---------- real payment ----------

def test_payment_flow_with_a_genuine_signature(paid_shop):
    assert paid_shop.get("/site").json()["payments"] == "razorpay"
    placed = paid_shop.post("/orders", json=ORDER).json()
    order_id, checkout = placed["order"]["id"], placed["checkout"]
    assert checkout == {"key": "rzp_test_abc123", "order_id": "order_T1", "amount": 10100, "currency": "INR"}
    assert paid_shop.asked == [101] and placed["order"]["status"] == "created" and placed["order"]["test"] is False
    # Nothing is released before payment
    assert paid_shop.get(f"/orders/{order_id}/pdf").status_code == 404 and paid_shop.made == []

    bad = paid_shop.post(f"/orders/{order_id}/verify", json={"razorpay_payment_id": "pay_1", "razorpay_signature": "forged"})
    assert bad.status_code == 400 and paid_shop.made == []
    wrong_secret = sign("order_T1", "pay_1", secret="someone-elses-secret")
    assert paid_shop.post(f"/orders/{order_id}/verify", json={"razorpay_payment_id": "pay_1", "razorpay_signature": wrong_secret}).status_code == 400

    proof = {"razorpay_payment_id": "pay_1", "razorpay_signature": sign("order_T1", "pay_1")}
    assert paid_shop.post(f"/orders/{order_id}/verify", json=proof).status_code == 200
    assert paid_shop.get(f"/orders/{order_id}").json()["status"] == "delivered"
    assert paid_shop.get(f"/orders/{order_id}/pdf").status_code == 200
    # Reporting the same payment again does not make a second PDF
    paid_shop.post(f"/orders/{order_id}/verify", json=proof)
    assert len(paid_shop.made) == 1


def test_a_signature_for_one_order_cannot_pay_for_another(paid_shop):
    cheap = paid_shop.post("/orders", json={**ORDER, "variant": "mini"}).json()
    dear = paid_shop.post("/orders", json=ORDER).json()
    proof = {"razorpay_payment_id": "pay_9", "razorpay_signature": sign(cheap["checkout"]["order_id"], "pay_9")}
    assert paid_shop.post(f"/orders/{dear['order']['id']}/verify", json=proof).status_code == 400
    assert paid_shop.made == []


def test_webhook_delivers_and_is_safe_against_repeats(paid_shop):
    placed = paid_shop.post("/orders", json=ORDER).json()
    order_id, gateway = placed["order"]["id"], placed["checkout"]["order_id"]
    assert webhook(paid_shop, gateway, secret="forged-secret").status_code == 400
    assert paid_shop.made == []
    assert webhook(paid_shop, gateway).json() == {"ok": True}
    assert paid_shop.get(f"/orders/{order_id}").json()["status"] == "delivered"
    assert webhook(paid_shop, gateway).json()["repeat"] is True                      # same event again
    assert webhook(paid_shop, gateway, event_id="evt_2").json() == {"ok": True}      # a second event, same payment
    # The browser reporting it afterwards changes nothing either
    proof = {"razorpay_payment_id": "pay_W1", "razorpay_signature": sign(gateway, "pay_W1")}
    paid_shop.post(f"/orders/{order_id}/verify", json=proof)
    assert len(paid_shop.made) == 1
    assert webhook(paid_shop, "order_unknown", event_id="evt_3").status_code == 200  # not ours: ignored quietly


def test_free_reports_are_closed_once_payments_are_on(paid_shop, monkeypatch):
    body = {k: ORDER[k] for k in ("date", "time", "latitude", "longitude", "gender")}
    assert paid_shop.post("/pdf", json=body).status_code == 403
    assert paid_shop.post("/report", json=body).status_code == 403
    assert paid_shop.post("/preview", json=body).status_code == 200                  # the free preview stays free
    # The live server without keys takes no orders at all
    monkeypatch.delenv("RAZORPAY_KEY_ID")
    monkeypatch.setenv("ENV", "production")
    assert paid_shop.get("/site").json()["payments"] == "off"
    assert paid_shop.post("/orders", json=ORDER).status_code == 503
    assert paid_shop.post("/pdf", json=body).status_code == 403


def test_a_full_coupon_needs_no_payment(paid_shop):
    paid_shop.post("/admin/coupons", json={"code": "GIFT", "percent": 100}, headers=ADMIN)
    placed = paid_shop.post("/orders", json={**ORDER, "coupon": "GIFT"}).json()
    assert placed["checkout"] is None and paid_shop.asked == []
    assert paid_shop.get(f"/orders/{placed['order']['id']}").json()["status"] == "delivered"


# ---------- when the PDF cannot be made ----------

def test_failed_pdf_after_payment_is_flagged_for_refund_and_can_be_retried(paid_shop, monkeypatch):
    def broken(*args):
        raise RuntimeError("browser crashed")

    monkeypatch.setattr(orders, "generate_pdf", broken)
    placed = paid_shop.post("/orders", json=ORDER).json()
    order_id, gateway = placed["order"]["id"], placed["checkout"]["order_id"]
    paid_shop.post(f"/orders/{order_id}/verify", json={"razorpay_payment_id": "pay_5", "razorpay_signature": sign(gateway, "pay_5")})
    status = paid_shop.get(f"/orders/{order_id}").json()
    assert status["status"] == "failed" and status["refund_due"] is True
    assert paid_shop.get(f"/orders/{order_id}/pdf").status_code == 404
    view = paid_shop.get("/admin/orders", headers=ADMIN).json()
    assert view["totals"]["refunds_due"] == 1 and "browser crashed" in view["orders"][0]["error"]

    # The owner fixes the problem and makes it again: delivered, nothing owed
    monkeypatch.setattr(orders, "generate_pdf", lambda *args: b"%PDF-retry")
    again = paid_shop.post(f"/admin/orders/{order_id}/regenerate", headers=ADMIN).json()
    assert again["status"] == "delivered" and again["refund_due"] is False
    assert paid_shop.get(f"/orders/{order_id}/pdf").content == b"%PDF-retry"


def test_failed_test_order_owes_no_refund(shop, monkeypatch):
    monkeypatch.setattr(orders, "generate_pdf", lambda *args: (_ for _ in ()).throw(RuntimeError("no browser")))
    order_id = shop.post("/orders", json=ORDER).json()["order"]["id"]
    status = shop.get(f"/orders/{order_id}").json()
    assert status["status"] == "failed" and status["refund_due"] is False


# ---------- the owner's view ----------

def test_owner_sees_orders_and_revenue_and_can_delete(paid_shop, monkeypatch):
    for number, variant in enumerate(("mini", "full"), start=1):
        placed = paid_shop.post("/orders", json={**ORDER, "variant": variant}).json()
        gateway = placed["checkout"]["order_id"]
        paid_shop.post(f"/orders/{placed['order']['id']}/verify",
                       json={"razorpay_payment_id": f"pay_{number}", "razorpay_signature": sign(gateway, f"pay_{number}")})
    unpaid = paid_shop.post("/orders", json=ORDER).json()["order"]["id"]
    view = paid_shop.get("/admin/orders", headers=ADMIN).json()
    assert view["totals"] == {"orders": 3, "paid": 2, "revenue": 152, "test_orders": 0, "refunds_due": 0}
    assert view["payments"] == "razorpay" and view["live_keys"] is False and view["email"] is False
    newest = view["orders"][0]
    assert newest["id"] == unpaid and newest["status"] == "created" and newest["whatsapp"] == "9876543210"
    numbers = sorted(o["invoice_no"] for o in view["orders"] if o["invoice_no"])
    assert len(set(numbers)) == 2 and numbers[0][-1] == "1" and numbers[1][-1] == "2"

    assert paid_shop.post(f"/admin/orders/{unpaid}/regenerate", headers=ADMIN).status_code == 422
    paid_id = view["orders"][1]["id"]
    assert paid_shop.post(f"/admin/orders/{paid_id}/refunded", headers=ADMIN).json()["refunded"] is True
    assert paid_shop.get("/admin/orders", headers=ADMIN).json()["totals"]["revenue"] in (51, 101)

    # A deletion request removes the row and the stored PDF
    assert orders.pdf_file(paid_id).exists()
    assert paid_shop.delete(f"/admin/orders/{paid_id}", headers=ADMIN).json() == {"deleted": True}
    assert not orders.pdf_file(paid_id).exists() and paid_shop.get(f"/orders/{paid_id}").status_code == 404
    assert paid_shop.get("/admin/orders").status_code == 401


def test_test_orders_are_not_revenue(shop):
    shop.post("/orders", json=ORDER)
    totals = shop.get("/admin/orders", headers=ADMIN).json()["totals"]
    assert totals["test_orders"] == 1 and totals["revenue"] == 0 and totals["paid"] == 0


def test_email_is_sent_when_set_up(shop, monkeypatch):
    sent = []
    monkeypatch.setattr(orders.mailer, "send_patrika", lambda to, lang, link, invoice, brand, pdf: sent.append((to, link, invoice)) or True)
    monkeypatch.setenv("SITE_URL", "https://example.test")
    order_id = shop.post("/orders", json={**ORDER, "lang": "hi"}).json()["order"]["id"]
    assert sent[0][0] == "rohan@example.com" and sent[0][1] == f"https://example.test/thank-you?order={order_id}"
    assert shop.get(f"/orders/{order_id}").json()["emailed"] is True
    # A sending error leaves the order delivered
    def fails(*args):
        raise OSError("smtp down")
    monkeypatch.setattr(orders.mailer, "send_patrika", fails)
    second = shop.post("/orders", json=ORDER).json()["order"]["id"]
    assert shop.get(f"/orders/{second}").json()["status"] == "delivered"


def test_signature_helpers():
    assert payments.checkout_is_genuine("o", "p", "") is False
    assert payments.webhook_is_genuine(b"{}", "abc") is False      # no secret set: nothing is genuine
    assert store.first_time is not None
