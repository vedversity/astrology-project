import { GrahIndexPage, grahIndexMetadata } from "@/components/guides";

export const generateMetadata = () => grahIndexMetadata("hi");

export default function Page() {
  return <GrahIndexPage lang="hi" />;
}
