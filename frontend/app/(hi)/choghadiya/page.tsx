import { ChoghadiyaPage, choghadiyaMetadata } from "@/components/daily";

export const generateMetadata = () => choghadiyaMetadata("hi");

export default function Page() {
  return <ChoghadiyaPage lang="hi" />;
}
