import { RashifalIndexPage, rashifalIndexMetadata } from "@/components/daily";

export const generateMetadata = () => rashifalIndexMetadata("hi");

export default function Page() {
  return <RashifalIndexPage lang="hi" />;
}
