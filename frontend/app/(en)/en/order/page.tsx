import { Suspense } from "react";

import Order from "@/components/Order";

// A visitor's own result: kept out of search engines
export const metadata = { robots: { index: false, follow: false } };

export default function Page() {
  return (
    <Suspense>
      <Order lang="en" />
    </Suspense>
  );
}
