"use client";

import { useState } from "react";

import { track } from "@/lib/track";

type Props = {
  brand: string;
  heading: string;
  rows: { label: string; value: string }[];
  blessing: string;
  buttonLabel: string;
  shareText: string;
};

const SIZE = 1080;

/** Draws the result as a square picture and shares it (WhatsApp and others), or saves it. */
export default function ShareCard({ brand, heading, rows, blessing, buttonLabel, shareText }: Props) {
  const [busy, setBusy] = useState(false);

  async function make() {
    setBusy(true);
    try {
      await document.fonts.ready;
      // The site's own fonts, so Hindi is drawn exactly as on the page
      const body = getComputedStyle(document.body).fontFamily;
      const serif = getComputedStyle(document.querySelector("h1") ?? document.body).fontFamily;
      const canvas = document.createElement("canvas");
      canvas.width = canvas.height = SIZE;
      const pen = canvas.getContext("2d")!;

      pen.fillStyle = "#fff7ed";
      pen.fillRect(0, 0, SIZE, SIZE);
      pen.strokeStyle = "#c9a24b";
      pen.lineWidth = 8;
      pen.strokeRect(40, 40, SIZE - 80, SIZE - 80);
      pen.lineWidth = 2;
      pen.strokeRect(58, 58, SIZE - 116, SIZE - 116);

      pen.textAlign = "center";
      pen.fillStyle = "#ea7a1a";
      pen.font = `120px ${serif}`;
      pen.fillText("ॐ", SIZE / 2, 230);
      pen.fillStyle = "#7a1f2b";
      pen.font = `64px ${serif}`;
      pen.fillText(heading, SIZE / 2, 350, SIZE - 180);

      let y = 480;
      for (const row of rows) {
        pen.fillStyle = "#57504a";
        pen.font = `38px ${body}`;
        pen.fillText(row.label, SIZE / 2, y);
        pen.fillStyle = "#5e1720";
        pen.font = `76px ${serif}`;
        pen.fillText(row.value, SIZE / 2, y + 84, SIZE - 180);
        y += 170;
      }

      pen.fillStyle = "#7a1f2b";
      pen.font = `40px ${serif}`;
      pen.fillText(blessing, SIZE / 2, SIZE - 150);
      pen.fillStyle = "#c2410c";
      pen.font = `600 34px ${body}`;
      pen.fillText(brand, SIZE / 2, SIZE - 90);

      const blob: Blob = await new Promise((resolve) => canvas.toBlob((b) => resolve(b!), "image/png"));
      const file = new File([blob], "janam-patrika.png", { type: "image/png" });
      track("share_card");
      if (navigator.canShare?.({ files: [file] })) {
        await navigator.share({ files: [file], text: shareText });
      } else {
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = file.name;
        link.click();
        setTimeout(() => URL.revokeObjectURL(link.href), 60000);
      }
    } catch {
      // The visitor closed the share sheet: nothing to do
    } finally {
      setBusy(false);
    }
  }

  return (
    <button type="button" onClick={make} disabled={busy} className="btn-secondary">
      {buttonLabel}
    </button>
  );
}
