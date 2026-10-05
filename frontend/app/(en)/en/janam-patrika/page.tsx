import { PatrikaPage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("en", "/janam-patrika", "patrika");

export default function Page() {
  return <PatrikaPage lang="en" />;
}
