"""Orders: placing one, paying, delivery, the receipt, coupons, and the owner's view.

The journey of an order:

    created --(payment checked)--> paid --(PDF made)--> delivered
                                     \\--(PDF could not be made)--> failed  (refund_due is set)

Two things report a payment: the customer's browser (POST /orders/{id}/verify)
and Razorpay's own server (POST /webhooks/razorpay). Either may arrive first, or
only one. store.mark_paid() lets exactly one of them start the delivery.
"""

import datetime as dt
import json
import os
from typing import Literal, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from app import config, mailer, payments, store
from app.api_common import PdfInput, admin_only, checked
from app.content import audience_for
from app.limits import Limiter, pdf_limit
from app.pdf import build_receipt_html, generate_pdf, html_to_pdf
from app.report import build_report

router = APIRouter()
# 20 orders per address every 10 minutes
order_limit = Limiter(limit=20, seconds=600)


class OrderInput(PdfInput):
    whatsapp: str = Field(pattern=r"^[6-9]\d{9}$", description="10-digit Indian mobile number")
    email: Optional[str] = Field(default=None, max_length=120, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    coupon: Optional[str] = Field(default=None, max_length=20)
    # The customer must tick the consent box; anything but true is refused
    consent: Literal[True]


class PaymentProof(BaseModel):
    razorpay_payment_id: str = Field(max_length=60)
    razorpay_signature: str = Field(max_length=200)


class CouponInput(BaseModel):
    code: str = Field(pattern=r"^[A-Za-z0-9]{3,20}$")
    percent: int = Field(ge=1, le=100)
    max_uses: Optional[int] = Field(default=None, ge=1)
    note: Optional[str] = Field(default=None, max_length=100)


class CouponCheck(BaseModel):
    code: str = Field(max_length=20)
    plan: Literal["mini", "full", "premium"]


# ---------- prices and coupons ----------

def _discount(code, price):
    """Rupees a coupon takes off a price. Raises 422 with a reason if it cannot be used."""
    coupon = store.get_coupon(code.strip().upper())
    if not coupon:
        raise HTTPException(status_code=422, detail="This coupon code is not valid.")
    if coupon["max_uses"] is not None and coupon["used"] >= coupon["max_uses"]:
        raise HTTPException(status_code=422, detail="This coupon has been used up.")
    return coupon["code"], price * coupon["percent"] // 100


@router.post("/coupons/check")
def check_coupon(body: CouponCheck):
    plan = config.plan(body.plan)
    code, discount = _discount(body.code, plan["price"])
    return {"code": code, "price": plan["price"], "discount": discount, "amount": plan["price"] - discount}


# ---------- delivery ----------

def pdf_file(order_id):
    return store.data_dir() / "pdfs" / f"{order_id}.pdf"


def _birth(request):
    return {"date": dt.date.fromisoformat(request["date"]),
            "time": dt.time.fromisoformat(request["time"]) if request["time"] else None,
            "latitude": request["latitude"], "longitude": request["longitude"],
            "timezone": request["timezone"], "time_known": request["time_known"]}


def fulfil(order_id):
    """Make the PDF for a paid order, keep it, and email it. Safe to run again (regenerate)."""
    order = store.get_order(order_id)
    request = order["request"]
    try:
        report = build_report(**_birth(request), gender=request["person"]["gender"],
                              surname=request["person"].get("surname"), kuldevi=request["person"].get("kuldevi"))
        pdf = generate_pdf(report, request["person"], order["plan"], order["lang"])
        target = pdf_file(order_id)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(pdf)
        order = store.update_order(order_id, status="delivered", error=None, refund_due=0,
                                   invoice_no=order["invoice_no"] or store.next_invoice_no())
    except Exception as error:                                    # the customer paid and got nothing
        owed = 0 if order["test"] or order["amount"] == 0 else 1
        store.update_order(order_id, status="failed", refund_due=owed, error=str(error)[:300])
        return
    try:
        site = config.site()
        link = f"{os.environ.get('SITE_URL', 'http://localhost:3000').rstrip('/')}" \
               f"{'' if order['lang'] == 'hi' else '/en'}/thank-you?order={order_id}"
        if mailer.send_patrika(order["email"], order["lang"], link, order["invoice_no"],
                               site["brand"]["name"][order["lang"]], pdf):
            store.update_order(order_id, emailed=1)
    except Exception as error:                                    # delivered on the page; only the email failed
        store.update_order(order_id, error=f"email: {error}"[:300])


def _public(order):
    """What the customer's browser may know about an order: never the personal details."""
    return {
        "id": order["id"], "status": order["status"], "plan": order["plan"], "lang": order["lang"],
        "price": order["price"], "discount": order["discount"], "amount": order["amount"],
        "test": order["test"], "invoice_no": order["invoice_no"], "emailed": order["emailed"],
        "refund_due": order["refund_due"],
    }


def _get(order_id):
    order = store.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


# ---------- the customer's steps ----------

@router.post("/orders", dependencies=[Depends(order_limit)])
def place_order(body: OrderInput, background: BackgroundTasks):
    mode = payments.mode()
    if mode == "off":
        raise HTTPException(status_code=503, detail="Orders are not being taken yet.")
    birth = checked(body)
    plan = config.plan(body.variant)
    if plan.get("audience") == "child" and audience_for(body.date, dt.date.today()) != "child":
        raise HTTPException(status_code=422, detail="This plan is for a child's Patrika.")

    # The price always comes from our own settings, never from the browser
    price = plan["price"]
    coupon, discount = _discount(body.coupon, price) if body.coupon else (None, 0)
    amount = price - discount
    person = body.model_dump(include={"child_name", "gender", "father_name", "mother_name",
                                      "gotra", "kuldevi", "place", "surname"})
    request = {**{key: (value.isoformat() if hasattr(value, "isoformat") else value) for key, value in birth.items()},
               "person": person}
    order = store.create_order(plan=body.variant, lang=body.lang, price=price, discount=discount,
                               amount=amount, coupon=coupon, request=request, whatsapp=body.whatsapp,
                               email=body.email, test=mode == "test")

    if mode == "test" or amount == 0:
        # Nothing to pay (test mode, or a 100% coupon): deliver straight away
        store.mark_paid(order["id"], "test" if mode == "test" else "coupon")
        background.add_task(fulfil, order["id"])
        return {"order": _public(store.get_order(order["id"])), "checkout": None}

    try:
        gateway_order_id = payments.create_order(amount, receipt=order["id"])
    except Exception:
        store.update_order(order["id"], status="failed", error="could not open the payment")
        raise HTTPException(status_code=502, detail="The payment could not be started. Please try again.")
    store.update_order(order["id"], gateway_order_id=gateway_order_id)
    return {"order": _public(store.get_order(order["id"])),
            "checkout": {"key": payments.public_key(), "order_id": gateway_order_id,
                         "amount": amount * 100, "currency": "INR"}}


@router.post("/orders/{order_id}/verify")
def verify_payment(order_id: str, proof: PaymentProof, background: BackgroundTasks):
    order = _get(order_id)
    if not order["gateway_order_id"] or not payments.checkout_is_genuine(
            order["gateway_order_id"], proof.razorpay_payment_id, proof.razorpay_signature):
        raise HTTPException(status_code=400, detail="The payment could not be confirmed.")
    if store.mark_paid(order_id, proof.razorpay_payment_id):
        background.add_task(fulfil, order_id)
    return _public(store.get_order(order_id))


@router.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request, background: BackgroundTasks,
                           x_razorpay_signature: str = Header(default=""),
                           x_razorpay_event_id: str = Header(default="")):
    body = await request.body()
    if not payments.webhook_is_genuine(body, x_razorpay_signature):
        raise HTTPException(status_code=400, detail="Bad signature.")
    event = json.loads(body)
    # Razorpay repeats a webhook until it gets a 200, so each event is acted on once
    if x_razorpay_event_id and not store.first_time(x_razorpay_event_id):
        return {"ok": True, "repeat": True}
    if event.get("event") in ("payment.captured", "order.paid"):
        payment = event.get("payload", {}).get("payment", {}).get("entity", {})
        order = store.find_by_gateway_order(payment.get("order_id", ""))
        if order and store.mark_paid(order["id"], payment.get("id", "")):
            background.add_task(fulfil, order["id"])
    return {"ok": True}


@router.get("/orders/{order_id}")
def order_status(order_id: str):
    return _public(_get(order_id))


@router.get("/orders/{order_id}/pdf")
def order_pdf(order_id: str):
    order = _get(order_id)
    if order["status"] != "delivered" or not pdf_file(order_id).exists():
        raise HTTPException(status_code=404, detail="The Patrika is not ready.")
    return FileResponse(pdf_file(order_id), media_type="application/pdf", filename="janam-patrika.pdf")


@router.get("/orders/{order_id}/receipt", dependencies=[Depends(pdf_limit)])
def order_receipt(order_id: str):
    order = _get(order_id)
    if order["status"] not in ("paid", "delivered") or not order["invoice_no"]:
        raise HTTPException(status_code=404, detail="No receipt for this order.")
    site = config.site()
    html = build_receipt_html(order, config.plan(order["plan"]), site)
    return Response(content=html_to_pdf(html), media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="receipt-{order["invoice_no"]}.pdf"'})


# ---------- the owner's view ----------

def _admin_view(order):
    person = order["request"]["person"]
    return {**_public(order), "created_at": order["created_at"], "coupon": order["coupon"],
            "name": person.get("child_name"), "whatsapp": order["whatsapp"], "email": order["email"],
            "payment_id": order["gateway_payment_id"], "refunded": order["refunded"], "error": order["error"]}


@router.get("/admin/orders", dependencies=[Depends(admin_only)])
def admin_orders():
    return {"totals": store.totals(), "payments": payments.mode(), "live_keys": payments.is_live(),
            "email": mailer.configured(), "orders": [_admin_view(o) for o in store.list_orders(200)]}


@router.post("/admin/orders/{order_id}/regenerate", dependencies=[Depends(admin_only)])
def admin_regenerate(order_id: str):
    order = _get(order_id)
    if order["status"] == "created":
        raise HTTPException(status_code=422, detail="This order has not been paid.")
    fulfil(order_id)
    return _admin_view(store.get_order(order_id))


@router.post("/admin/orders/{order_id}/refunded", dependencies=[Depends(admin_only)])
def admin_mark_refunded(order_id: str):
    _get(order_id)
    return _admin_view(store.update_order(order_id, refunded=1, refund_due=0))


@router.delete("/admin/orders/{order_id}", dependencies=[Depends(admin_only)])
def admin_delete_order(order_id: str):
    """A customer's deletion request: removes the order, their details and the stored PDF."""
    _get(order_id)
    pdf_file(order_id).unlink(missing_ok=True)
    store.delete_order(order_id)
    return {"deleted": True}


@router.get("/admin/coupons", dependencies=[Depends(admin_only)])
def admin_coupons():
    return store.list_coupons()


@router.post("/admin/coupons", dependencies=[Depends(admin_only)])
def admin_save_coupon(coupon: CouponInput):
    store.save_coupon(coupon.code.upper(), coupon.percent, coupon.max_uses, coupon.note)
    return store.list_coupons()


@router.delete("/admin/coupons/{code}", dependencies=[Depends(admin_only)])
def admin_delete_coupon(code: str):
    store.delete_coupon(code.upper())
    return store.list_coupons()
