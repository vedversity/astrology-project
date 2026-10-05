"use client";

import { useCallback, useEffect, useState } from "react";

import { API_URL } from "@/lib/site";

// Orders, revenue and coupons for the owner. Shown on /admin after signing in.

type Row = {
  id: string; created_at: string; status: string; plan: string; lang: string; amount: number; discount: number;
  coupon: string | null; test: boolean; invoice_no: string | null; name: string | null; whatsapp: string | null;
  email: string | null; refund_due: boolean; refunded: boolean; error: string | null;
};
type Overview = {
  totals: { orders: number; paid: number; revenue: number; test_orders: number; refunds_due: number };
  payments: "razorpay" | "test" | "off";
  live_keys: boolean;
  email: boolean;
  orders: Row[];
};
type Coupon = { code: string; percent: number; max_uses: number | null; used: number; note: string | null };

export default function AdminOrders({ token }: { token: string }) {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [coupons, setCoupons] = useState<Coupon[]>([]);
  const [message, setMessage] = useState("");
  const [code, setCode] = useState("");
  const [percent, setPercent] = useState("10");
  const [maxUses, setMaxUses] = useState("");

  const call = useCallback(
    async (route: string, method = "GET", body?: unknown) => {
      const response = await fetch(API_URL + route, {
        method,
        headers: { "Content-Type": "application/json", "X-Admin-Token": token },
        body: body ? JSON.stringify(body) : undefined,
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "That did not work. Please check and try again.");
      return data;
    },
    [token],
  );

  const refresh = useCallback(async () => {
    try {
      const [orders, list] = await Promise.all([call("/admin/orders"), call("/admin/coupons")]);
      setOverview(orders);
      setCoupons(list);
    } catch (error) {
      setMessage((error as Error).message);
    }
  }, [call]);

  useEffect(() => {
    // Loading the owner's data when the page opens
    const timer = setTimeout(refresh, 0);
    return () => clearTimeout(timer);
  }, [refresh]);

  async function act(route: string, method: string, confirmText?: string) {
    if (confirmText && !window.confirm(confirmText)) return;
    setMessage("");
    try {
      await call(route, method);
      await refresh();
    } catch (error) {
      setMessage((error as Error).message);
    }
  }

  async function addCoupon(event: React.FormEvent) {
    event.preventDefault();
    setMessage("");
    try {
      setCoupons(await call("/admin/coupons", "POST", { code, percent: Number(percent), max_uses: maxUses ? Number(maxUses) : null }));
      setCode("");
    } catch (error) {
      setMessage((error as Error).message);
    }
  }

  if (!overview) return <p className="card mt-4 text-ink-600">{message || "Loading orders…"}</p>;
  const t = overview.totals;
  const paymentText = {
    razorpay: overview.live_keys ? "Payments: LIVE (real money)" : "Payments: Razorpay TEST keys",
    test: "Payments: not connected. Orders are delivered without charging (test mode).",
    off: "Payments: not connected. The live site is not taking orders.",
  }[overview.payments];

  return (
    <section className="py-6">
      <h1 className="font-serif text-[28px] text-maroon-800">Orders</h1>
      <p className="mt-1 text-sm text-ink-600">
        {paymentText} · Email delivery: {overview.email ? "on" : "not set up"}
      </p>

      <div className="mt-3 grid grid-cols-2 gap-3 md:grid-cols-4">
        {[
          ["Revenue", `₹${t.revenue}`],
          ["Paid orders", t.paid],
          ["Refunds to make", t.refunds_due],
          ["Test orders", t.test_orders],
        ].map(([label, value]) => (
          <div key={label} className="card">
            <p className="text-sm text-ink-600">{label}</p>
            <p className="font-serif text-2xl text-maroon-800">{value}</p>
          </div>
        ))}
      </div>
      {message && (
        <p role="alert" className="mt-3 text-sm font-semibold text-red-700">
          {message}
        </p>
      )}

      <div className="mt-3 overflow-x-auto rounded-2xl border border-kesar-100 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="bg-kesar-50 text-maroon-800">
            <tr>
              {["Date", "Name", "Contact", "Plan", "Paid", "Status", ""].map((heading) => (
                <th key={heading} className="px-3 py-2">
                  {heading}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {overview.orders.length === 0 && (
              <tr>
                <td colSpan={7} className="px-3 py-4 text-ink-600">
                  No orders yet.
                </td>
              </tr>
            )}
            {overview.orders.map((order) => (
              <tr key={order.id} className="border-t border-kesar-100 align-top">
                <td className="px-3 py-2 whitespace-nowrap">{order.created_at.slice(0, 10)}</td>
                <td className="px-3 py-2">{order.name ?? "—"}</td>
                <td className="px-3 py-2">
                  {order.whatsapp}
                  {order.email && <span className="block text-ink-600">{order.email}</span>}
                </td>
                <td className="px-3 py-2">
                  {order.plan} · {order.lang}
                </td>
                <td className="px-3 py-2 whitespace-nowrap">
                  ₹{order.amount}
                  {order.coupon && <span className="block text-ink-600">{order.coupon}</span>}
                </td>
                <td className="px-3 py-2">
                  <b>{order.status}</b>
                  {order.test && " (test)"}
                  {order.refund_due && <span className="block font-semibold text-red-700">refund due</span>}
                  {order.refunded && <span className="block">refunded</span>}
                  {order.error && <span className="block text-ink-600">{order.error}</span>}
                  {order.invoice_no && <span className="block text-ink-600">{order.invoice_no}</span>}
                </td>
                <td className="px-3 py-2 whitespace-nowrap">
                  {order.status !== "created" && (
                    <button type="button" className="block underline" onClick={() => act(`/admin/orders/${order.id}/regenerate`, "POST")}>
                      Make PDF again
                    </button>
                  )}
                  {order.refund_due && (
                    <button type="button" className="block underline" onClick={() => act(`/admin/orders/${order.id}/refunded`, "POST", "Mark this order as refunded? Do this after refunding in Razorpay.")}>
                      Mark refunded
                    </button>
                  )}
                  <button type="button" className="block text-red-700 underline" onClick={() => act(`/admin/orders/${order.id}`, "DELETE", "Delete this order and the customer's details for good?")}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 className="mt-8 font-serif text-2xl text-maroon-800">Coupons</h2>
      <form onSubmit={addCoupon} className="card mt-3 grid gap-3 md:grid-cols-4 md:items-end">
        <div>
          <label className="label" htmlFor="coupon-code">
            Code
          </label>
          <input id="coupon-code" className="field uppercase" value={code} maxLength={20} onChange={(event) => setCode(event.target.value)} />
        </div>
        <div>
          <label className="label" htmlFor="coupon-percent">
            Percent off
          </label>
          <input id="coupon-percent" type="number" min={1} max={100} className="field" value={percent} onChange={(event) => setPercent(event.target.value)} />
        </div>
        <div>
          <label className="label" htmlFor="coupon-max">
            Uses allowed (empty = no limit)
          </label>
          <input id="coupon-max" type="number" min={1} className="field" value={maxUses} onChange={(event) => setMaxUses(event.target.value)} />
        </div>
        <button type="submit" disabled={!code} className="btn-secondary">
          Add coupon
        </button>
      </form>
      <ul className="mt-3 space-y-2">
        {coupons.map((coupon) => (
          <li key={coupon.code} className="card flex items-center justify-between">
            <span>
              <b>{coupon.code}</b> · {coupon.percent}% off · used {coupon.used}
              {coupon.max_uses ? ` of ${coupon.max_uses}` : ""}
            </span>
            <button type="button" className="text-sm text-red-700 underline" onClick={() => act(`/admin/coupons/${coupon.code}`, "DELETE")}>
              Remove
            </button>
          </li>
        ))}
        {coupons.length === 0 && <li className="text-sm text-ink-600">No coupons yet.</li>}
      </ul>
    </section>
  );
}
