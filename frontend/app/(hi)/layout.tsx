import "../globals.css";

import Shell from "@/components/Shell";
import { mukta, tiro } from "@/lib/fonts";
import { SITE_URL } from "@/lib/site";

export const metadata = { metadataBase: new URL(SITE_URL) };
export const viewport = { themeColor: "#7a1f2b" };

// The Hindi site: every page under /
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="hi" className={`${mukta.variable} ${tiro.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col font-sans text-[17px]">
        <Shell lang="hi">{children}</Shell>
      </body>
    </html>
  );
}
