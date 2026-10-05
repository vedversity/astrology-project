import { LegalPage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("en", "/refund", "refund");

export default function Page() {
  return <LegalPage lang="en" doc="refund" />;
}
