import { AboutPage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("hi", "/about", "about");

export default function Page() {
  return <AboutPage lang="hi" />;
}
