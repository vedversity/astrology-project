import { Suspense } from "react";

import Thanks from "@/components/Thanks";

// A customer's own order page: kept out of search engines
export const metadata = { robots: { index: false, follow: false }, referrer: "no-referrer" as const };

export default function Page() {
  return (
    <Suspense>
      <Thanks lang="hi" />
    </Suspense>
  );
}
