"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import PlaceInput from "@/components/PlaceInput";
import { saveCity, useCity, type Place } from "@/lib/birth";
import { content, fill } from "@/lib/content";
import { API_URL, DEFAULT_CITY, path, type Lang, type Text } from "@/lib/site";

type Timed = Text & { end?: string };
export type PanchangData = {
  date: string;
  weekday: Text;
  tithi: Timed;
  paksha: Text;
  nakshatra: Timed;
  yoga: Timed;
  karana: Text;
  moon_sign: Text;
  maas: { amanta: Text; purnimanta: Text };
  ritu: Text;
  vikram_samvat: number;
  sunrise: string;
  sunset: string;
  rahu_kaal: { start: string; end: string };
};

/** "2026-09-27T16:59:27+05:30" -> "4:59 PM". The time is already in the city's own clock. */
function clock(iso: string) {
  const hour = Number(iso.slice(11, 13));
  return `${hour % 12 || 12}:${iso.slice(14, 16)} ${hour < 12 ? "AM" : "PM"}`;
}

/** A time, with the date added when it falls on a later day than the Panchang's. */
function until(iso: string, day: string) {
  return iso.slice(0, 10) === day ? clock(iso) : `${clock(iso)} (${iso.slice(8, 10)}/${iso.slice(5, 7)})`;
}

function usePanchang(place: Place, date: string, initial: PanchangData | null) {
  const [result, setResult] = useState<{ key: string; data: PanchangData | null; failed: boolean }>({
    key: initial ? `${DEFAULT_CITY.label}|` : "",
    data: initial,
    failed: false,
  });
  const key = `${place.label}|${date}`;

  useEffect(() => {
    let current = true;
    const query = new URLSearchParams({
      latitude: String(place.latitude),
      longitude: String(place.longitude),
      timezone: place.timezone,
    });
    if (date) query.set("date", date);
    fetch(`${API_URL}/panchang?${query}`)
      .then((response) => (response.ok ? response.json() : Promise.reject()))
      .then((data) => current && setResult({ key, data, failed: false }))
      .catch(() => current && setResult({ key, data: null, failed: true }));
    return () => {
      current = false;
    };
  }, [key, place, date]);

  // Until the answer for this city and date arrives, nothing stale is shown
  return result.key === key ? result : { key, data: null, failed: false };
}

/** The remembered city if there is one, otherwise Delhi. undefined while the page loads. */
function useChosenCity() {
  const remembered = useCity();
  const [picked, setPicked] = useState<Place | null>(null);
  const place = picked ?? (remembered === undefined ? undefined : (remembered ?? DEFAULT_CITY));
  const choose = (next: Place | null) => {
    if (!next) return;
    saveCity(next);
    setPicked(next);
  };
  return { place, choose };
}

/** The full Panchang page: pick a city and a date, see the day's details. */
export default function Panchang({ lang, initial }: { lang: Lang; initial: PanchangData | null }) {
  const c = content(lang).panchang;
  const { place, choose } = useChosenCity();
  const [date, setDate] = useState("");
  const { data, failed } = usePanchang(place ?? DEFAULT_CITY, date, initial);

  const rows: [string, React.ReactNode][] = data
    ? [
        [c.rows.weekday, data.weekday[lang]],
        [c.rows.tithi, `${data.tithi[lang]} · ${fill(c.till, { time: until(data.tithi.end!, data.date) })}`],
        [c.rows.paksha, data.paksha[lang]],
        [c.rows.nakshatra, `${data.nakshatra[lang]} · ${fill(c.till, { time: until(data.nakshatra.end!, data.date) })}`],
        [c.rows.yoga, `${data.yoga[lang]} · ${fill(c.till, { time: until(data.yoga.end!, data.date) })}`],
        [c.rows.karana, data.karana[lang]],
        [c.rows.moonSign, data.moon_sign[lang]],
        [c.rows.sunrise, clock(data.sunrise)],
        [c.rows.sunset, clock(data.sunset)],
        [c.rows.rahuKaal, `${clock(data.rahu_kaal.start)} – ${clock(data.rahu_kaal.end)}`],
        [c.rows.maas, `${c.rows.amanta}: ${data.maas.amanta[lang]} · ${c.rows.purnimanta}: ${data.maas.purnimanta[lang]}`],
        [c.rows.ritu, data.ritu[lang]],
        [c.rows.samvat, data.vikram_samvat],
      ]
    : [];

  return (
    <>
      <div className="card grid gap-3 md:grid-cols-2">
        <div>
          <label className="label" htmlFor="city">
            {c.city}
          </label>
          {place && (
            <PlaceInput
              key={place.label}
              id="city"
              value={place}
              onChange={choose}
              placeholder={place.label}
              noneText={content(lang).form.placeNone}
            />
          )}
        </div>
        <div>
          <label className="label" htmlFor="panchang-date">
            {c.date}
          </label>
          <input
            id="panchang-date"
            type="date"
            className="field"
            min="1900-01-01"
            max="2100-12-31"
            value={date || data?.date || ""}
            onChange={(event) => setDate(event.target.value)}
          />
        </div>
      </div>

      <div className="card mt-3">
        {failed && <p role="alert">{c.error}</p>}
        {!failed && !data && <p className="text-ink-600">{c.loading}</p>}
        {data && (
          <>
            <p className="mb-2 text-sm text-ink-600">{c.atSunrise}</p>
            <dl className="grid grid-cols-[auto_1fr] gap-x-4">
              {rows.map(([label, value]) => (
                <div key={label} className="col-span-2 grid grid-cols-subgrid border-b border-kesar-100 py-2 last:border-0">
                  <dt className="font-semibold text-maroon-700">{label}</dt>
                  <dd>{value}</dd>
                </div>
              ))}
            </dl>
          </>
        )}
      </div>
    </>
  );
}

/** The short strip on the home page: four lines and a link to the full page. */
export function PanchangStrip({ lang }: { lang: Lang }) {
  const c = content(lang).panchang;
  const { place } = useChosenCity();
  const { data, failed } = usePanchang(place ?? DEFAULT_CITY, "", null);
  if (failed) return null;

  return (
    <div className="rounded-2xl bg-maroon-700 p-5 text-white">
      <div className="flex items-baseline justify-between gap-3">
        <h2 className="font-serif text-xl">{c.stripTitle}</h2>
        <span className="text-sm opacity-80">{place?.label.split(",")[0]}</span>
      </div>
      <dl className="mt-3 grid min-h-28 grid-cols-[auto_1fr] gap-x-4 gap-y-1">
        {data && (
          <>
            <dt className="opacity-80">{c.rows.tithi}</dt>
            <dd>
              {data.paksha[lang]} {data.tithi[lang]}
            </dd>
            <dt className="opacity-80">{c.rows.nakshatra}</dt>
            <dd>{data.nakshatra[lang]}</dd>
            <dt className="opacity-80">{c.rows.rahuKaal}</dt>
            <dd>
              {clock(data.rahu_kaal.start)} – {clock(data.rahu_kaal.end)}
            </dd>
            <dt className="opacity-80">{c.rows.sunrise}</dt>
            <dd>{clock(data.sunrise)}</dd>
          </>
        )}
      </dl>
      <Link href={path(lang, "/panchang")} className="mt-3 inline-block font-semibold text-haldi-300">
        {c.stripMore}
      </Link>
    </div>
  );
}
