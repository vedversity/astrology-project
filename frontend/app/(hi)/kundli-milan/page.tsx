import { MilanPage, milanMetadata } from "@/components/guides";

export const generateMetadata = () => milanMetadata("hi");

export default function Page() {
  return <MilanPage lang="hi" />;
}
