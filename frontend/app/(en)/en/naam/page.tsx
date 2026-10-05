import { NaamIndexPage, naamIndexMetadata } from "@/components/guides";

export const generateMetadata = () => naamIndexMetadata("en");

export default function Page() {
  return <NaamIndexPage lang="en" />;
}
