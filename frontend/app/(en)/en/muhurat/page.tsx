import { MuhuratIndexPage, muhuratIndexMetadata } from "@/components/muhurat";

export const generateMetadata = () => muhuratIndexMetadata("en");

export default function Page() {
  return <MuhuratIndexPage lang="en" />;
}
