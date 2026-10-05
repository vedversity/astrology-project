"use client";

import { useEffect, useRef, useState } from "react";

import type { Place } from "@/lib/birth";
import { API_URL } from "@/lib/site";

type Props = {
  id: string;
  value: Place | null;
  onChange: (place: Place | null) => void;
  placeholder: string;
  noneText: string;
};

/** Birth-place box: type a few letters, pick a town; the town carries latitude, longitude and timezone. */
export default function PlaceInput({ id, value, onChange, placeholder, noneText }: Props) {
  const [text, setText] = useState(value?.label ?? "");
  const [options, setOptions] = useState<Place[]>([]);
  // True while the text in the box is a town picked from the list (not something half-typed)
  const [chosen, setChosen] = useState(Boolean(value));
  const [open, setOpen] = useState(false);
  const [searched, setSearched] = useState(false);
  const [active, setActive] = useState(0);
  const latest = useRef(0);

  useEffect(() => {
    const query = text.trim();
    if (chosen || query.length < 2) return;
    // Wait until typing pauses, and ignore answers that arrive out of order
    const ticket = ++latest.current;
    const timer = setTimeout(async () => {
      try {
        const response = await fetch(`${API_URL}/places?q=${encodeURIComponent(query)}`);
        const found: Place[] = response.ok ? await response.json() : [];
        if (ticket !== latest.current) return;
        setOptions(found);
        setActive(0);
        setSearched(true);
        setOpen(true);
      } catch {
        if (ticket === latest.current) setOptions([]);
      }
    }, 250);
    return () => clearTimeout(timer);
  }, [text, chosen]);

  function pick(place: Place) {
    setText(place.label);
    setChosen(true);
    setOpen(false);
    onChange(place);
  }

  function onKeyDown(event: React.KeyboardEvent) {
    if (!open || options.length === 0) return;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActive((active + 1) % options.length);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActive((active - 1 + options.length) % options.length);
    } else if (event.key === "Enter") {
      event.preventDefault();
      pick(options[active]);
    } else if (event.key === "Escape") {
      setOpen(false);
    }
  }

  return (
    <div className="relative">
      <input
        id={id}
        className="field"
        value={text}
        placeholder={placeholder}
        autoComplete="off"
        role="combobox"
        aria-expanded={open}
        aria-controls={`${id}-list`}
        aria-autocomplete="list"
        onChange={(event) => {
          setText(event.target.value);
          setSearched(false);
          if (chosen) {
            setChosen(false);
            onChange(null); // typing again clears the earlier choice
          }
        }}
        onKeyDown={onKeyDown}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        onFocus={() => options.length > 0 && !chosen && setOpen(true)}
      />
      {open && (
        <ul
          id={`${id}-list`}
          role="listbox"
          className="absolute z-10 mt-1 max-h-64 w-full overflow-auto rounded-xl border border-gray-300 bg-white shadow-lg"
        >
          {options.map((place, index) => (
            <li
              key={`${place.label}-${place.latitude}`}
              role="option"
              aria-selected={index === active}
              className={`flex min-h-12 cursor-pointer items-center px-4 py-2 ${index === active ? "bg-kesar-50" : ""}`}
              onMouseDown={(event) => {
                event.preventDefault();
                pick(place);
              }}
            >
              {place.label}
            </li>
          ))}
          {options.length === 0 && searched && <li className="px-4 py-3 text-sm text-ink-600">{noneText}</li>}
        </ul>
      )}
    </div>
  );
}
