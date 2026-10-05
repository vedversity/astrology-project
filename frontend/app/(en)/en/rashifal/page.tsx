import { RashifalIndexPage, rashifalIndexMetadata } from "@/components/daily";

export const generateMetadata = () => rashifalIndexMetadata("en");

export default function Page() {
  return <RashifalIndexPage lang="en" />;
}
