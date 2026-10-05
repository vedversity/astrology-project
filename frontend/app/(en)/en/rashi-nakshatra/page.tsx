import { RashiPage, rashiMetadata } from "@/components/guides";

export const generateMetadata = () => rashiMetadata("en");

export default function Page() {
  return <RashiPage lang="en" />;
}
