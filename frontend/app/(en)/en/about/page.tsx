import { AboutPage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("en", "/about", "about");

export default function Page() {
  return <AboutPage lang="en" />;
}
