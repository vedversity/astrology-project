import { LegalPage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("en", "/privacy", "privacy");

export default function Page() {
  return <LegalPage lang="en" doc="privacy" />;
}
