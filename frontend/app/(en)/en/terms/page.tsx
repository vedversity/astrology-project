import { LegalPage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("en", "/terms", "terms");

export default function Page() {
  return <LegalPage lang="en" doc="terms" />;
}
