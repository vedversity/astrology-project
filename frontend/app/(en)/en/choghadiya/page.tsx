import { ChoghadiyaPage, choghadiyaMetadata } from "@/components/daily";

export const generateMetadata = () => choghadiyaMetadata("en");

export default function Page() {
  return <ChoghadiyaPage lang="en" />;
}
