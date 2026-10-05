"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import PlaceInput from "@/components/PlaceInput";
import { removeProfile, saveBirth, useBirth, useProfiles, type Birth, type Place } from "@/lib/birth";
import { content, fill } from "@/lib/content";
import { path, type Lang } from "@/lib/site";

/** The two-step birth form. Step 1: name, gender, date. Step 2: time and place. */
export default function KundliForm({ lang }: { lang: Lang }) {
  // A returning family finds their last entry already filled in
  const last = useBirth(true);
  const profiles = useProfiles();
  // A saved family member chosen from the list, or "new" for an empty form
  const [picked, setPicked] = useState<Birth | "new" | null>(null);
  const shown = picked === "new" ? null : (picked ?? last ?? null);
  return (
    <Fields
      key={picked === "new" ? "new" : shown ? `${shown.name}|${shown.date}|${shown.gender}` : "empty"}
      lang={lang}
      last={shown}
      profiles={profiles}
      onPick={setPicked}
    />
  );
}

type FieldsProps = { lang: Lang; last: Birth | null; profiles: Birth[]; onPick: (pick: Birth | "new") => void };

function Fields({ lang, last, profiles, onPick }: FieldsProps) {
  const c = content(lang).form;
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [name, setName] = useState(last?.name ?? "");
  const [gender, setGender] = useState<Birth["gender"] | "">(last?.gender ?? "");
  const [date, setDate] = useState(last?.date ?? "");
  const [time, setTime] = useState(last?.time ?? "");
  const [timeKnown, setTimeKnown] = useState(last?.timeKnown ?? true);
  const [place, setPlace] = useState<Place | null>(last?.place ?? null);
  const [error, setError] = useState("");
  const today = new Date().toISOString().slice(0, 10);

  function toStepTwo() {
    if (!gender) return setError(c.errors.gender);
    if (!date || date > today || date < "1900-01-01") return setError(c.errors.date);
    setError("");
    setStep(2);
  }

  function submit(event: React.FormEvent) {
    event.preventDefault();
    if (step === 1) return toStepTwo();
    if (timeKnown && !time) return setError(c.errors.time);
    if (!place) return setError(c.errors.place);
    setError("");
    saveBirth({ name: name.trim(), gender: gender as Birth["gender"], date, time, timeKnown, place });
    router.push(path(lang, "/preview"));
  }

  const genders: { value: Birth["gender"]; label: string }[] = [
    { value: "female", label: c.female },
    { value: "male", label: c.male },
  ];

  return (
    <form id="kundli" onSubmit={submit} noValidate className="card scroll-mt-28">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">{c.title}</h2>
        <span className="text-sm text-ink-600">{fill(c.step, { n: step })}</span>
      </div>

      {step === 1 && profiles.length > 1 && (
        <div className="mb-4 rounded-xl bg-kesar-50 p-3">
          <p className="text-sm font-semibold">{c.saved}</p>
          <ul className="mt-2 flex flex-wrap gap-2">
            {profiles.map((profile) => (
              <li key={`${profile.name}|${profile.date}|${profile.gender}`} className="flex items-center rounded-full border border-kesar-100 bg-white">
                <button type="button" className="h-10 pl-4 pr-2" onClick={() => onPick(profile)}>
                  {profile.name || profile.date}
                </button>
                <button
                  type="button"
                  className="h-10 pl-1 pr-3 text-ink-600"
                  aria-label={fill(c.savedRemove, { name: profile.name || profile.date })}
                  onClick={() => removeProfile(profile)}
                >
                  ×
                </button>
              </li>
            ))}
            <li>
              <button type="button" className="h-10 rounded-full border border-kesar-600 px-4 text-kesar-700" onClick={() => onPick("new")}>
                {c.savedNew}
              </button>
            </li>
          </ul>
          <p className="mt-2 text-xs text-ink-600">{c.savedNote}</p>
        </div>
      )}

      {step === 1 && (
        <div>
          <label className="label" htmlFor="name">
            {c.name}
          </label>
          <input
            id="name"
            className="field"
            value={name}
            maxLength={80}
            autoComplete="off"
            placeholder={c.namePlaceholder}
            onChange={(event) => setName(event.target.value)}
          />
          <p className="mt-1 text-xs text-ink-600">{c.nameHint}</p>

          <fieldset className="mt-4">
            <legend className="label">{c.gender}</legend>
            <div className="mt-1 grid grid-cols-2 gap-2">
              {genders.map((option) => (
                <label
                  key={option.value}
                  className={`flex h-12 cursor-pointer items-center justify-center rounded-xl border px-2 text-center ${
                    gender === option.value ? "border-kesar-600 bg-kesar-50 font-semibold" : "border-gray-300"
                  }`}
                >
                  <input
                    type="radio"
                    name="gender"
                    value={option.value}
                    checked={gender === option.value}
                    onChange={() => setGender(option.value)}
                    className="sr-only"
                  />
                  {option.label}
                </label>
              ))}
            </div>
          </fieldset>

          <label className="label mt-4" htmlFor="date">
            {c.date}
          </label>
          <input
            id="date"
            type="date"
            className="field"
            value={date}
            min="1900-01-01"
            max={today}
            onChange={(event) => setDate(event.target.value)}
          />
        </div>
      )}

      {step === 2 && (
        <div>
          <label className="label" htmlFor="time">
            {c.time}
          </label>
          <input
            id="time"
            type="time"
            className="field disabled:bg-gray-100"
            value={time}
            disabled={!timeKnown}
            onChange={(event) => setTime(event.target.value)}
          />
          <label className="mt-2 flex min-h-8 items-center gap-2 text-sm text-ink-600">
            <input
              type="checkbox"
              className="size-5 accent-kesar-600"
              checked={!timeKnown}
              onChange={(event) => setTimeKnown(!event.target.checked)}
            />
            {c.timeUnknown}
          </label>
          {!timeKnown && <p className="mt-1 text-xs text-ink-600">{c.timeUnknownNote}</p>}

          <label className="label mt-4" htmlFor="place">
            {c.place}
          </label>
          <PlaceInput
            id="place"
            value={place}
            onChange={setPlace}
            placeholder={c.placePlaceholder}
            noneText={c.placeNone}
          />
          <p className="mt-1 text-xs text-ink-600">{c.placeHint}</p>
        </div>
      )}

      {error && (
        <p role="alert" className="mt-3 text-sm font-semibold text-red-700">
          {error}
        </p>
      )}

      <button type="submit" className="btn-primary mt-5">
        {step === 1 ? c.next : c.submit}
      </button>
      {step === 2 && (
        <button
          type="button"
          className="mt-2 h-10 w-full text-sm text-ink-600"
          onClick={() => {
            setError("");
            setStep(1);
          }}
        >
          {c.back}
        </button>
      )}
      <p className="mt-3 text-center text-xs text-ink-600">{c.privacy}</p>
    </form>
  );
}
