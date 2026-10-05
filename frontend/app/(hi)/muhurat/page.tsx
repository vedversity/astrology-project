import { MuhuratIndexPage, muhuratIndexMetadata } from "@/components/muhurat";

export const generateMetadata = () => muhuratIndexMetadata("hi");

export default function Page() {
  return <MuhuratIndexPage lang="hi" />;
}
