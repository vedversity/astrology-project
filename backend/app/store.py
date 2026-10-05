"""Where orders and coupons are kept: a single SQLite database file.

SQLite needs no account and no server: the whole database is one file
(backend/data/app.db, or the path in DATABASE_PATH). It is right for one small
server. Before running several servers, or for automatic off-site backups,
move these few functions to PostgreSQL (Supabase); nothing else needs to change.

The data folder is never committed to Git: it holds customers' details.
"""

import datetime as dt
import json
import os
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,            -- long random text: also the customer's private download key
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    status TEXT NOT NULL,           -- created, paid, delivered, failed
    test INTEGER NOT NULL,          -- 1 = made without real payment (test mode)
    plan TEXT NOT NULL,
    lang TEXT NOT NULL,
    price INTEGER NOT NULL,         -- rupees, before any coupon
    discount INTEGER NOT NULL,      -- rupees taken off by a coupon
    amount INTEGER NOT NULL,        -- rupees actually charged
    coupon TEXT,
    request TEXT NOT NULL,          -- JSON: birth details and names needed to make the PDF again
    whatsapp TEXT,
    email TEXT,
    gateway_order_id TEXT,
    gateway_payment_id TEXT,
    invoice_no TEXT,
    emailed INTEGER NOT NULL DEFAULT 0,
    refund_due INTEGER NOT NULL DEFAULT 0,   -- 1 = paid but the PDF could not be made: refund the customer
    refunded INTEGER NOT NULL DEFAULT 0,
    error TEXT
);
CREATE TABLE IF NOT EXISTS coupons (
    code TEXT PRIMARY KEY,
    percent INTEGER NOT NULL,
    max_uses INTEGER,               -- NULL = no limit
    used INTEGER NOT NULL DEFAULT 0,
    note TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS seen_events (id TEXT PRIMARY KEY, at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS counters (name TEXT PRIMARY KEY, value INTEGER NOT NULL);
"""


def data_dir():
    return _path().parent


def _path():
    return Path(os.environ.get("DATABASE_PATH") or DEFAULT_PATH)


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


@contextmanager
def _db():
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=15)
    connection.row_factory = sqlite3.Row
    try:
        connection.executescript(SCHEMA)
        with connection:                       # commits on success, rolls back on error
            yield connection
    finally:
        connection.close()


def _order(row):
    if row is None:
        return None
    order = dict(row)
    order["request"] = json.loads(order["request"])
    for flag in ("test", "emailed", "refund_due", "refunded"):
        order[flag] = bool(order[flag])
    return order


# ---------- orders ----------

def create_order(*, plan, lang, price, discount, amount, coupon, request, whatsapp, email, test):
    order_id = secrets.token_urlsafe(24)
    now = _now()
    with _db() as db:
        db.execute(
            "INSERT INTO orders (id, created_at, updated_at, status, test, plan, lang, price, discount, amount,"
            " coupon, request, whatsapp, email) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (order_id, now, now, "created", int(test), plan, lang, price, discount, amount, coupon,
             json.dumps(request, ensure_ascii=False), whatsapp, email))
    return get_order(order_id)


def get_order(order_id):
    with _db() as db:
        return _order(db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone())


def find_by_gateway_order(gateway_order_id):
    with _db() as db:
        return _order(db.execute("SELECT * FROM orders WHERE gateway_order_id = ?", (gateway_order_id,)).fetchone())


def update_order(order_id, **fields):
    fields["updated_at"] = _now()
    names = ", ".join(f"{name} = ?" for name in fields)
    with _db() as db:
        db.execute(f"UPDATE orders SET {names} WHERE id = ?", (*fields.values(), order_id))
    return get_order(order_id)


def mark_paid(order_id, payment_id):
    """Move an order from created to paid. Returns True only for the call that made the change,
    so a payment reported twice (browser and webhook) is fulfilled once."""
    with _db() as db:
        changed = db.execute(
            "UPDATE orders SET status = 'paid', gateway_payment_id = ?, updated_at = ? "
            "WHERE id = ? AND status = 'created'", (payment_id, _now(), order_id)).rowcount == 1
        if changed:
            coupon = db.execute("SELECT coupon FROM orders WHERE id = ?", (order_id,)).fetchone()["coupon"]
            if coupon:
                db.execute("UPDATE coupons SET used = used + 1 WHERE code = ?", (coupon,))
    return changed


def next_invoice_no():
    """JP-2026-000001, counting up within each year. Never repeats."""
    year = dt.datetime.now(dt.timezone.utc).year
    with _db() as db:
        db.execute("INSERT OR IGNORE INTO counters (name, value) VALUES (?, 0)", (f"invoice-{year}",))
        db.execute("UPDATE counters SET value = value + 1 WHERE name = ?", (f"invoice-{year}",))
        value = db.execute("SELECT value FROM counters WHERE name = ?", (f"invoice-{year}",)).fetchone()["value"]
    return f"JP-{year}-{value:06d}"


def list_orders(limit=100):
    with _db() as db:
        rows = db.execute("SELECT * FROM orders ORDER BY created_at DESC, rowid DESC LIMIT ?", (limit,)).fetchall()
    return [_order(row) for row in rows]


def totals():
    """Counts and revenue. Test orders are never counted as revenue."""
    with _db() as db:
        row = db.execute(
            "SELECT COUNT(*) AS orders,"
            " SUM(CASE WHEN status IN ('paid','delivered') AND test = 0 AND refunded = 0 THEN 1 ELSE 0 END) AS paid,"
            " SUM(CASE WHEN status IN ('paid','delivered') AND test = 0 AND refunded = 0 THEN amount ELSE 0 END) AS revenue,"
            " SUM(CASE WHEN test = 1 THEN 1 ELSE 0 END) AS test_orders,"
            " SUM(CASE WHEN refund_due = 1 AND refunded = 0 THEN 1 ELSE 0 END) AS refunds_due"
            " FROM orders").fetchone()
    return {key: row[key] or 0 for key in row.keys()}


def delete_order(order_id):
    """Remove an order and everything typed with it (a customer's deletion request)."""
    with _db() as db:
        return db.execute("DELETE FROM orders WHERE id = ?", (order_id,)).rowcount == 1


def first_time(event_id):
    """True the first time an event id is seen; a repeated webhook returns False."""
    with _db() as db:
        return db.execute("INSERT OR IGNORE INTO seen_events (id, at) VALUES (?, ?)",
                          (event_id, _now())).rowcount == 1


# ---------- coupons ----------

def save_coupon(code, percent, max_uses=None, note=None):
    with _db() as db:
        db.execute(
            "INSERT INTO coupons (code, percent, max_uses, note, created_at) VALUES (?,?,?,?,?) "
            "ON CONFLICT(code) DO UPDATE SET percent = excluded.percent, max_uses = excluded.max_uses, "
            "note = excluded.note", (code, percent, max_uses, note, _now()))


def get_coupon(code):
    with _db() as db:
        row = db.execute("SELECT * FROM coupons WHERE code = ?", (code,)).fetchone()
    return dict(row) if row else None


def list_coupons():
    with _db() as db:
        return [dict(row) for row in db.execute("SELECT * FROM coupons ORDER BY created_at DESC").fetchall()]


def delete_coupon(code):
    with _db() as db:
        return db.execute("DELETE FROM coupons WHERE code = ?", (code,)).rowcount == 1
