import { DoshIndexPage, doshIndexMetadata } from "@/components/guides";

export const generateMetadata = () => doshIndexMetadata("en");

export default function Page() {
  return <DoshIndexPage lang="en" />;
}
