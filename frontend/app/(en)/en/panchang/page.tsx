import { PanchangPage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("en", "/panchang", "panchang");

export default function Page() {
  return <PanchangPage lang="en" />;
}
