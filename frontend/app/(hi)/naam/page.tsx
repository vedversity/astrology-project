import { NaamIndexPage, naamIndexMetadata } from "@/components/guides";

export const generateMetadata = () => naamIndexMetadata("hi");

export default function Page() {
  return <NaamIndexPage lang="hi" />;
}
