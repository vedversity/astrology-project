import { LegalPage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("en", "/disclaimer", "disclaimer");

export default function Page() {
  return <LegalPage lang="en" doc="disclaimer" />;
}
