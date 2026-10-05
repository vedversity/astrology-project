import Admin from "@/components/Admin";

// The owner's settings page: not linked anywhere and kept out of search engines
export const metadata = { title: "Site settings", robots: { index: false, follow: false } };

export default function Page() {
  return <Admin />;
}
