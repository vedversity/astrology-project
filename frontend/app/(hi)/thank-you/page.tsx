import Thanks from "@/components/Thanks";

// A visitor's own result: kept out of search engines
export const metadata = { robots: { index: false, follow: false } };

export default function Page() {
  return (
    <Thanks lang="hi" />
  );
}
