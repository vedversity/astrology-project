import { LegalPage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("hi", "/disclaimer", "disclaimer");

export default function Page() {
  return <LegalPage lang="hi" doc="disclaimer" />;
}
