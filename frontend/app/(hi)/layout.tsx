import "../globals.css";

import Script from "next/script";

import Shell from "@/components/Shell";
import { mukta, tiro } from "@/lib/fonts";
import { SITE_URL } from "@/lib/site";
import { GA_ID } from "@/lib/track";

export const metadata = { metadataBase: new URL(SITE_URL) };
export const viewport = { themeColor: "#7a1f2b" };

// The Hindi site: every page under /
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="hi" className={`${mukta.variable} ${tiro.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col font-sans text-[17px]">
        <Shell lang="hi">{children}</Shell>
        {GA_ID && (
          <>
            <Script src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`} strategy="afterInteractive" />
            <Script id="ga" strategy="afterInteractive">
              {`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${GA_ID}',{anonymize_ip:true});`}
            </Script>
          </>
        )}
      </body>
    </html>
  );
}
