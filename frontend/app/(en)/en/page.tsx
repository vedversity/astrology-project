import { HomePage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("en", "/", "home");

export default function Page() {
  return <HomePage lang="en" />;
}
