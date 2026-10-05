"use client";

// The birth details typed into the form, kept in the visitor's own browser.
//
// sessionStorage: carries the details from the form to the preview and order pages.
// localStorage:   remembers the last entry so a returning family need not retype it.
// Nothing here is sent anywhere except to our own API when a chart is requested.

import { useMemo, useSyncExternalStore } from "react";

export type Place = { label: string; latitude: number; longitude: number; timezone: string };

export type Birth = {
  name: string;
  gender: "male" | "female";
  date: string; // YYYY-MM-DD
  time: string; // HH:MM, empty when not known
  timeKnown: boolean;
  place: Place;
};

const KEY = "birth";
const noChange = () => () => {};

export function saveBirth(birth: Birth) {
  const json = JSON.stringify(birth);
  sessionStorage.setItem(KEY, json);
  localStorage.setItem(KEY, json);
}

/**
 * The saved birth details, for use inside a component.
 * undefined = not known yet (the page is still loading); null = nothing saved.
 */
export function useBirth(remembered = false): Birth | null | undefined {
  const json = useSyncExternalStore(
    noChange,
    () => (remembered ? localStorage : sessionStorage).getItem(KEY),
    () => undefined,
  );
  return useMemo(() => {
    if (json === undefined) return undefined;
    try {
      return json ? (JSON.parse(json) as Birth) : null;
    } catch {
      return null;
    }
  }, [json]);
}

/** The birth details in the shape the API expects. */
export function apiBody(birth: Birth) {
  return {
    date: birth.date,
    time: birth.timeKnown && birth.time ? birth.time : null,
    time_known: birth.timeKnown && Boolean(birth.time),
    latitude: birth.place.latitude,
    longitude: birth.place.longitude,
    timezone: birth.place.timezone,
  };
}

// The finished PDF is held in memory between the order page and the download page.
let pdf: { url: string; filename: string } | null = null;

export function keepPdf(blob: Blob, filename: string) {
  if (pdf) URL.revokeObjectURL(pdf.url);
  pdf = { url: URL.createObjectURL(blob), filename };
}

/** The finished PDF, for use inside a component. undefined = the page is still loading. */
export function usePdf() {
  return useSyncExternalStore(
    noChange,
    () => pdf,
    () => undefined,
  );
}

/** Remove everything this site has remembered on this device. */
export function forgetEverything() {
  sessionStorage.removeItem(KEY);
  localStorage.removeItem(KEY);
  localStorage.removeItem(CITY_KEY);
}

// The city chosen on the Panchang page, remembered for the next visit
const CITY_KEY = "city";

export function saveCity(place: Place) {
  localStorage.setItem(CITY_KEY, JSON.stringify(place));
}

/** The remembered city. undefined = the page is still loading; null = none chosen yet. */
export function useCity(): Place | null | undefined {
  const json = useSyncExternalStore(
    noChange,
    () => localStorage.getItem(CITY_KEY),
    () => undefined,
  );
  return useMemo(() => {
    if (json === undefined) return undefined;
    try {
      return json ? (JSON.parse(json) as Place) : null;
    } catch {
      return null;
    }
  }, [json]);
}
