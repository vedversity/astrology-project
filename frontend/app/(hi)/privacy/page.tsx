import { LegalPage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("hi", "/privacy", "privacy");

export default function Page() {
  return <LegalPage lang="hi" doc="privacy" />;
}
