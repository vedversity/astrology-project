import { GrahIndexPage, grahIndexMetadata } from "@/components/guides";

export const generateMetadata = () => grahIndexMetadata("en");

export default function Page() {
  return <GrahIndexPage lang="en" />;
}
