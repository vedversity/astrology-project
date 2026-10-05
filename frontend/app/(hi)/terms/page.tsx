import { LegalPage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("hi", "/terms", "terms");

export default function Page() {
  return <LegalPage lang="hi" doc="terms" />;
}
