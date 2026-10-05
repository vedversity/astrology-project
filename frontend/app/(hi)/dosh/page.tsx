import { DoshIndexPage, doshIndexMetadata } from "@/components/guides";

export const generateMetadata = () => doshIndexMetadata("hi");

export default function Page() {
  return <DoshIndexPage lang="hi" />;
}
