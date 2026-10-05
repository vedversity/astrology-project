import { MilanPage, milanMetadata } from "@/components/guides";

export const generateMetadata = () => milanMetadata("en");

export default function Page() {
  return <MilanPage lang="en" />;
}
