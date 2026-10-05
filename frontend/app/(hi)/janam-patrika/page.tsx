import { PatrikaPage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("hi", "/janam-patrika", "patrika");

export default function Page() {
  return <PatrikaPage lang="hi" />;
}
