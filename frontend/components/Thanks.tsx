"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { content, fill } from "@/lib/content";
import { API_URL, path, type Lang } from "@/lib/site";

type OrderView = {
  id: string;
  status: "created" | "paid" | "delivered" | "failed";
  test: boolean;
  invoice_no: string | null;
  emailed: boolean;
  refund_due: boolean;
};

/**
 * The order's own page: waits while the Patrika is prepared, then offers the
 * download and the receipt. Its address holds the order's private key, so the
 * customer can come back to it later.
 */
export default function Thanks({ lang }: { lang: Lang }) {
  const c = content(lang).thanks;
  const orderId = useSearchParams().get("order");
  const [order, setOrder] = useState<OrderView | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    if (!orderId) return;
    let current = true;
    let tries = 0;
    let timer: ReturnType<typeof setTimeout>;

    async function check() {
      try {
        const response = await fetch(`${API_URL}/orders/${orderId}`);
        if (!current) return;
        if (response.status === 404) return setMissing(true);
        const view: OrderView = await response.json();
        setOrder(view);
        // Still being prepared: look again shortly (for up to about two minutes)
        if ((view.status === "paid" || view.status === "created") && tries++ < 60) timer = setTimeout(check, 2000);
      } catch {
        if (current && tries++ < 60) timer = setTimeout(check, 3000);
      }
    }
    check();
    return () => {
      current = false;
      clearTimeout(timer);
    };
  }, [orderId]);

  if (!orderId || missing) {
    return (
      <section className="py-10 text-center">
        <p className="text-ink-600">{c.lost}</p>
        <Link href={path(lang) + "#kundli"} className="btn-primary mx-auto mt-4 max-w-sm">
          {c.again}
        </Link>
      </section>
    );
  }

  if (order?.status === "failed") {
    return (
      <section className="mx-auto max-w-xl py-10 text-center">
        <h1 className="font-serif text-[28px] leading-tight text-maroon-800">{c.failedTitle}</h1>
        <p className="mt-3 text-ink-600">{c.failedText}</p>
        {order.refund_due && <p className="mt-3 font-semibold">{fill(c.refund, { id: order.id.slice(0, 12) })}</p>}
        <Link href={path(lang) + "#kundli"} className="btn-secondary mx-auto mt-6 max-w-sm">
          {c.again}
        </Link>
      </section>
    );
  }

  if (order?.status !== "delivered") {
    return (
      <section className="py-16 text-center" aria-live="polite">
        <p className="font-serif text-xl text-kesar-600">{c.blessing}</p>
        <p className="mt-3 text-ink-600">{c.preparing}</p>
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-xl py-10 text-center">
      <p className="font-serif text-xl text-kesar-600">{c.blessing}</p>
      <h1 className="mt-2 font-serif text-[28px] leading-tight text-maroon-800">{c.title}</h1>
      <p className="mt-3 text-ink-600">{c.text}</p>
      <a href={`${API_URL}/orders/${order.id}/pdf`} download="janam-patrika.pdf" className="btn-primary mt-6">
        {c.download}
      </a>
      {order.invoice_no && (
        <a href={`${API_URL}/orders/${order.id}/receipt`} target="_blank" rel="noopener" className="btn-secondary mt-2">
          {c.receipt}
        </a>
      )}
      {order.emailed && <p className="mt-3 text-sm text-ink-600">{c.emailed}</p>}
      {order.test && <p className="mt-3 rounded-lg bg-haldi-300/40 p-3 text-sm">{c.testOrder}</p>}
      <Link href={path(lang) + "#kundli"} className="mt-4 inline-block text-kesar-700 underline">
        {c.another}
      </Link>
    </section>
  );
}
