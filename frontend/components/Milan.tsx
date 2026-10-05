"use client";

import { useRef, useState } from "react";

import PlaceInput from "@/components/PlaceInput";
import type { Place } from "@/lib/birth";
import { content, fill } from "@/lib/content";
import { guides } from "@/lib/guides";
import { API_URL, type Lang, type Text } from "@/lib/site";

type Person = { name: string; date: string; time: string; timeKnown: boolean; place: Place | null };
type Koota = { key: string; name: Text; about: Text; points: number; max: number; groom: Text; bride: Text };
type Side = { rashi: Text; nakshatra: Text; pada: number; time_known: boolean };
type Result = {
  total: number;
  max: number;
  band: "excellent" | "good" | "acceptable" | "review";
  label: Text;
  text: Text;
  kootas: Koota[];
  exceptions: Text[];
  manglik: { groom: { label: Text }; bride: { label: Text }; text: Text; note: Text | null };
  people: { groom: Side; bride: Side };
  note: Text;
};

const EMPTY: Person = { name: "", date: "", time: "", timeKnown: true, place: null };
const WHO = ["groom", "bride"] as const;

/** Kundli Milan: the birth details of two people, then the 36-guna result. */
export default function Milan({ lang }: { lang: Lang }) {
  const c = guides(lang).milan;
  const form = content(lang).form;
  const [people, setPeople] = useState<Record<(typeof WHO)[number], Person>>({ groom: EMPTY, bride: EMPTY });
  const [error, setError] = useState("");
  const [working, setWorking] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const [pdfState, setPdfState] = useState<"idle" | "working" | "failed">("idle");
  const resultBox = useRef<HTMLDivElement>(null);
  const today = new Date().toISOString().slice(0, 10);

  const set = (who: (typeof WHO)[number], change: Partial<Person>) =>
    setPeople((current) => ({ ...current, [who]: { ...current[who], ...change } }));

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    for (const who of WHO) {
      const p = people[who];
      const label = c.who[who];
      if (!p.date || p.date > today || p.date < "1900-01-01") return setError(`${label}: ${form.errors.date}`);
      if (p.timeKnown && !p.time) return setError(`${label}: ${form.errors.time}`);
      if (!p.place) return setError(`${label}: ${form.errors.place}`);
    }
    setError("");
    setWorking(true);
    const body = requestBody();
    try {
      const response = await fetch(`${API_URL}/milan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!response.ok) throw new Error(String(response.status));
      setResult(await response.json());
      setTimeout(() => resultBox.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
    } catch {
      setError(c.failed);
    } finally {
      setWorking(false);
    }
  }

  /** The two births in the shape the API expects. */
  function requestBody() {
    return Object.fromEntries(
      WHO.map((who) => {
        const p = people[who];
        return [
          who,
          {
            date: p.date,
            time: p.timeKnown ? p.time : null,
            time_known: p.timeKnown,
            latitude: p.place!.latitude,
            longitude: p.place!.longitude,
            timezone: p.place!.timezone,
          },
        ];
      }),
    );
  }

  async function downloadPdf() {
    setPdfState("working");
    try {
      const response = await fetch(`${API_URL}/milan/pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...requestBody(),
          lang,
          groom_name: people.groom.name.trim() || null,
          bride_name: people.bride.name.trim() || null,
          groom_place: people.groom.place?.label ?? null,
          bride_place: people.bride.place?.label ?? null,
        }),
      });
      if (!response.ok) throw new Error(String(response.status));
      const link = document.createElement("a");
      link.href = URL.createObjectURL(await response.blob());
      link.download = "kundli-milan.pdf";
      link.click();
      setTimeout(() => URL.revokeObjectURL(link.href), 60000);
      setPdfState("idle");
    } catch {
      setPdfState("failed");
    }
  }

  const nameOf = (who: (typeof WHO)[number]) => people[who].name.trim() || c.who[who];
  const number = (value: number) => (Number.isInteger(value) ? String(value) : value.toFixed(1));

  return (
    <>
      <form id="milan" onSubmit={submit} noValidate className="scroll-mt-28">
        <div className="grid gap-3 md:grid-cols-2">
          {WHO.map((who) => (
            <fieldset key={who} className="card">
              <legend className="sr-only">{c.who[who]}</legend>
              <h2 className="text-lg font-semibold text-maroon-800">{c.who[who]}</h2>

              <label className="label mt-3" htmlFor={`${who}-name`}>
                {form.name}
              </label>
              <input
                id={`${who}-name`}
                className="field"
                maxLength={60}
                autoComplete="off"
                value={people[who].name}
                onChange={(event) => set(who, { name: event.target.value })}
              />

              <label className="label mt-3" htmlFor={`${who}-date`}>
                {form.date}
              </label>
              <input
                id={`${who}-date`}
                type="date"
                className="field"
                min="1900-01-01"
                max={today}
                value={people[who].date}
                onChange={(event) => set(who, { date: event.target.value })}
              />

              <label className="label mt-3" htmlFor={`${who}-time`}>
                {form.time}
              </label>
              <input
                id={`${who}-time`}
                type="time"
                className="field disabled:bg-gray-100"
                disabled={!people[who].timeKnown}
                value={people[who].time}
                onChange={(event) => set(who, { time: event.target.value })}
              />
              <label className="mt-2 flex min-h-8 items-center gap-2 text-sm text-ink-600">
                <input
                  type="checkbox"
                  className="size-5 accent-kesar-600"
                  checked={!people[who].timeKnown}
                  onChange={(event) => set(who, { timeKnown: !event.target.checked })}
                />
                {form.timeUnknown}
              </label>

              <label className="label mt-3" htmlFor={`${who}-place`}>
                {form.place}
              </label>
              <PlaceInput
                id={`${who}-place`}
                value={people[who].place}
                onChange={(place) => set(who, { place })}
                placeholder={form.placePlaceholder}
                noneText={form.placeNone}
              />
            </fieldset>
          ))}
        </div>
        {error && (
          <p role="alert" className="mt-3 text-sm font-semibold text-red-700">
            {error}
          </p>
        )}
        <button type="submit" disabled={working} className="btn-primary mt-4 md:mx-auto md:max-w-md">
          {working ? c.working : c.submit}
        </button>
        <p className="mt-2 text-center text-xs text-ink-600">{form.privacy}</p>
      </form>

      {result && (
        <div ref={resultBox} className="scroll-mt-28 pt-8">
          <div className="rounded-2xl border-2 border-kesar-500 bg-white p-5 text-center">
            <p className="text-sm text-ink-600">
              {nameOf("groom")} · {nameOf("bride")}
            </p>
            <p className="mt-1 font-serif text-5xl text-maroon-800">
              {number(result.total)}
              <span className="text-2xl text-ink-600"> / {result.max}</span>
            </p>
            <p className="mt-1 text-lg font-semibold text-kesar-700">{result.label[lang]}</p>
            <p className="mx-auto mt-2 max-w-2xl text-left md:text-center">{result.text[lang]}</p>
          </div>

          <div className="mt-3 grid gap-3 md:grid-cols-2">
            {WHO.map((who) => (
              <div key={who} className="card">
                <h3 className="font-semibold text-maroon-800">{nameOf(who)}</h3>
                <p className="text-ink-600">
                  {result.people[who].rashi[lang]} · {result.people[who].nakshatra[lang]} ·{" "}
                  {fill(c.pada, { n: result.people[who].pada })}
                </p>
                <p className="mt-1 text-sm">
                  {c.manglikLabel}: <b>{result.manglik[who].label[lang]}</b>
                </p>
              </div>
            ))}
          </div>

          <h2 className="mt-6 mb-3 font-serif text-2xl text-maroon-800">{c.tableTitle}</h2>
          <div className="overflow-x-auto rounded-2xl border border-kesar-100 bg-white">
            <table className="w-full text-left">
              <thead className="bg-kesar-50 text-sm text-maroon-800">
                <tr>
                  <th className="px-3 py-2">{c.columns.koota}</th>
                  <th className="hidden px-3 py-2 md:table-cell">{c.who.groom}</th>
                  <th className="hidden px-3 py-2 md:table-cell">{c.who.bride}</th>
                  <th className="px-3 py-2 text-right">{c.columns.points}</th>
                </tr>
              </thead>
              <tbody>
                {result.kootas.map((koota) => (
                  <tr key={koota.key} className="border-t border-kesar-100 align-top">
                    <td className="px-3 py-2">
                      <span className="font-semibold">{koota.name[lang]}</span>
                      <span className="block text-sm text-ink-600">{koota.about[lang]}</span>
                      <span className="block text-sm text-ink-600 md:hidden">
                        {koota.groom[lang]} · {koota.bride[lang]}
                      </span>
                    </td>
                    <td className="hidden px-3 py-2 md:table-cell">{koota.groom[lang]}</td>
                    <td className="hidden px-3 py-2 md:table-cell">{koota.bride[lang]}</td>
                    <td className="px-3 py-2 text-right font-semibold whitespace-nowrap">
                      {number(koota.points)} / {koota.max}
                    </td>
                  </tr>
                ))}
                <tr className="border-t-2 border-kesar-500 bg-kesar-50 font-semibold">
                  <td className="px-3 py-2" colSpan={1}>
                    {c.columns.total}
                  </td>
                  <td className="hidden md:table-cell" />
                  <td className="hidden md:table-cell" />
                  <td className="px-3 py-2 text-right whitespace-nowrap">
                    {number(result.total)} / {result.max}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {result.exceptions.length > 0 && (
            <div className="card mt-3">
              <h3 className="font-semibold text-maroon-800">{c.exceptionsTitle}</h3>
              <ul className="mt-1 list-disc space-y-1 pl-5">
                {result.exceptions.map((item) => (
                  <li key={item.en}>{item[lang]}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="card mt-3">
            <h3 className="font-semibold text-maroon-800">{c.manglikTitle}</h3>
            <p className="mt-1">{result.manglik.text[lang]}</p>
            {result.manglik.note && <p className="mt-1 text-sm text-ink-600">{result.manglik.note[lang]}</p>}
          </div>
          <p className="mt-3 text-sm text-ink-600">{result.note[lang]}</p>
          <button type="button" onClick={downloadPdf} disabled={pdfState === "working"} className="btn-secondary mt-4 md:mx-auto md:max-w-md">
            {pdfState === "working" ? c.pdfWorking : c.pdf}
          </button>
          {pdfState === "failed" && (
            <p role="alert" className="mt-2 text-center text-sm font-semibold text-red-700">
              {c.failed}
            </p>
          )}
        </div>
      )}
    </>
  );
}
