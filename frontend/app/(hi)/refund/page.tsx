import { LegalPage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("hi", "/refund", "refund");

export default function Page() {
  return <LegalPage lang="hi" doc="refund" />;
}
