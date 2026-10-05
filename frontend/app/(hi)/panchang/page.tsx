import { PanchangPage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("hi", "/panchang", "panchang");

export default function Page() {
  return <PanchangPage lang="hi" />;
}
