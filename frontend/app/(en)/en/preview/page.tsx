import Preview from "@/components/Preview";

// A visitor's own result: kept out of search engines
export const metadata = { robots: { index: false, follow: false } };

export default function Page() {
  return (
    <Preview lang="en" />
  );
}
