import { RashiPage, rashiMetadata } from "@/components/guides";

export const generateMetadata = () => rashiMetadata("hi");

export default function Page() {
  return <RashiPage lang="hi" />;
}
